import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

// simple session id generator (keeps same id in localStorage per browser)
function getSessionId() {
  const key = "freedomz_session_id";
  let sid = localStorage.getItem(key);
  if (!sid) {
    sid = `sess-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;
    localStorage.setItem(key, sid);
  }
  return sid;
}

export default function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const sessionId = useRef(getSessionId());
  const chatBoxRef = useRef();

  useEffect(() => {
    // scroll to bottom when messages update
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const sendQuestion = async () => {
    if (!question.trim()) return;
    const userMsg = { sender: "user", text: question };
    setMessages((m) => [...m, userMsg]);
    setLoading(true);

    try {
      const res = await axios.post("https://kamran5901-chatbot.hf.space/ask", {
        question: question,
        session_id: sessionId.current, // optional on backend but useful for history
      }, { timeout: 120000 });

      // Expecting backend: { "answer": "..." }
      const botText = res.data?.answer ?? "No answer returned.";
      setMessages((m) => [...m, { sender: "bot", text: botText }]);
    } catch (err) {
      console.error("API error:", err);
      setMessages((m) => [...m, { sender: "bot", text: "Error connecting to server." }]);
    } finally {
      setLoading(false);
      setQuestion("");
    }
  };

  // send on Enter
  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendQuestion();
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Freedomz Chatbot</h2>


      <div style={styles.chatBox} ref={chatBoxRef}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor: m.sender === "user" ? "#0078d7" : "#e6e6e6",
              color: m.sender === "user" ? "white" : "black",
            }}
          >
            {m.text}
          </div>
        ))}

        {loading && <div style={styles.loading}>Thinking…</div>}
      </div>

      <div style={styles.inputRow}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKey}
          placeholder=""
          style={styles.textarea}
          rows={2}
        />
        <button onClick={sendQuestion} style={styles.button} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { 
    maxWidth: 720, 
    margin: "10px auto", 
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#fff", // dark background outside the chatbox
    padding: 10,
    borderRadius: 5,
    minHeight: "90vh", // cover full height
  },
  title: {
    color: "#198754", // 👈 text color for h2
    textAlign: "center",
    marginBottom: 16,
  },
  chatBox: {
    border: "3px solid #20c997",
    borderRadius: 8,
    padding: 5,
    minHeight: 400,
    display: "flex",
    flexDirection: "column",
    gap: 8,
    overflowY: "auto",
    marginBottom: 8,
    backgroundColor: "#ffffff", // keep chatbox white
  },
  message: { padding: "8px 12px", borderRadius: 12, maxWidth: "75%" },
  loading: { fontStyle: "italic", color: "#777" },
  inputRow: { display: "flex", gap: 8 },
  textarea: { flex: 1, padding: 10, borderRadius: 6, border: "2px solid #20c997" },
  button: { padding: "10px 14px", borderRadius: 6, border: "none", background: "#20c997", color: "white", cursor: "pointer" },
};
