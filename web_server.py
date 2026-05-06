from __future__ import annotations

import argparse
import json
import sys
import traceback
import warnings
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore")
warnings.showwarning = lambda *args, **kwargs: None

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from message_polishing import MessagePolishingInput, run_message_polishing_workflow
from message_polishing.env import load_dotenv


HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Message Polishing Test</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --text: #172033;
      --muted: #647084;
      --line: #d9deea;
      --accent: #2563eb;
      --accent-dark: #1d4ed8;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    main {
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0;
    }
    header {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0;
      font-size: 24px;
      font-weight: 760;
      letter-spacing: 0;
    }
    .mode {
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }
    .layout {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
      gap: 16px;
      align-items: start;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }
    label {
      display: block;
      margin: 0 0 8px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
    }
    textarea {
      width: 100%;
      min-height: 122px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      color: var(--text);
      font: inherit;
      line-height: 1.5;
      background: #fff;
    }
    textarea:focus {
      border-color: var(--accent);
      outline: 3px solid rgba(37, 99, 235, 0.16);
    }
    .field + .field { margin-top: 14px; }
    .actions {
      display: flex;
      gap: 8px;
      margin-top: 14px;
      flex-wrap: wrap;
    }
    button {
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      min-height: 40px;
      background: var(--accent);
      color: #fff;
      font-weight: 720;
      cursor: pointer;
    }
    button.secondary {
      background: #e8edf7;
      color: #22304a;
    }
    button:disabled {
      cursor: wait;
      opacity: 0.68;
    }
    .output {
      min-height: 230px;
      white-space: pre-wrap;
      line-height: 1.6;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 14px;
      background: #fbfcff;
    }
    .summary {
      min-height: 24px;
      margin-top: 12px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }
    .error {
      color: var(--danger);
      font-weight: 650;
    }
    @media (max-width: 760px) {
      header { align-items: flex-start; flex-direction: column; }
      .layout { grid-template-columns: 1fr; }
      main { width: min(100vw - 20px, 1120px); padding: 18px 0; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Message Polishing Test</h1>
      <div class="mode">Upstage API mode</div>
    </header>
    <div class="layout">
      <section>
        <div class="field">
          <label for="original">원문 메시지</label>
          <textarea id="original">교수님 제가 일이 있어서 과제 제출 좀 늦게 해도 될까요?</textarea>
        </div>
        <div class="field">
          <label for="feedback">피드백</label>
          <textarea id="feedback" placeholder="처음 생성할 때는 비워두고, 결과를 받은 뒤 수정 요청을 입력하세요."></textarea>
        </div>
        <div class="actions">
          <button id="submit">Polish</button>
          <button class="secondary" id="example">피드백 예시</button>
          <button class="secondary" id="reset">Reset</button>
        </div>
      </section>
      <section>
        <label>Polished Message</label>
        <div class="output" id="output"></div>
        <div class="summary" id="summary"></div>
      </section>
    </div>
  </main>
  <script>
    const state = {
      previousPolishedMessage: null,
      sessionId: "browser-test-" + Math.random().toString(36).slice(2)
    };
    const original = document.getElementById("original");
    const feedback = document.getElementById("feedback");
    const output = document.getElementById("output");
    const summary = document.getElementById("summary");
    const submit = document.getElementById("submit");

    async function polish() {
      submit.disabled = true;
      summary.textContent = "Running...";
      summary.className = "summary";
      try {
        const response = await fetch("/api/polish", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            originalMessage: original.value,
            feedbackMessage: feedback.value || null,
            previousPolishedMessage: state.previousPolishedMessage,
            sessionId: state.sessionId
          })
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Request failed");
        }
        output.textContent = data.polishedMessage;
        summary.textContent = data.appliedFeedbackSummary || "";
        state.previousPolishedMessage = data.polishedMessage;
      } catch (error) {
        summary.textContent = error.message;
        summary.className = "summary error";
      } finally {
        submit.disabled = false;
      }
    }

    submit.addEventListener("click", polish);
    document.getElementById("example").addEventListener("click", () => {
      feedback.value = "좀 더 죄송한 느낌을 넣고, 금요일까지 제출 가능하다고 말해줘";
    });
    document.getElementById("reset").addEventListener("click", () => {
      feedback.value = "";
      output.textContent = "";
      summary.textContent = "";
      state.previousPolishedMessage = null;
      state.sessionId = "browser-test-" + Math.random().toString(36).slice(2);
    });
  </script>
</body>
</html>
"""


class PolishingRequestHandler(BaseHTTPRequestHandler):
    server_version = "MessagePolishingHTTP/0.1"

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._send_bytes(HTML.encode("utf-8"), content_type="text/html; charset=utf-8")
            return
        if self.path == "/health":
            self._send_json({"ok": True})
            return
        if self.path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/polish":
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            workflow_input = MessagePolishingInput.model_validate(payload)
            result = run_message_polishing_workflow(workflow_input, debug=False)

            self._send_json(result.model_dump(by_alias=True, exclude_none=True))
        except Exception as exc:
            traceback.print_exc()
            self._send_json({"error": str(exc)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args: Any) -> None:
        print("%s - %s" % (self.address_string(), format % args))

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length)
        return json.loads(raw_body.decode("utf-8") or "{}")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send_bytes(
            json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            status=status,
            content_type="application/json; charset=utf-8",
        )

    def _send_bytes(
        self,
        payload: bytes,
        *,
        status: HTTPStatus = HTTPStatus.OK,
        content_type: str,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the message polishing HTML test server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    load_dotenv()

    server = ThreadingHTTPServer((args.host, args.port), PolishingRequestHandler)
    print(f"Serving message polishing test UI at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
