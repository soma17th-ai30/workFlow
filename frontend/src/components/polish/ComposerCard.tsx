import { channelOptions, exampleMessage, relationshipOptions, toneOptions } from "../../constants/polishOptions";

type ComposerCardProps = {
  originalMessage: string;
  feedbackMessage: string;
  relationship: string;
  channel: string;
  tone: string;
  includeDebug: boolean;
  isLoading: boolean;
  hasResult: boolean;
  canSubmit: boolean;
  errorMessage: string;
  onOriginalMessageChange: (value: string) => void;
  onFeedbackMessageChange: (value: string) => void;
  onRelationshipChange: (value: string) => void;
  onChannelChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onIncludeDebugChange: (value: boolean) => void;
  onSubmit: () => void;
  onReset: () => void;
};

export default function ComposerCard({
  originalMessage,
  feedbackMessage,
  relationship,
  channel,
  tone,
  includeDebug,
  isLoading,
  hasResult,
  canSubmit,
  errorMessage,
  onOriginalMessageChange,
  onFeedbackMessageChange,
  onRelationshipChange,
  onChannelChange,
  onToneChange,
  onIncludeDebugChange,
  onSubmit,
  onReset
}: ComposerCardProps) {
  return (
    <section className="composer-card" aria-label="메시지 입력">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <div className="field">
          <div className="label-row">
            <label htmlFor="originalMessage">원문 메시지</label>
            <span className="doc-icon" aria-hidden="true">
              ▧
            </span>
          </div>
          <textarea
            id="originalMessage"
            className="original-input"
            value={originalMessage}
            onChange={(event) => onOriginalMessageChange(event.target.value)}
            placeholder="다듬고 싶은 메시지를 입력하세요."
          />
        </div>

        <div className="context-grid" aria-label="메시지 맥락 선택">
          <label>
            상대
            <select value={relationship} onChange={(event) => onRelationshipChange(event.target.value)}>
              {relationshipOptions.map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          </label>
          <label>
            채널
            <select value={channel} onChange={(event) => onChannelChange(event.target.value)}>
              {channelOptions.map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          </label>
          <label>
            톤
            <select value={tone} onChange={(event) => onToneChange(event.target.value)}>
              {toneOptions.map((option) => (
                <option key={option}>{option}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="field feedback-field">
          <label htmlFor="feedbackMessage">수정 피드백</label>
          <textarea
            id="feedbackMessage"
            className="feedback-input"
            value={feedbackMessage}
            onChange={(event) => onFeedbackMessageChange(event.target.value)}
            placeholder="첫 요청이면 비워두고, 결과를 받은 뒤 더 반영할 내용을 적으세요."
          />
        </div>

        <div className="actions">
          <button className="primary-action" type="submit" disabled={!canSubmit}>
            <span aria-hidden="true">✎</span>
            {isLoading ? "다듬는 중" : hasResult ? "다시 다듬기" : "다듬기"}
          </button>
          <button type="button" className="secondary-action" onClick={() => onOriginalMessageChange(exampleMessage)}>
            예시 넣기
          </button>
          <button type="button" className="secondary-action" onClick={onReset}>
            초기화
          </button>
          <label className="debug-toggle">
            <input
              type="checkbox"
              checked={includeDebug}
              onChange={(event) => onIncludeDebugChange(event.target.checked)}
            />
            개발용 분석 결과 포함
          </label>
        </div>

        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </form>
    </section>
  );
}
