type SiteHeaderProps = {
  sessionId: string;
};

export default function SiteHeader({ sessionId }: SiteHeaderProps) {
  return (
    <header className="site-header">
      <a className="brand" href="/" aria-label="30만큼 사랑해 홈">
        30만큼 사랑해
      </a>
      <nav className="main-nav" aria-label="주요 메뉴">
        <a className="active" href="/">
          Polish
        </a>
        <a href="/">History</a>
        <a href="/">Templates</a>
        <a href="/">Guide</a>
      </nav>
      <div className="header-tools">
        <span className="session-pill" title={sessionId}>
          세션 유지 중
        </span>
        <button className="icon-button" type="button" aria-label="되돌리기">
          ↺
        </button>
        <button className="icon-button" type="button" aria-label="설정">
          ⚙
        </button>
        <button className="icon-button" type="button" aria-label="계정">
          ○
        </button>
      </div>
    </header>
  );
}
