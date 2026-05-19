import { useState } from "react";

function App() {
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");

  const sendMessage = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
        }),
      });

      const data = await response.json();

      console.log(data);

      setReply(data.reply || data.error);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div style={{ padding: "40px" }}>
      <h1>Healthcare ChatBot</h1>

      <input
        type="text"
        placeholder="Ask health question..."
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        style={{
          width: "300px",
          padding: "10px",
          marginRight: "10px",
        }}
      />

      <button onClick={sendMessage}>
        Send
      </button>

      <div style={{ marginTop: "20px" }}>
        <strong>Bot Reply:</strong>
        <p>{reply}</p>
      </div>
    </div>
  );
}

export default App;