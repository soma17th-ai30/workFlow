import {
  channelOptions,
  purposeOptions,
  relationshipOptions,
  scenarioExamples,
  toneOptions,
} from "../../constants/polishOptions";

type Scenario = (typeof scenarioExamples)[number];

type ComposerCardProps = {
  originalMessage: string;
  feedbackMessage: string;
  purpose: string;
  relationship: string;
  channel: string;
  tone: string;
  isLoading: boolean;
  hasResult: boolean;
  canSubmit: boolean;
  errorMessage: string;
  onOriginalMessageChange: (value: string) => void;
  onFeedbackMessageChange: (value: string) => void;
  onPurposeChange: (value: string) => void;
  onRelationshipChange: (value: string) => void;
  onChannelChange: (value: string) => void;
  onToneChange: (value: string) => void;
  onScenarioSelect: (scenario: Scenario) => void;
  onSubmit: () => void;
  onReset: () => void;
};

export default function ComposerCard({
  originalMessage,
  feedbackMessage,
  purpose,
  relationship,
  channel,
  tone,
  isLoading,
  hasResult,
  canSubmit,
  errorMessage,
  onOriginalMessageChange,
  onFeedbackMessageChange,
  onPurposeChange,
  onRelationshipChange,
  onChannelChange,
  onToneChange,
  onScenarioSelect,
  onSubmit,
  onReset,
}: ComposerCardProps) {
  return (
    <section className="composer-card" aria-label="메시지 입력">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit();
        }}
      >
        <div className="step-label">1. 보내기 망설여지는 문장 입력</div>
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
            placeholder="예: 교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?"
          />
        </div>

        <div className="scenario-row" aria-label="빠른 시나리오 선택">
          {scenarioExamples.map((scenario) => (
            <button
              type="button"
              key={scenario.label}
              onClick={() => onScenarioSelect(scenario)}
            >
              {scenario.label}
            </button>
          ))}
        </div>

        <div className="field feedback-field">
          <label htmlFor="feedbackMessage">추가 요청 / 수정 피드백</label>
          <textarea
            id="feedbackMessage"
            className="feedback-input"
            value={feedbackMessage}
            onChange={(event) => onFeedbackMessageChange(event.target.value)}
            placeholder="예: 더 죄송한 느낌으로, 너무 길지 않게, 고객 응대처럼 전문적으로"
          />
        </div>

        <div className="privacy-note">
          메시지 원문은 저장하지 않는 것을 원칙으로 하고, 입력한 맥락은 이번
          요청 처리에만 사용됩니다.
        </div>

        <div className="actions">
          <button
            className="primary-action"
            type="submit"
            disabled={!canSubmit}
          >
            <span aria-hidden="true">✎</span>
            {isLoading
              ? "다듬는 중"
              : hasResult
                ? "피드백 반영하기"
                : "메시지 다듬기"}
          </button>
          <button type="button" className="secondary-action" onClick={onReset}>
            초기화
          </button>
        </div>

        {errorMessage && <p className="error-message">{errorMessage}</p>}
      </form>
    </section>
  );
}
