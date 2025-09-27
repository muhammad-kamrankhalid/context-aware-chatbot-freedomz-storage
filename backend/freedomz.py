import os

# Use /app/.cache (writable in Spaces)
cache_dir = "/app/.cache/huggingface"
os.environ["HF_HOME"] = cache_dir
os.environ["TRANSFORMERS_CACHE"] = f"{cache_dir}/transformers"
os.environ["SENTENCE_TRANSFORMERS_HOME"] = f"{cache_dir}/sentence-transformers"

os.makedirs(cache_dir, exist_ok=True)




import bs4
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# LangChain imports
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# ----------------- Load environment variables -----------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
hf_token = os.getenv("HF_TOKEN")

# ----------------- Initialize LLM -----------------
llm = ChatGroq(api_key=groq_api_key, model="llama-3.1-8b-instant")

# ----------------- Embeddings -----------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ----------------- Load Multiple Website Pages -----------------
urls = [
    "https://freedomzstorage.com/",
    "https://freedomzstorage.com/blogs/",
    "https://freedomzstorage.com/faqs/",
    "https://freedomzstorage.com/contact/",
    "https://freedomzstorage.com/nassau/",
    "https://freedomzstorage.com/nassau/east-rockaway/",
    "https://freedomzstorage.com/nassau/freeport-ny/",
    "https://freedomzstorage.com/nassau/massapequa/",
    "https://freedomzstorage.com/nassau/glen-cove/",
    "https://freedomzstorage.com/nassau/new-hyde-park/",
    "https://freedomzstorage.com/nassau/lawrence-ny/",
    "https://freedomzstorage.com/business-storage-in-long-island/",
    "https://freedomzstorage.com/personal-self-storage-long-island/",
    "https://freedomzstorage.com/caravan-storage-long-island/"
]

# Always fetch docs and build in-memory vectorstore (no persist_directory)
loader = WebBaseLoader(urls)

docs = loader.load()

print("Loaded docs:", len(docs))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=250)
splits = text_splitter.split_documents(docs)

vectordb = Chroma.from_documents(
    documents=splits,
    embedding=embeddings
)

retriever = vectordb.as_retriever(
    search_kwargs={"k": 8}
)


# ----------------- Prompt Templates ----------------

system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use three sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
)

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)



contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}")
    ]
)

qa_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

# ----------------- Chat History Store -----------------
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# ----------------- FastAPI App -----------------
app = FastAPI()

# Enable CORS so React/WordPress can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev, you can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    session_id: str | None = "default_session"   # ✅ optional with default value

@app.post("/ask")
def ask_question(query: QueryRequest):
    session_id = query.session_id or "default_session"  # ✅ fallback
    response = conversational_rag_chain.invoke(
        {"input": query.question},
        config={"configurable": {"session_id": session_id}}
    )
    return {"answer": response["answer"]}

