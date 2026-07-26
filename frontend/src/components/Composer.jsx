import { useEffect, useRef } from "react";

import { SendIcon } from "./Icons";

export default function Composer({ value, onChange, onSubmit, busy }) {
  const textareaRef = useRef(null);

  // Grow with the content instead of scrolling a one-line box.
  //
  // Two traps here, both of which produced a composer stuck at max-height:
  //  - measuring while height is "auto" lets the textarea stretch to fill the
  //    flex row, so scrollHeight reports the row, not the text. Collapse to 0
  //    first.
  //  - measuring during the mount commit happens before the stylesheet and
  //    webfonts apply, which gives a bogus reading. Defer past layout, and
  //    while the field is empty let the CSS min-height own the resting size.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;

    const fit = () => {
      if (!value) {
        el.style.height = "";
        return;
      }
      el.style.height = "0px";
      el.style.height = `${el.scrollHeight}px`;
    };

    const frame = requestAnimationFrame(fit);
    return () => cancelAnimationFrame(frame);
  }, [value]);

  const canSend = value.trim().length > 0 && !busy;

  const handleKeyDown = (event) => {
    // Enter sends, Shift+Enter makes a new line.
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (canSend) onSubmit();
    }
  };

  return (
    <div className="composer-wrap">
      <div className="composer">
        <span className="composer__prefix" aria-hidden="true">
          Q.
        </span>

        <label htmlFor="enquiry" className="visually-hidden">
          Your health question
        </label>
        <textarea
          id="enquiry"
          ref={textareaRef}
          className="composer__input"
          rows={1}
          placeholder="Ask about nutrition, sleep, fitness, symptoms…"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />

        <button
          className="composer__send"
          onClick={onSubmit}
          disabled={!canSend}
          aria-label={busy ? "Searching the library" : "Send question"}
        >
          <SendIcon size={14} aria-hidden="true" />
          {busy ? "Searching…" : "Ask"}
        </button>
      </div>

      <div className="composer__foot">
        <span>
          Answers are limited to the curated library. Not medical advice.
        </span>
        <span className="composer__hint">
          <kbd>Enter</kbd> to send · <kbd>Shift</kbd>+<kbd>Enter</kbd> for a new
          line
        </span>
      </div>
    </div>
  );
}
