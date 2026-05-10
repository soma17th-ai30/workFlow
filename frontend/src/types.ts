export type UserContext = {
  purpose: string;
  relationship: string;
  communication_channel: string;
  preferred_tone: string;
  selected_options: {
    purpose: string;
    relationship: string;
    channel: string;
    tone: string;
  };
};

export type MessagePolishingRequest = {
  originalMessage: string;
  feedbackMessage?: string | null;
  previousPolishedMessage?: string | null;
  userContext?: UserContext | string | null;
  sessionId?: string | null;
};

export type MessagePolishingResponse = {
  polishedMessage: string;
  appliedFeedbackSummary?: string;
  feedbackMessage?: string | null;
};

export type ApiErrorResponse = {
  error: string;
};
