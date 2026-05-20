import { useState } from "react";

function App() {

  const [message, setMessage] = useState("");

  const [reply, setReply] = useState("");

  const [sources, setSources] = useState([]);


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

      setSources(data.sources || []);

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


      <div style={{ marginTop: "30px" }}>

        <h3>Sources</h3>

        {
          sources.map((source, index) => (

            <div
              key={index}
              style={{
                border: "1px solid gray",
                padding: "10px",
                marginBottom: "10px",
                borderRadius: "8px"
              }}
            >

              <p>
                <strong>Title:</strong> {source.title}
              </p>

              <p>
                <strong>Source:</strong> {source.source}
              </p>

              <p>
                <strong>Category:</strong> {source.category}
              </p>

            </div>

          ))
        }

      </div>

    </div>

  );
}

export default App;