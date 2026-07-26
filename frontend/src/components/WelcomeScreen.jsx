import { CATEGORIES, SUGGESTIONS, SOURCE_COUNT, PUBLISHERS } from "../constants";
import { AlertIcon } from "./Icons";

export default function WelcomeScreen({ recent, onAsk }) {
  // Recent enquiries take the place of the stock prompts once they exist.
  const prompts = [
    ...recent.slice(0, 2).map((chat) => ({
      question: chat.title,
      category: "Asked earlier",
    })),
    ...SUGGESTIONS,
  ].slice(0, 4);

  return (
    <div>
      <header className="masthead">
        <div className="masthead__rule">
          <span className="eyebrow">Health reference assistant</span>
        </div>
        <h1>
          Ask a health question.
          <br />
          Get an answer with its <em>sources</em>.
        </h1>
        <p className="masthead__standfirst">
          Every answer is drawn from a curated library of public-health fact
          sheets — and nothing else. If the library cannot support an answer, it
          says so rather than guessing.
        </p>
      </header>

      <section className="section">
        <div className="section__head">
          <h2 className="eyebrow">Start here</h2>
          <span className="count">{String(prompts.length).padStart(2, "0")}</span>
        </div>
        <div className="prompt-grid">
          {prompts.map((prompt, index) => (
            <button
              key={prompt.question}
              className="prompt"
              onClick={() => onAsk(prompt.question)}
            >
              <span className="prompt__index" aria-hidden="true">
                {String(index + 1).padStart(2, "0")}
              </span>
              <span className="prompt__body">
                <span className="prompt__q">{prompt.question}</span>
                <span className="prompt__cat">{prompt.category}</span>
              </span>
            </button>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section__head">
          <h2 className="eyebrow">Topic index</h2>
          <span className="count">{CATEGORIES.length}</span>
        </div>
        <div className="topics">
          {CATEGORIES.map((category) => (
            <button
              key={category}
              className="topic"
              onClick={() => onAsk(`What should I know about ${category.toLowerCase()}?`)}
            >
              {category}
            </button>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="provenance">
          <span className="provenance__figure" aria-hidden="true">
            {SOURCE_COUNT}
          </span>
          <p>
            <strong>articles in the library.</strong> Curated from{" "}
            {PUBLISHERS.join(", ")} and others. Answers cite the specific
            articles they draw on, so you can read the original.
          </p>
        </div>
      </section>

      <div className="notice">
        <AlertIcon size={15} className="notice__icon" aria-hidden="true" />
        <div>
          <strong>Educational information only.</strong> This assistant does not
          diagnose conditions or advise on medication. For anything urgent,
          contact emergency services or a licensed healthcare professional.
        </div>
      </div>
    </div>
  );
}
