import { NavLink } from "react-router-dom";

export default function SiteHeader() {
  return (
    <header className="site-header">
      <NavLink className="brand" to="/" aria-label="30만큼 사랑해 홈">
        30만큼 사랑해
      </NavLink>
      <nav className="main-nav" aria-label="주요 메뉴">
        <NavLink to="/polish">Polish</NavLink>
        <NavLink to="/" end>
          Guide
        </NavLink>
      </nav>
      <div className="header-tools">
        <NavLink className="start-writing" to="/polish">
          Start Writing
        </NavLink>
      </div>
    </header>
  );
}
