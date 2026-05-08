export default function ResultVisual() {
  return (
    <div className="visual-panel" aria-hidden="true">
      <div className="paper-stack">
        <div className="paper paper-back" />
        <div className="paper paper-front">
          <span />
          <span />
          <span />
        </div>
      </div>
      <div className="pen-shape" />
      <div className="spark one" />
      <div className="spark two" />
      <div className="spark three" />
    </div>
  );
}
