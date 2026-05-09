const sidebarItems = ["Dashboard", "Recent Drafts", "Saved Tones", "Pro Insights"];

export default function GuideSidebar() {
  return (
    <aside className="guide-sidebar" aria-label="가이드 보조 메뉴">
      <div className="studio-profile">
        <div className="profile-mark">⌘</div>
        <div>
          <strong>Editorial Studio</strong>
          <span>Professional Plan</span>
        </div>
      </div>

      <nav>
        {sidebarItems.map((item) => (
          <a className={item === "Pro Insights" ? "active" : ""} href="/" key={item}>
            <span aria-hidden="true">□</span>
            {item}
          </a>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <button type="button">Upgrade to Pro</button>
        <a href="/">Help Center</a>
        <a href="/">Log Out</a>
      </div>
    </aside>
  );
}
