from __future__ import annotations

import argparse
import importlib.util
import json
import mimetypes
import os
import sys
import traceback
import warnings
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

warnings.filterwarnings("ignore")
warnings.showwarning = lambda *args, **kwargs: None

if __package__ in {None, ""}:
    package_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(package_dir.parent))
    if "message_polishing" not in sys.modules:
        package_spec = importlib.util.spec_from_file_location(
            "message_polishing",
            package_dir / "__init__.py",
            submodule_search_locations=[str(package_dir)],
        )
        if package_spec and package_spec.loader:
            package_module = importlib.util.module_from_spec(package_spec)
            sys.modules["message_polishing"] = package_module
            package_spec.loader.exec_module(package_module)

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
    .debug {
      margin-top: 16px;
      min-height: 180px;
      max-height: 360px;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      background: #101828;
      color: #eef4ff;
      font: 12px/1.55 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
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
        <label for="debug" style="margin-top:16px;">Feature / Debug Output</label>
        <div class="debug" id="debug"></div>
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
    const debug = document.getElementById("debug");
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
            sessionId: state.sessionId,
            debug: true
          })
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Request failed");
        }
        output.textContent = data.polishedMessage;
        summary.textContent = data.appliedFeedbackSummary || "";
        debug.textContent = data.debug ? JSON.stringify(data.debug, null, 2) : "";
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
      debug.textContent = "";
      state.previousPolishedMessage = null;
      state.sessionId = "browser-test-" + Math.random().toString(36).slice(2);
    });
  </script>
</body>
</html>
"""


def get_static_dir() -> Path:
    configured_path = os.environ.get("MESSAGE_POLISHING_STATIC_DIR")
    if configured_path:
        return Path(configured_path).expanduser().resolve()
    return Path(__file__).resolve().parent / "frontend" / "dist"


class PolishingRequestHandler(BaseHTTPRequestHandler):
    server_version = "MessagePolishingHTTP/0.1"

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json({"ok": True})
            return

        if self._send_static_file():
            return

        if self.path in {"/", "/index.html"}:
            self._send_bytes(HTML.encode("utf-8"), content_type="text/html; charset=utf-8")
            return
        self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/polish":
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        try:
            payload = self._read_json()
            debug = bool(payload.pop("debug", False))
            workflow_input = MessagePolishingInput.model_validate(payload)
            result = run_message_polishing_workflow(workflow_input, debug=debug)

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

    def _send_static_file(self) -> bool:
        static_dir = get_static_dir()
        if not static_dir.is_dir():
            return False

        parsed_path = urlparse(self.path).path
        if parsed_path.startswith("/api/"):
            return False

        requested_path = unquote(parsed_path).lstrip("/") or "index.html"
        static_root = static_dir.resolve()
        candidate = (static_root / requested_path).resolve()
        try:
            candidate.relative_to(static_root)
        except ValueError:
            self._send_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return True

        if candidate.is_dir():
            candidate = candidate / "index.html"
        if not candidate.is_file():
            fallback = static_root / "index.html"
            if fallback.is_file() and self._should_fallback_to_index(parsed_path):
                candidate = fallback
            else:
                return False

        content_type = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
        if content_type.startswith("text/"):
            content_type = f"{content_type}; charset=utf-8"
        self._send_bytes(candidate.read_bytes(), content_type=content_type)
        return True

    def _should_fallback_to_index(self, parsed_path: str) -> bool:
        if Path(parsed_path).suffix:
            return False
        accept_header = self.headers.get("Accept", "")
        return "text/html" in accept_header or "*/*" in accept_header

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
