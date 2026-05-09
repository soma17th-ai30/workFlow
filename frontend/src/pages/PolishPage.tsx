import { useMemo, useState } from "react";
import Toast from "../components/common/Toast";
import SiteFooter from "../components/layout/SiteFooter";
import SiteHeader from "../components/layout/SiteHeader";
import ComposerCard from "../components/polish/ComposerCard";
import ResultCard from "../components/polish/ResultCard";
import { polishMessage } from "../api";
import {
  channelOptions,
  exampleMessage,
  purposeOptions,
  relationshipOptions,
  toneOptions
} from "../constants/polishOptions";
import type { UserContext } from "../types";
import { createSessionId } from "../utils/session";

type Scenario = {
  purpose: string;
  relationship: string;
  channel: string;
  tone: string;
  message: string;
};

type ToastState = {
  message: string;
  variant: "success" | "error";
};

export default function PolishPage() {
  const [sessionId, setSessionId] = useState(createSessionId);
  const [originalMessage, setOriginalMessage] = useState(exampleMessage);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [previousPolishedMessage, setPreviousPolishedMessage] = useState<string | null>(null);
  const [polishedMessage, setPolishedMessage] = useState("");
  const [appliedFeedbackSummary, setAppliedFeedbackSummary] = useState("");
  const [purpose, setPurpose] = useState(purposeOptions[0]);
  const [relationship, setRelationship] = useState(relationshipOptions[0]);
  const [channel, setChannel] = useState(channelOptions[0]);
  const [tone, setTone] = useState(toneOptions[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [toast, setToast] = useState<ToastState | null>(null);

  const userContext = useMemo<UserContext>(
    () => ({
      purpose,
      relationship,
      communication_channel: channel,
      preferred_tone: tone,
      selected_options: {
        purpose,
        relationship,
        channel,
        tone
      }
    }),
    [purpose, relationship, channel, tone]
  );

  const canSubmit = originalMessage.trim().length > 0 && !isLoading;
  const hasResult = polishedMessage.trim().length > 0;
  const resultText = hasResult ? polishedMessage : "";

  function showToast(message: string, variant: ToastState["variant"] = "success") {
    setToast({ message, variant });
    window.setTimeout(() => setToast(null), 2200);
  }

  async function handlePolish() {
    if (!canSubmit) return;

    setIsLoading(true);
    setErrorMessage("");
    setToast(null);

    try {
      const data = await polishMessage({
        originalMessage: originalMessage.trim(),
        feedbackMessage: feedbackMessage.trim() || null,
        previousPolishedMessage,
        userContext,
        sessionId
      });

      setPolishedMessage(data.polishedMessage);
      setPreviousPolishedMessage(data.polishedMessage);
      setAppliedFeedbackSummary(data.appliedFeedbackSummary || "");
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(resultText);
      showToast("복사가 완료되었습니다.");
    } catch {
      showToast("복사에 실패했습니다. 다시 시도해 주세요.", "error");
    }
  }

  function handleScenarioSelect(scenario: Scenario) {
    setOriginalMessage(scenario.message);
    setPurpose(scenario.purpose);
    setRelationship(scenario.relationship);
    setChannel(scenario.channel);
    setTone(scenario.tone);
    setFeedbackMessage("");
    setToast(null);
  }

  function handleReset() {
    setSessionId(createSessionId());
    setOriginalMessage("");
    setFeedbackMessage("");
    setPreviousPolishedMessage(null);
    setPolishedMessage("");
    setAppliedFeedbackSummary("");
    setPurpose(purposeOptions[0]);
    setRelationship(relationshipOptions[0]);
    setChannel(channelOptions[0]);
    setTone(toneOptions[0]);
    setErrorMessage("");
    setToast(null);
  }

  return (
    <div className="page-frame">
      <SiteHeader />

      <main className="app-shell">
        <ComposerCard
          originalMessage={originalMessage}
          feedbackMessage={feedbackMessage}
          purpose={purpose}
          relationship={relationship}
          channel={channel}
          tone={tone}
          isLoading={isLoading}
          hasResult={hasResult}
          canSubmit={canSubmit}
          errorMessage={errorMessage}
          onOriginalMessageChange={setOriginalMessage}
          onFeedbackMessageChange={setFeedbackMessage}
          onPurposeChange={setPurpose}
          onRelationshipChange={setRelationship}
          onChannelChange={setChannel}
          onToneChange={setTone}
          onScenarioSelect={handleScenarioSelect}
          onSubmit={handlePolish}
          onReset={handleReset}
        />

        <ResultCard
          resultText={resultText}
          purpose={purpose}
          channel={channel}
          relationship={relationship}
          tone={tone}
          appliedFeedbackSummary={appliedFeedbackSummary}
          isLoading={isLoading}
          hasResult={hasResult}
          onCopy={handleCopy}
        />
      </main>

      {toast && <Toast message={toast.message} variant={toast.variant} />}
      <SiteFooter />
    </div>
  );
}
