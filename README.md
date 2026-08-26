# AI Summary

## 담당 역할 및 기여도

- **백엔드**
  - Python/FastAPI 기반 서버 및 API 구현
  - 영상 처리 및 결과 조회를 위한 Router 구성

- **영상 처리 파이프라인**
  - YouTube URL을 입력받아 영상 및 음원 다운로드
  - YouTube 자막 추출 및 파싱
  - 자막이 없는 경우 STT를 활용한 음성 → 텍스트 변환

- **AI 요약 및 번역 기능**
  - 추출된 영상 스크립트를 기반으로 AI 요약
  - 영상 챕터 및 자막 유무에 따른 요약 처리
  - 요약 결과 한국어 번역

- **비동기 작업 처리**
  - Celery와 Redis를 활용해 영상 다운로드, STT, 요약 등의 작업을 비동기로 처리
  - 작업 진행 상태를 DB에 저장하여 처리 상태 확인 가능하도록 구현

- **DB 설계 및 관리**
  - 초기 Railway PostgreSQL 연동을 시도
  - 개발 및 실행 환경의 제약을 고려하여 **SQLite로 전환**
  - 영상 처리 상태 및 요약 결과 관리

- **결과물 생성**
  - AI 요약 결과를 Markdown 및 PDF 형태로 생성
  - 영상 스크립트, 요약 내용 등의 결과 데이터 관리

- **배포 및 외부 접근 환경 구축**
  - Railway를 활용한 배포 환경 구축을 시도
  - 실행 환경상의 문제를 해결하기 위해 **ngrok 기반 외부 접근 방식으로 전환**

## 기술 스택

### Backend
- Python
- FastAPI
- Uvicorn
- Jinja2

### AI / 영상 처리
- Google Gemini API
- OpenAI API
- yt-dlp
- STT
- YouTube 자막 파싱
- AI 기반 요약 및 번역

### 비동기 처리
- Celery
- Redis

### Database
- SQLite
- PostgreSQL *(Railway 연동 시도 후 SQLite로 전환)*

### 결과물 생성
- Markdown
- PDF
- pdfkit

### Deployment / Network
- Railway *(배포 시도)*
- ngrok *(최종 외부 접근 환경)*

## 

> YouTube 영상의 다운로드부터 자막/STT 변환, AI 요약·번역, PDF 생성까지 이어지는 **전체 비동기 처리 파이프라인을 백엔드에서 구현**하고, Railway 및 PostgreSQL 연동 과정에서 발생한 환경적 제약을 해결하기 위해 SQLite와 ngrok 기반의 실행 환경으로 전환했습니다.
