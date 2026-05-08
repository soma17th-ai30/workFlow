import { NavLink } from "react-router-dom";

export default function SiteHeader() {
  return (
    <header className="site-header">
      <NavLink className="brand" to="/" aria-label="30만큼 사랑해 홈">
        30만큼 사랑해
      </NavLink>
      <nav className="main-nav" aria-label="주요 메뉴">
        <NavLink to="/" end>
          Polish
        </NavLink>
        <NavLink to="/guide">Guide</NavLink>
      </nav>
      <div className="header-tools">
        <button className="icon-button" type="button" aria-label="되돌리기">
          ↺
        </button>
        <button className="icon-button" type="button" aria-label="설정">
          ⚙
        </button>
        <button className="icon-button" type="button" aria-label="계정">
          ○
        </button>
        <NavLink className="start-writing" to="/">
          Start Writing
        </NavLink>
      </div>
    </header>
  );
}
