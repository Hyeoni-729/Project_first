# 🍳 나만의 레시피 비서 (FastAPI & ChatGPT)

ChatGPT API를 활용하여 레시피를 추천받고, 나만의 레시피를 관리할 수 있는 웹 애플리케이션입니다.

---

## 🚀 프로젝트 소개

FastAPI와 Jinja2 템플릿을 이용해 구현한 **레시피 관리 및 AI 채팅 웹 앱**입니다.

- OpenAI ChatGPT API를 연동하여 사용자 질문에 맞는 요리 레시피를 실시간 추천
- 세션 기반 인증으로 로그인된 사용자만 레시피 생성 및 AI 채팅 이용 가능
- HTML, CSS, JavaScript 기반의 사용자 친화적 UI

---

## 🛠️ 기술 스택

| 구분     | 기술                                |
|--------|-------------------------------------|
| Backend | FastAPI, Uvicorn, Pydantic, Python, Jinja2 |
| Frontend | HTML, CSS, JavaScript               |
| API     | OpenAI ChatGPT                      |
| Auth    | 세션 기반 인증 (쿠키)                  |

---

## 📁 프로젝트 구조

📦 project-root/
┣ 📜 recipe.py # FastAPI 메인 앱, 라우터
┣ 📜 auth.py # 사용자 인증, 세션 관리
┣ 📜 models.py # Pydantic 데이터 모델 정의
┣ 📜 chatgpt_service.py # OpenAI API 연동 서비스
┣ 📂 static/ # CSS, JavaScript 등 정적 파일
┃ ┣ 📜 style.css
┃ ┗ 📜 script.js
┣ 📂 templates/ # HTML 템플릿 파일
┃ ┣ 📜 recipe.html # 레시피 목록 페이지
┃ ┣ 📜 recipe_detail.html # 레시피 상세 페이지
┃ ┣ 📜 chat.html # ChatGPT 채팅 페이지
┃ ┗ 📜 my_recipes.html # 내 레시피 목록 페이지
┗ 📜 README.md

---

## ⚙️ 실행 방법

1. 필요한 라이브러리를 설치합니다:

```(venv)
pip install fastapi uvicorn jinja2 pydantic openai python-jose bcrypt
```

2. FastAPI 서버 실행:

```(venv)
uvicorn recipe:app --reload
```

3. 웹 브라우저에서 접속:

API 서버 (Swagger UI): http://127.0.0.1:8000/docs

메인 페이지: http://127.0.0.1:8000/recipes

---

## 🔑 핵심 기능
### ✅ 사용자 관리
- 회원가입 / 로그인 / 로그아웃

- 세션 기반 인증으로 로그인 상태 유지

### 🍲 레시피 CRUD
- 레시피 생성, 조회, 수정, 삭제

- 자신이 작성한 레시피만 수정 및 삭제 가능

- '내 레시피' 페이지에서 개인 레시피만 모아보기

### 🤖 AI 레시피 상담 (ChatGPT 연동)
- 로그인된 사용자만 AI 채팅 기능 사용 가능

- 요리 관련 질문 시 ChatGPT가 실시간으로 답변 및 레시피 추천

- AI가 추천한 레시피를 저장 가능 ('내 레시피'에 추가)

### 💬 채팅 기록 관리
- 사용자별 질문/답변 기록 확인 가능

- 채팅 기록 전체 삭제 기능