import { useCallback, useEffect, useRef, useState } from "react";

import "./App.css";
import { API_BASE } from "./constants";
import Sidebar from "./components/Sidebar";
import WelcomeScreen from "./components/WelcomeScreen";
import ChatThread from "./components/ChatThread";
import Composer from "./components/Composer";
import { MenuIcon } from "./components/Icons";

function titleFor(question) {
  const clean = question.trim().replace(/\s+/g, " ");
  return clean.length > 42 ? `${clean.slice(0, 42)}…` : clean;
}

// Matches the CSS breakpoint where the sidebar becomes an overlay.
const MOBILE_BREAKPOINT = 860;

const isMobileWidth = () =>
  typeof window !== "undefined" && window.innerWidth < MOBILE_BREAKPOINT;

export default function App() {
  // On narrow screens the sidebar overlays the content, so it starts closed.
  const [collapsed, setCollapsed] = useState(isMobileWidth);
  const [activeNav, setActiveNav] = useState("home");

  const [chats, setChats] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);

  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  const [health, setHealth] = useState({
    loading: true,
    apiConnected: false,
    dbConnected: false,
  });

  const abortRef = useRef(null);
  const wasMobileRef = useRef(isMobileWidth());

  // Only react when the viewport crosses the breakpoint, so a deliberate
  // collapse/expand is not undone by unrelated resizes.
  useEffect(() => {
    const onResize = () => {
      const mobile = isMobileWidth();
      if (mobile !== wasMobileRef.current) {
        wasMobileRef.current = mobile;
        setCollapsed(mobile);
      }
    };

    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  // Poll the backend so the sidebar reflects real API + Mongo state.
  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        const response = await fetch(`${API_BASE}/health/db`);
        const data = await response.json();
        if (!cancelled) {
          setHealth({
            loading: false,
            apiConnected: true,
            dbConnected: Boolean(data.connected),
          });
        }
      } catch {
        if (!cancelled) {
          setHealth({ loading: false, apiConnected: false, dbConnected: false });
        }
      }
    };

    check();
    const timer = setInterval(check, 20000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => () => abortRef.current?.abort(), []);

  const startNewChat = useCallback(() => {
    abortRef.current?.abort();
    setActiveChatId(null);
    setMessages([]);
    setDraft("");
    setBusy(false);
    setActiveNav("home");
  }, []);

  const send = useCallback(
    async (rawText) => {
      const text = (rawText ?? draft).trim();
      if (!text || busy) return;

      setDraft("");
      setBusy(true);
      setActiveNav("home");

      if (!activeChatId) {
        const chat = {
          id: `${Date.now()}`,
          title: titleFor(text),
          createdAt: Date.now(),
        };
        setChats((prev) => [chat, ...prev]);
        setActiveChatId(chat.id);
      }

      // Push the user turn plus an empty bot turn to stream into.
      setMessages((prev) => [
        ...prev,
        { role: "user", content: text },
        { role: "bot", content: "", sources: [], pending: true },
      ]);

      const controller = new AbortController();
      abortRef.current = controller;

      const failWith = (error) =>
        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = { role: "bot", content: "", error };
          return next;
        });

      try {
        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: text }),
          signal: controller.signal,
        });

        if (!response.ok) {
          failWith(
            `The assistant could not answer (HTTP ${response.status}). Check that the backend is running.`,
          );
          return;
        }

        let sources = [];
        const header = response.headers.get("X-Sources");
        if (header) {
          try {
            sources = JSON.parse(header);
          } catch {
            sources = [];
          }
        }

        // Non-streaming replies (safety refusals, no-context) come back as JSON.
        const contentType = response.headers.get("Content-Type") || "";
        if (contentType.includes("application/json")) {
          const data = await response.json();
          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = {
              role: "bot",
              content: data.reply || "",
              error: data.error,
              sources: data.sources || [],
            };
            return next;
          });
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulated = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          accumulated += decoder.decode(value, { stream: true });

          setMessages((prev) => {
            const next = [...prev];
            next[next.length - 1] = {
              role: "bot",
              content: accumulated,
              sources,
              pending: true,
            };
            return next;
          });
        }

        setMessages((prev) => {
          const next = [...prev];
          next[next.length - 1] = {
            role: "bot",
            content: accumulated,
            sources,
            pending: false,
          };
          return next;
        });
      } catch (error) {
        if (error.name !== "AbortError") {
          failWith(
            "Could not reach the assistant. Make sure the backend is running on port 5000.",
          );
        }
      } finally {
        setBusy(false);
        abortRef.current = null;
      }
    },
    [activeChatId, busy, draft],
  );

  // On mobile the sidebar sits over the content, so dismiss it after a choice.
  const closeIfMobile = () => {
    if (isMobileWidth()) setCollapsed(true);
  };

  const handleNavigate = (id) => {
    if (id === "new") {
      startNewChat();
      closeIfMobile();
      return;
    }
    setActiveNav(id);
    closeIfMobile();
  };

  const handleSelectChat = (id) => {
    setActiveChatId(id);
    setActiveNav("home");
    closeIfMobile();
  };

  const showWelcome = messages.length === 0;

  return (
    <div className="app">
      <a className="skip-link" href="#main">
        Skip to content
      </a>

      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNavigate={handleNavigate}
        activeNav={activeNav}
        health={health}
      />

      {/* Scrim only renders under the overlay sidebar on narrow screens. */}
      {!collapsed && (
        <button
          className="scrim"
          onClick={() => setCollapsed(true)}
          aria-label="Close navigation"
          tabIndex={-1}
        />
      )}

      <main className="main" id="main">
        <div className="mobile-bar">
          <button
            className="icon-btn"
            onClick={() => setCollapsed((c) => !c)}
            aria-label="Show navigation"
          >
            <MenuIcon />
          </button>
          <span className="mobile-bar__title">Health Reference</span>
        </div>

        <div className="main__scroll">
          <div className="main__inner">
            {showWelcome ? (
              <WelcomeScreen recent={chats} onAsk={send} />
            ) : (
              <ChatThread messages={messages} />
            )}
          </div>
        </div>

        <Composer
          value={draft}
          onChange={setDraft}
          onSubmit={() => send()}
          busy={busy}
        />
      </main>
    </div>
  );
}
