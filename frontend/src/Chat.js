import React, { useState, useRef, useEffect } from "react";
import "./Chat.css";

function Chat({ onBack }) {
  //store all chat messages shown in the interface
  const [messages, setMessages] = useState([
    {
      sender: "universe",
      text: "Hi!!"
    }
  ]);
  //store current user input 
  const [input, setInput] = useState("");
  //store loading state to show "..." when waiting for response
  const [loading, setLoading] = useState(false);
  //auto scroll to the bottom of the chat when new messages are added or loading state changes
  const bottomRef = useRef(null);

  //scroll to the latest message 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading]);

  //send user message to backend and get response 
  const sendMessage = async () => {
    //no empty messages allowed
    if (!input.trim()) return;
    const userMessage = { sender: "user", text: input };
    setMessages([...messages, userMessage]);
    const currentInput = input;
    setInput("");
    setLoading(true);
    try {
      //send message to FAST API 
      const response = await fetch("http://localhost:8000/predict", {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: currentInput })
      });
      const data = await response.json();

      //simulate typing delay based on response length
      const delay = Math.min(500 + data.response.length * 20, 4000);
      await new Promise(res => setTimeout(res, delay));

      const universeMessage = { 
        sender: "universe", 
        text: data.response,
        intent: data.intent 
      };
      setMessages(prev => [...prev, universeMessage]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = {
        sender: "universe",
        text: "something went wrong."
      };
      setMessages(prev => [...prev, errorMessage]);
    }
    setLoading(false);
  };

  // send message with enter ket
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <h2>Universe</h2>
      </div>
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.sender}`}>
            <div className="message-bubble">
              <p>{msg.text}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message universe">
            <div className="message-bubble">
              <p>...</p>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>
      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Text..."
        />
        <button onClick={sendMessage} disabled={!input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;