import { useMemo, useState } from "react";
import { polishMessage } from "./api";
import type { UserContext } from "./types";

const relationshipOptions = ["교수님", "상사", "동료", "친구", "고객", "기타"];
const channelOptions = ["문자", "카카오톡", "이메일", "DM"];
const toneOptions = ["정중하게", "부드럽게", "간결하게", "자연스럽게", "단호하게"];

const exampleMessage = "교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?";

function createSessionId() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function App() {
  const [sessionId, setSessionId] = useState(createSessionId);
  const [originalMessage, setOriginalMessage] = useState(exampleMessage);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [previousPolishedMessage, setPreviousPolishedMessage] = useState<string | null>(null);
  const [polishedMessage, setPolishedMessage] = useState("");
  const [appliedFeedbackSummary, setAppliedFeedbackSummary] = useState("");
  const [relationship, setRelationship] = useState(relationshipOptions[0]);
  const [channel, setChannel] = useState(channelOptions[0]);
  const [tone, setTone] = useState(toneOptions[0]);
  const [includeDebug, setIncludeDebug] = useState(false);
  const [debugOutput, setDebugOutput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [copyStatus, setCopyStatus] = useState("");

  const userContext = useMemo<UserContext>(
    () => ({
      relationship,
      communication_channel: channel,
      preferred_tone: tone,
      selected_options: {
        relationship,
        channel,
        tone
      }
    }),
    [relationship, channel, tone]
  );

  const canSubmit = originalMessage.trim().length > 0 && !isLoading;
  const hasResult = polishedMessage.trim().length > 0;

  async function handlePolish() {
    if (!canSubmit) return;

    setIsLoading(true);
    setErrorMessage("");
    setCopyStatus("");

    try {
      const data = await polishMessage({
        originalMessage: originalMessage.trim(),
        feedbackMessage: feedbackMessage.trim() || null,
        previousPolishedMessage,
        userContext,
        sessionId,
        debug: includeDebug
      });

      setPolishedMessage(data.polishedMessage);
      setPreviousPolishedMessage(data.polishedMessage);
      setAppliedFeedbackSummary(data.appliedFeedbackSummary || "");
      setDebugOutput(data.debug ? JSON.stringify(data.debug, null, 2) : "");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCopy() {
    if (!polishedMessage) return;
    await navigator.clipboard.writeText(polishedMessage);
    setCopyStatus("복사됐습니다.");
  }

  function handleReset() {
    setSessionId(createSessionId());
    setOriginalMessage("");
    setFeedbackMessage("");
    setPreviousPolishedMessage(null);
    setPolishedMessage("");
    setAppliedFeedbackSummary("");
    setDebugOutput("");
    setErrorMessage("");
    setCopyStatus("");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Message Polishing</p>
          <h1>보내기 전, 메시지를 한 번 더 다듬어요.</h1>
        </div>
        <div className="session-chip" title={sessionId}>
          세션 유지 중
        </div>
      </header>

      <section className="workspace" aria-label="메시지 다듬기 작업 영역">
        <form
          className="input-panel"
          onSubmit={(event) => {
            event.preventDefault();
            void handlePolish();
          }}
        >
          <div className="field">
            <label htmlFor="originalMessage">원문 메시지</label>
            <textarea
              id="originalMessage"
              value={originalMessage}
              onChange={(event) => setOriginalMessage(event.target.value)}
              placeholder="다듬고 싶은 메시지를 입력하세요."
            />
          </div>

          <div className="context-grid" aria-label="메시지 맥락 선택">
            <label>
              상대
              <select value={relationship} onChange={(event) => setRelationship(event.target.value)}>
                {relationshipOptions.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </label>
            <label>
              채널
              <select value={channel} onChange={(event) => setChannel(event.target.value)}>
                {channelOptions.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </label>
            <label>
              톤
              <select value={tone} onChange={(event) => setTone(event.target.value)}>
                {toneOptions.map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="field">
            <label htmlFor="feedbackMessage">수정 피드백</label>
            <textarea
              id="feedbackMessage"
              className="feedback-input"
              value={feedbackMessage}
              onChange={(event) => setFeedbackMessage(event.target.value)}
              placeholder="첫 요청이면 비워두고, 결과를 받은 뒤 더 반영할 내용을 적으세요."
            />
          </div>

          <div className="actions">
            <button type="submit" disabled={!canSubmit}>
              {isLoading ? "다듬는 중..." : hasResult ? "다시 다듬기" : "메시지 다듬기"}
            </button>
            <button type="button" className="secondary" onClick={() => setOriginalMessage(exampleMessage)}>
              예시 넣기
            </button>
            <button type="button" className="secondary" onClick={handleReset}>
              초기화
            </button>
          </div>

          <label className="debug-toggle">
            <input
              type="checkbox"
              checked={includeDebug}
              onChange={(event) => setIncludeDebug(event.target.checked)}
            />
            개발용 분석 결과 포함
          </label>

          {errorMessage && <p className="error-message">{errorMessage}</p>}
        </form>

        <aside className="output-panel" aria-label="다듬어진 메시지 결과">
          <div className="output-header">
            <div>
              <p className="eyebrow">Polished Message</p>
              <h2>결과</h2>
            </div>
            <button type="button" className="secondary" onClick={handleCopy} disabled={!hasResult}>
              복사
            </button>
          </div>

          <div className={`result-box ${hasResult ? "" : "empty"}`}>
            {hasResult ? polishedMessage : "아직 결과가 없습니다."}
          </div>

          {(appliedFeedbackSummary || copyStatus) && (
            <div className="status-row">
              {appliedFeedbackSummary && <span>{appliedFeedbackSummary}</span>}
              {copyStatus && <span>{copyStatus}</span>}
            </div>
          )}

          {includeDebug && (
            <div className="debug-panel">
              <div className="debug-title">Debug Output</div>
              <pre>{debugOutput || "분석 결과가 아직 없습니다."}</pre>
            </div>
          )}
        </aside>
      </section>
    </main>
  );
}
