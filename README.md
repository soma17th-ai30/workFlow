# 30만큼 사랑해

상황, 관계, 목적, 톤에 맞게 메시지를 다듬어 주는 LLM 기반 메시지 폴리싱 서비스입니다.

## 준비

Python 패키지 설치:

```bash
python -m pip install -r requirements.txt
```

프론트엔드 패키지 설치:

```bash
cd frontend
npm install
```

환경변수 설정:

```bash
copy .env.example .env
```

`.env`의 `UPSTAGE_API_KEY`를 실제 키로 바꿔주세요.

## 실행

백엔드 실행:

```bash
python web_server.py --host 127.0.0.1 --port 8000
```

프론트엔드 실행:

```bash
cd frontend
npm run dev
```

브라우저에서 접속:

```text
http://127.0.0.1:5173
```

## 경로

- `/`: Guide 페이지
- `/polish`: 메시지 다듬기 페이지
- 백엔드 API: `POST http://127.0.0.1:8000/api/polish`

API 상세는 [API_SPEC.md](./API_SPEC.md)를 참고하세요.
