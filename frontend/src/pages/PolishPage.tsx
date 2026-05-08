import { useMemo, useState } from "react";
import SiteFooter from "../components/layout/SiteFooter";
import SiteHeader from "../components/layout/SiteHeader";
import ComposerCard from "../components/polish/ComposerCard";
import ResultCard from "../components/polish/ResultCard";
import { polishMessage } from "../api";
import {
  channelOptions,
  exampleMessage,
  relationshipOptions,
  toneOptions
} from "../constants/polishOptions";
import type { UserContext } from "../types";
import { createSessionId } from "../utils/session";

export default function PolishPage() {
  const [sessionId, setSessionId] = useState(createSessionId);
  const [originalMessage, setOriginalMessage] = useState(exampleMessage);
  const [feedbackMessage, setFeedbackMessage] = useState("");
  const [previousPolishedMessage, setPreviousPolishedMessage] = useState<string | null>(null);
  const [polishedMessage, setPolishedMessage] = useState("");
  const [appliedFeedbackSummary, setAppliedFeedbackSummary] = useState("");
  const [relationship, setRelationship] = useState(relationshipOptions[0]);
  const [channel, setChannel] = useState(channelOptions[0]);
  const [tone, setTone] = useState(toneOptions[0]);
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
  const resultText = hasResult ? polishedMessage : "";

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
    await navigator.clipboard.writeText(resultText);
    setCopyStatus("복사됐습니다.");
  }

  function handleReset() {
    setSessionId(createSessionId());
    setOriginalMessage("");
    setFeedbackMessage("");
    setPreviousPolishedMessage(null);
    setPolishedMessage("");
    setAppliedFeedbackSummary("");
    setErrorMessage("");
    setCopyStatus("");
  }

  return (
    <div className="page-frame">
      <SiteHeader />

      <main className="app-shell">
        <ComposerCard
          originalMessage={originalMessage}
          feedbackMessage={feedbackMessage}
          relationship={relationship}
          channel={channel}
          tone={tone}
          isLoading={isLoading}
          hasResult={hasResult}
          canSubmit={canSubmit}
          errorMessage={errorMessage}
          onOriginalMessageChange={setOriginalMessage}
          onFeedbackMessageChange={setFeedbackMessage}
          onRelationshipChange={setRelationship}
          onChannelChange={setChannel}
          onToneChange={setTone}
          onSubmit={handlePolish}
          onReset={handleReset}
        />

        <ResultCard
          resultText={resultText}
          channel={channel}
          relationship={relationship}
          tone={tone}
          appliedFeedbackSummary={appliedFeedbackSummary}
          copyStatus={copyStatus}
          isLoading={isLoading}
          hasResult={hasResult}
          onCopy={handleCopy}
        />
      </main>

      <SiteFooter />
    </div>
  );
}
