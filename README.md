# Message Polishing

원문 메시지를 polishing하고, 사용자가 피드백을 다시 입력하면 이전 결과를 기준으로 재폴리싱하는 LangGraph workflow입니다.



## 서버 실행

```bash
python3 web_server.py --host 127.0.0.1 --port 8000
```

브라우저에서 엽니다.

```text
http://127.0.0.1:8000
```

프론트엔드 연동 API 명세는 `message_polishing/API_SPEC.md`를 참고하세요.
