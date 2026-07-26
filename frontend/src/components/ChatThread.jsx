import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

import { HeartIcon, AlertIcon, ArrowIcon } from "./Icons";

/*
  The numbered reference list is this product's whole claim made visible: the
  answer is grounded in these specific articles.

  Deliberately NOT injecting [1]/[2] markers into the answer prose — the model
  does not emit them, so any inline marker would point at a source the sentence
  may not actually rest on. In a health context that would be a fabricated
  citation. The list is numbered; the prose is left as written.
*/
function Evidence({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="evidence">
      <div className="evidence__head">
        <h3 className="eyebrow">
          References ({sources.length})
        </h3>
      </div>
      <div className="evidence__list">
        {sources.map((source, index) => {
          const Tag = source.url ? "a" : "div";
          const linkProps = source.url
            ? { href: source.url, target: "_blank", rel: "noreferrer noopener" }
            : {};

          return (
            <Tag
              key={`${source.url || source.title}-${index}`}
              className="reference"
              {...linkProps}
            >
              <span className="reference__num" aria-hidden="true">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span>
                <span className="reference__title">{source.title}</span>
                <span className="reference__meta">
                  <span className="reference__publisher">{source.source}</span>
                  {source.category && <span>{source.category}</span>}
                  {source.url && (
                    <span className="visually-hidden">opens in a new tab</span>
                  )}
                </span>
              </span>
              {source.url && (
                <ArrowIcon size={14} className="reference__go" aria-hidden="true" />
              )}
            </Tag>
          );
        })}
      </div>
    </div>
  );
}

function Answer({ message }) {
  const count = message.sources?.length || 0;

  return (
    <div className="answer">
      <div className="rail" aria-hidden="true">
        <span className="rail__mark">
          <HeartIcon size={13} />
        </span>
        {count > 0 && <span className="rail__count">{count}</span>}
        <span className="rail__line" />
      </div>

      <div>
        {message.error ? (
          <div className="error" role="alert">
            <AlertIcon size={15} className="error__icon" aria-hidden="true" />
            <span>{message.error}</span>
          </div>
        ) : message.content ? (
          <>
            <div className="prose">
              <ReactMarkdown>{message.content}</ReactMarkdown>
              {message.pending && <span className="caret" aria-hidden="true" />}
            </div>
            <Evidence sources={message.sources} />
          </>
        ) : (
          <p className="working">
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            <span aria-hidden="true" />
            Searching the library…
          </p>
        )}
      </div>
    </div>
  );
}

export default function ChatThread({ messages }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  return (
    <div className="thread">
      {messages.map((msg, index) =>
        msg.role === "user" ? (
          <div className="question" key={index}>
            <span className="eyebrow">Enquiry</span>
            <h2>{msg.content}</h2>
          </div>
        ) : (
          /* Streamed text is announced once settled, not on every chunk. */
          <div
            key={index}
            aria-live="polite"
            aria-busy={msg.pending ? "true" : "false"}
          >
            <Answer message={msg} />
          </div>
        ),
      )}
      <div ref={endRef} />
    </div>
  );
}
