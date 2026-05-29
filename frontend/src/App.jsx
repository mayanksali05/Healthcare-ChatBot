import { useState } from "react";
import ReactMarkdown from "react-markdown";

function App() {

  const [message, setMessage] = useState("");

  const [reply, setReply] = useState("");

  const [sources, setSources] = useState([]);


  const sendMessage = async () => {

  setReply("");
  setSources([]);

  const response = await fetch(
    "http://127.0.0.1:5000/chat",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: message,
      }),
    }
  );
  

const sourceHeader = response.headers.get("X-Sources");

if (sourceHeader) {

  try {

    const parsedSources = JSON.parse(sourceHeader);

    setSources(parsedSources);

  } catch (error) {

    console.error(error);

  }
}

console.log(response.headers);
console.log(response.headers.get("X-Sources"));
  const reader = response.body.getReader();

  const decoder = new TextDecoder();

  let done = false;

  let accumulatedResponse = "";

  while (!done) {

    const result = await reader.read();

    done = result.done;

    const chunk = decoder.decode(result.value || new Uint8Array());

    accumulatedResponse += chunk;

    setReply(accumulatedResponse);
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

        <div
          style={{
            textAlign: "left",
            maxWidth: "900px",
            margin: "0 auto",
            lineHeight: "1.8"
        }}
      >
        <ReactMarkdown
          components={{

            h2: ({node, ...props}) => (
              <h2
                style={{
                  marginTop: "25px",
                  marginBottom: "10px",
                  color: "#ffffff"
                }}
                {...props}
              />
            ),

            li: ({node, ...props}) => (
              <li
                style={{
                  marginBottom: "10px"
                }}
                {...props}
              />
            ),

            p: ({node, ...props}) => (
              <p
                style={{
                  marginBottom: "15px"
                }}
                {...props}
              />
            )

          }}
        >
          {reply}
        </ReactMarkdown>
      </div>

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