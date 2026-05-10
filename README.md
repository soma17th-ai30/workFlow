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

시연 중 Agent별 backend input/output을 서버 콘솔에 출력하려면:

```bash
MESSAGE_POLISHING_TRACE=1 python web_server.py --host 127.0.0.1 --port 8000
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

## Docker 실행

Docker 이미지는 Vite 프론트엔드를 먼저 빌드한 뒤, Python 백엔드가 `/api`와 정적 프론트 파일을 함께 서빙합니다.

`.env` 파일에 최소한 다음 값을 설정하세요.

```bash
UPSTAGE_API_KEY=your-api-key
```

컨테이너 실행:

```bash
docker compose up --build
```

브라우저에서 접속:

```text
http://127.0.0.1:8000
```

포트를 바꾸려면 `.env`나 shell에 `MESSAGE_POLISHING_PORT`를 설정하면 됩니다.

```bash
MESSAGE_POLISHING_PORT=8080 docker compose up --build
```

## 구조

```text
.
├── agents/                 # LangGraph agent 구현
├── frontend/               # Vite React frontend
├── Dockerfile              # frontend build + backend runtime 단일 이미지
├── docker-compose.yml      # 로컬 Docker 실행 구성
├── web_server.py           # API 서버와 frontend/dist 정적 파일 서빙
├── graph.py                # workflow graph
├── llm.py                  # LLM 호출, JSON schema validation/repair
├── prompts.py              # agent prompt/output rules
└── schemas.py              # Pydantic input/output/state schema
```

## 경로

- `/`: Guide 페이지
- `/polish`: 메시지 다듬기 페이지
- 백엔드 API: `POST http://127.0.0.1:8000/api/polish`

API 상세는 [API_SPEC.md](./API_SPEC.md)를 참고하세요.
