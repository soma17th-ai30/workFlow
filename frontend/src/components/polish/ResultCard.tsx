import ResultVisual from "./ResultVisual";

type ResultCardProps = {
  resultText: string;
  channel: string;
  relationship: string;
  tone: string;
  appliedFeedbackSummary: string;
  copyStatus: string;
  isLoading: boolean;
  hasResult: boolean;
  onCopy: () => void;
};

export default function ResultCard({
  resultText,
  channel,
  relationship,
  tone,
  appliedFeedbackSummary,
  copyStatus,
  isLoading,
  hasResult,
  onCopy
}: ResultCardProps) {
  return (
    <aside className="result-card" aria-label="다듬어진 메시지 결과">
      <div className="result-header">
        <div>
          <p className="eyebrow">Polished Message</p>
          <h1>결과</h1>
        </div>
        <button type="button" className="copy-button" onClick={onCopy} disabled={!hasResult || isLoading}>
          ▣ 복사
        </button>
      </div>

      <div className={`result-box ${!hasResult ? "empty" : ""} ${isLoading ? "loading" : ""}`}>
        {isLoading ? (
          <div className="loading-state" role="status" aria-live="polite">
            <span className="spinner" aria-hidden="true" />
            <strong>문장을 다듬는 중입니다</strong>
            <p>상대, 채널, 톤과 피드백을 반영하고 있어요.</p>
          </div>
        ) : (
          resultText || <span className="empty-result">아직 다듬어진 메시지가 없습니다.</span>
        )}
      </div>

      {hasResult && (
        <div className="tag-row" aria-label="선택된 맥락">
          <span>#{channel}</span>
          <span>#{relationship}</span>
          <span>#{tone}</span>
        </div>
      )}

      {(appliedFeedbackSummary || copyStatus) && (
        <div className="status-row">
          {appliedFeedbackSummary && <span>{appliedFeedbackSummary}</span>}
          {copyStatus && <span>{copyStatus}</span>}
        </div>
      )}

      <ResultVisual />
    </aside>
  );
}
