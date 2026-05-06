# Message Polishing API Spec

이 문서는 내장 HTML 또는 같은 서버에서 서빙되는 프론트엔드가 `message_polishing.web_server`에 붙기 위한 최소 API 명세입니다.

## Base URL

로컬 기본값:

```text
http://127.0.0.1:8000
```

서버 실행:

```bash
python3 -m message_polishing.web_server --host 127.0.0.1 --port 8000
```

## GET /

내장 테스트 HTML을 반환합니다.

## GET /health

서버 상태 확인용 endpoint입니다.

Response `200`:

```json
{
  "ok": true
}
```

## POST /api/polish

메시지를 polishing하거나, 이전 polishing 결과에 사용자 피드백을 반영해 다시 polishing합니다.

Headers:

```http
Content-Type: application/json
```

Request body:

```ts
type MessagePolishingRequest = {
  originalMessage: string;
  feedbackMessage?: string | null;
  previousPolishedMessage?: string | null;
  userContext?: Record<string, unknown> | string | null;
  sessionId?: string | null;
};
```

Field notes:

- `originalMessage`: 사용자가 처음 입력한 원문 메시지입니다. 필수입니다.
- `feedbackMessage`: 이전 결과에 대한 수정 요청입니다. 첫 polishing에는 `null` 또는 생략합니다.
- `previousPolishedMessage`: 프론트엔드가 들고 있는 직전 `polishedMessage`입니다. 피드백 재반영 시 넘기는 것을 권장합니다.
- `userContext`: 상대와의 관계, 선호 톤, 채널 같은 선택 맥락입니다.
- `sessionId`: 같은 브라우저 세션의 연속 polishing을 묶는 ID입니다. 프론트엔드에서 UUID를 만들어 유지하면 됩니다.

Response `200`:

```ts
type MessagePolishingResponse = {
  polishedMessage: string;
  appliedFeedbackSummary?: string;
};
```

Error response `500`:

```ts
type ErrorResponse = {
  error: string;
};
```

## Frontend State Flow

프론트엔드는 최소한 아래 상태를 유지하면 됩니다.

```ts
const state = {
  sessionId: crypto.randomUUID(),
  previousPolishedMessage: null as string | null,
};
```

첫 polishing:

```ts
const response = await fetch("/api/polish", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    originalMessage,
    feedbackMessage: null,
    previousPolishedMessage: null,
    sessionId: state.sessionId,
  }),
});

const data = await response.json();
state.previousPolishedMessage = data.polishedMessage;
```

피드백 재반영:

```ts
const response = await fetch("/api/polish", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    originalMessage,
    feedbackMessage,
    previousPolishedMessage: state.previousPolishedMessage,
    sessionId: state.sessionId,
  }),
});

const data = await response.json();
state.previousPolishedMessage = data.polishedMessage;
```

## Curl Examples

처음 polishing:

```bash
curl -sS http://127.0.0.1:8000/api/polish \
  -H 'Content-Type: application/json' \
  --data '{
    "originalMessage": "교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?",
    "sessionId": "frontend-test-1"
  }'
```

피드백 재반영:

```bash
curl -sS http://127.0.0.1:8000/api/polish \
  -H 'Content-Type: application/json' \
  --data '{
    "originalMessage": "교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?",
    "feedbackMessage": "뭔가 덜 죄송해보여",
    "previousPolishedMessage": "교수님, 과제 제출 기한을 조금 연장해 주실 수 있을까요?",
    "sessionId": "frontend-test-1"
  }'
```
