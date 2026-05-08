export type UserContext = {
  relationship: string;
  communication_channel: string;
  preferred_tone: string;
  selected_options: {
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
};

export type ApiErrorResponse = {
  error: string;
};
