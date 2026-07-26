import {
  HomeIcon,
  ChatIcon,
  TopicsIcon,
  BookmarkIcon,
  ShieldIcon,
  SettingsIcon,
  CollapseIcon,
  MenuIcon,
} from "./Icons";

const NAV = [
  { id: "home", label: "Ask", Icon: HomeIcon },
  { id: "new", label: "New enquiry", Icon: ChatIcon },
  { id: "topics", label: "Topic index", Icon: TopicsIcon },
  { id: "saved", label: "Saved answers", Icon: BookmarkIcon },
  { id: "sources", label: "Source library", Icon: ShieldIcon },
];

function groupByDay(chats) {
  const groups = { Today: [], Yesterday: [], Earlier: [] };

  const startOfToday = new Date();
  startOfToday.setHours(0, 0, 0, 0);

  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);

  for (const chat of chats) {
    if (chat.createdAt >= startOfToday.getTime()) groups.Today.push(chat);
    else if (chat.createdAt >= startOfYesterday.getTime())
      groups.Yesterday.push(chat);
    else groups.Earlier.push(chat);
  }

  return groups;
}

function StatusRow({ label, state, value }) {
  return (
    <div className={`status__row status--${state}`}>
      <span className={`dot dot--${state}`} aria-hidden="true" />
      <span className="status__label">{label}</span>
      <span className="status__value">{value}</span>
    </div>
  );
}

export default function Sidebar({
  collapsed,
  onToggle,
  chats,
  activeChatId,
  onSelectChat,
  onNavigate,
  activeNav,
  health,
}) {
  const groups = groupByDay(chats);

  const state = (loading, ok) => (loading ? "wait" : ok ? "on" : "off");

  return (
    <aside className={`sidebar${collapsed ? " sidebar--collapsed" : ""}`}>
      <div className="sidebar__head">
        {collapsed ? (
          <button
            className="icon-btn"
            onClick={onToggle}
            aria-label="Show navigation"
            title="Show navigation"
          >
            <MenuIcon />
          </button>
        ) : (
          <>
            <div className="monogram" aria-hidden="true">
              Rx
            </div>
            <div className="sidebar__wordmark">
              <strong>Health Reference</strong>
              <span>Cited answers</span>
            </div>
            <button
              className="icon-btn"
              onClick={onToggle}
              aria-label="Hide navigation"
              title="Hide navigation"
            >
              <CollapseIcon />
            </button>
          </>
        )}
      </div>

      <nav className="sidebar__nav" aria-label="Main">
        {NAV.map(({ id, label, Icon }) => (
          <button
            key={id}
            className={`nav-item${activeNav === id ? " nav-item--active" : ""}`}
            onClick={() => onNavigate(id)}
            title={collapsed ? label : undefined}
            aria-label={collapsed ? label : undefined}
            aria-current={activeNav === id ? "page" : undefined}
          >
            <Icon className="nav-item__icon" />
            {!collapsed && <span className="nav-item__label">{label}</span>}
          </button>
        ))}
      </nav>

      {!collapsed && (
        <div className="sidebar__history">
          {chats.length === 0 ? (
            <p className="sidebar__empty">
              Enquiries you make will be listed here.
            </p>
          ) : (
            Object.entries(groups).map(([label, items]) =>
              items.length === 0 ? null : (
                <div key={label}>
                  <div className="sidebar__group">
                    <span className="eyebrow">{label}</span>
                  </div>
                  {items.map((chat) => (
                    <button
                      key={chat.id}
                      className={`history-item${
                        chat.id === activeChatId ? " history-item--active" : ""
                      }`}
                      onClick={() => onSelectChat(chat.id)}
                      title={chat.title}
                    >
                      {chat.title}
                    </button>
                  ))}
                </div>
              ),
            )
          )}
        </div>
      )}

      {!collapsed && (
        <div className="sidebar__foot">
          <div className="status">
            <StatusRow
              label="Assistant"
              state={state(health.loading, health.apiConnected)}
              value={
                health.loading
                  ? "checking"
                  : health.apiConnected
                    ? "online"
                    : "offline"
              }
            />
            <StatusRow
              label="MongoDB"
              state={state(health.loading, health.dbConnected)}
              value={
                health.loading
                  ? "checking"
                  : health.dbConnected
                    ? "connected"
                    : "unreachable"
              }
            />
          </div>

          <button
            className="nav-item"
            style={{ marginTop: "var(--s2)" }}
            onClick={() => onNavigate("settings")}
          >
            <SettingsIcon className="nav-item__icon" />
            <span className="nav-item__label">Settings</span>
          </button>
        </div>
      )}
    </aside>
  );
}
