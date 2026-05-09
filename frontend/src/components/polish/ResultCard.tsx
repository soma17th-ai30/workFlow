import ResultVisual from "./ResultVisual";

type ResultCardProps = {
  resultText: string;
  purpose: string;
  channel: string;
  relationship: string;
  tone: string;
  appliedFeedbackSummary: string;
  isLoading: boolean;
  hasResult: boolean;
  onCopy: () => void;
};

export default function ResultCard({
  resultText,
  purpose,
  channel,
  relationship,
  tone,
  appliedFeedbackSummary,
  isLoading,
  hasResult,
  onCopy
}: ResultCardProps) {
  return (
    <aside className="result-card" aria-label="다듬어진 메시지 결과">
      <div className="result-header">
        <div>
          <p className="eyebrow">Ready to Send</p>
          <h1>복사해서 바로 쓰기</h1>
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
            <p>의도는 유지하면서 관계, 목적, 톤을 반영하고 있어요.</p>
          </div>
        ) : (
          resultText || <span className="empty-result">원문을 입력하고 메시지를 다듬어 보세요.</span>
        )}
      </div>

      {hasResult && (
        <>
          <div className="tag-row" aria-label="선택된 맥락">
            <span>#{purpose}</span>
            <span>#{relationship}</span>
            <span>#{channel}</span>
            <span>#{tone}</span>
          </div>

          <div className="revision-card">
            <strong>수정 이유 요약</strong>
            <p>
              {appliedFeedbackSummary ||
                "원문의 의도는 유지하면서 상대와 상황에 맞는 표현 강도, 예의 수준, 문장 흐름을 조정했습니다."}
            </p>
          </div>
        </>
      )}

      <ResultVisual />
    </aside>
  );
}
