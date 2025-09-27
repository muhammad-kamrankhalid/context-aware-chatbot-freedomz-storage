# Context-Aware Chatbot for Freedomz Storage Website

## Overview
This project is a **context-aware chatbot** built specifically for the **Freedomz Storage** company website.  
Unlike general-purpose chatbots, this system retrieves and processes company-specific content to deliver accurate, context-driven answers to user queries.

The chatbot is designed using:
- **LangChain**
- **WebBaseLoader**
- **HuggingFace Embeddings**
- **ChromaDB**
- **FastAPI**
- **React.js**
- **HuggingFace Spaces**
- **WordPress Integration**

**Core Purpose:** Deliver reliable chatbot responses by strictly referencing the Freedomz Storage website content.

---

## Features
- **Website Context Retrieval**: Loads content from multiple Freedomz Storage web pages.
- **Semantic Search**: Uses embeddings and ChromaDB for precise context matching.
- **Retrieval-Augmented Generation**: Ensures context-bound, concise answers.
- **WordPress Integration**: Embedded chatbot interface for easy access.
- **React.js Frontend**: Clean and interactive user experience.

---

## Architecture
The system flow:
1. User sends a query via frontend (React.js).
2. FastAPI backend receives the query.
3. LangChain retrieves relevant context from ChromaDB.
4. The language model generates the answer.
5. The frontend displays the chatbot’s response.

---

## Usage
To run this project locally:
1. Clone the repository.
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
## Consent & Permissions
This project was developed for **Freedomz Storage**.  
**All code and documentation here are shared publicly with explicit written permission from Freedomz Storage.**  
Sensitive company information, API keys, and private data have been removed before publishing.  

If you are interested in deploying this chatbot for another project, please refer to the code and configuration instructions in this repository, while ensuring your own website’s permissions and privacy requirements.
