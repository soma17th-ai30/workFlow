import type {
  ApiErrorResponse,
  MessagePolishingRequest,
  MessagePolishingResponse
} from "./types";

export async function polishMessage(
  payload: MessagePolishingRequest
): Promise<MessagePolishingResponse> {
  const response = await fetch("/api/polish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as MessagePolishingResponse | ApiErrorResponse;
  if (!response.ok) {
    throw new Error("error" in data ? data.error : "메시지 다듬기에 실패했습니다.");
  }

  return data as MessagePolishingResponse;
}
