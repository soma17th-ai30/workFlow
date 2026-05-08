import DebugPanel from "./DebugPanel";
import ResultVisual from "./ResultVisual";

type ResultCardProps = {
  resultText: string;
  channel: string;
  relationship: string;
  tone: string;
  appliedFeedbackSummary: string;
  copyStatus: string;
  includeDebug: boolean;
  debugOutput: string;
  onCopy: () => void;
};

export default function ResultCard({
  resultText,
  channel,
  relationship,
  tone,
  appliedFeedbackSummary,
  copyStatus,
  includeDebug,
  debugOutput,
  onCopy
}: ResultCardProps) {
  return (
    <aside className="result-card" aria-label="다듬어진 메시지 결과">
      <div className="result-header">
        <div>
          <p className="eyebrow">Polished Message</p>
          <h1>결과</h1>
        </div>
        <button type="button" className="copy-button" onClick={onCopy}>
          ▣ 복사
        </button>
      </div>

      <div className="result-box">{resultText}</div>

      <div className="tag-row" aria-label="선택된 맥락">
        <span>#{channel}</span>
        <span>#{relationship}</span>
        <span>#{tone}</span>
      </div>

      {(appliedFeedbackSummary || copyStatus) && (
        <div className="status-row">
          {appliedFeedbackSummary && <span>{appliedFeedbackSummary}</span>}
          {copyStatus && <span>{copyStatus}</span>}
        </div>
      )}

      <ResultVisual />

      {includeDebug && <DebugPanel debugOutput={debugOutput} />}
    </aside>
  );
}
