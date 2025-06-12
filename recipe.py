from fastapi import FastAPI, Request, Form, HTTPException, Cookie, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from models import UserCreate, UserLogin, UserResponse
from auth import create_user, authenticate_user, create_session, get_current_user, logout_user
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime
from chatgpt_service import chatgpt_service
from models import ChatRequest, ChatResponse
import html
import re

app = FastAPI()

# 레시피 저장용 (고유 ID 시스템 사용)
recipes_db: Dict[str, Dict[str, Any]] = {}
chat_history_db: Dict[str, List[Dict[str, str]]] = {}

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 폴더 자동 생성
import os
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 정적 파일 사용 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML 템플릿 경로 설정
templates = Jinja2Templates(directory="templates")

# 인증 의존성 함수
async def get_authenticated_user(session_id: Optional[str] = Cookie(None)):
    """로그인된 사용자만 접근 가능하도록 하는 의존성"""
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="🚫 로그인이 필요합니다"
        )
    
    user = get_current_user(session_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="🚫 유효하지 않은 세션입니다. 다시 로그인해주세요"
        )
    
    return user

# 텍스트 정리 함수
def clean_text(text: str) -> str:
    """텍스트에서 HTML 태그 제거 및 특수문자 처리"""
    if not text:
        return ""
    
    # HTML 엔티티 디코딩
    text = html.unescape(text)
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 연속된 공백을 하나로 변경
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text

# 입력 검증 함수
def validate_recipe_input(title: str, content: str) -> None:
    """레시피 입력 데이터 검증"""
    # 텍스트 정리
    title = clean_text(title) if title else ""
    content = clean_text(content) if content else ""
    
    if not title:
        raise HTTPException(
            status_code=400,
            detail="❌ 레시피 제목을 입력해주세요"
        )
    
    if not content:
        raise HTTPException(
            status_code=400,
            detail="❌ 레시피 내용을 입력해주세요"
        )
    
    if len(title) > 200:  # 제한 늘림
        raise HTTPException(
            status_code=400,
            detail="❌ 제목은 200자 이내로 입력해주세요"
        )
    
    if len(content) > 10000:  # 긴 레시피도 허용
        raise HTTPException(
            status_code=400,
            detail="❌ 내용은 10,000자 이내로 입력해주세요"
        )

# ==================== 인증 관련 엔드포인트 ====================

@app.post("/register")
async def signup(userdata: UserCreate):
    """회원가입 처리"""
    result = create_user(
        username=userdata.username,
        email=userdata.email,
        password=userdata.password
    )

    if not result["success"]:
        raise HTTPException(
            status_code=400, 
            detail=result["message"]
        )
    
    user_response = UserResponse(
        id=result["user"].id,
        username=result["user"].username,
        email=result["user"].email
    )
    
    return {
        "message": "🎉 회원가입이 완료되었습니다!",
        "user": user_response
    }

@app.post("/login")
async def login(user_data: UserLogin):
    """로그인 처리"""
    user = authenticate_user(user_data.username, user_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="❌ 사용자명 또는 비밀번호가 올바르지 않습니다"
        )

    session_id = create_session(user_data.username)

    response = JSONResponse({
        "message": "🎉 로그인 성공!",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })

    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=3600
    )

    return response

@app.get("/me")
async def get_my_info(current_user = Depends(get_authenticated_user)):
    """현재 로그인한 사용자 정보 보기"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email
    )

@app.post("/logout")
async def logout(session_id: Optional[str] = Cookie(None)):
    """로그아웃 처리"""
    if session_id:
        logout_user(session_id)

    response = JSONResponse({"message": "👋 로그아웃되었습니다"})
    response.delete_cookie("session_id")

    return response

# ==================== 레시피 관련 엔드포인트 ====================

@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    """메인 홈페이지"""
    return templates.TemplateResponse("recipe.html", {"request": request})

@app.get("/recipes", response_class=HTMLResponse)
def get_recipes_list(request: Request):
    """전체 레시피 목록 조회"""
    sorted_recipes = sorted(
        recipes_db.items(), 
        key=lambda x: x[1]["created_at"], 
        reverse=True
    )
    
    recipes_list = [
        {
            "id": recipe_id,
            "title": recipe_data["title"],
            "content": recipe_data["content"][:100] + "..." if len(recipe_data["content"]) > 100 else recipe_data["content"],
            "author": recipe_data["author"],
            "created_at": recipe_data["created_at"],
            "is_from_chatgpt": recipe_data.get("is_from_chatgpt", False)
        }
        for recipe_id, recipe_data in sorted_recipes
    ]
    
    return templates.TemplateResponse(
        "recipe.html", 
        {"request": request, "recipes": recipes_list}
    )


@app.post("/recipes/from-chat")
async def create_recipe_from_chat(
    title: str = Form(...), 
    content: str = Form(...),
    original_question: str = Form(default=""),
    current_user = Depends(get_authenticated_user)
):
    """ChatGPT 상담 결과를 레시피로 저장"""
    try:
        # 텍스트 정리
        title = clean_text(title)
        content = clean_text(content)
        
        # 빈 값 처리
        if not title:
            title = f"ChatGPT 레시피 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        if not content:
            raise HTTPException(
                status_code=400,
                detail="❌ 저장할 레시피 내용이 없습니다"
            )
        
        # 입력 검증
        validate_recipe_input(title, content)
        
        # 고유 ID 생성
        recipe_id = str(uuid.uuid4())
        
        # 레시피 저장
        recipes_db[recipe_id] = {
            "title": title,
            "content": content,
            "author": current_user.username,
            "user_id": current_user.id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "is_from_chatgpt": True,
            "original_question": clean_text(original_question) if original_question else ""
        }
        
        return JSONResponse({
            "success": True,
            "message": "✅ ChatGPT 레시피가 성공적으로 저장되었습니다!",
            "recipe_id": recipe_id,
            "redirect_url": f"/recipes/{recipe_id}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({
            "success": False,
            "message": f"❌ 레시피 저장 중 오류가 발생했습니다: {str(e)}"
        }, status_code=500)

@app.get("/recipes/{recipe_id}", response_class=HTMLResponse)
def get_recipe_detail(
    recipe_id: str, 
    request: Request, 
    error: Optional[str] = None, 
    session_id: Optional[str] = Cookie(None)
):
    """개별 레시피 상세 조회"""
    if recipe_id not in recipes_db:
        raise HTTPException(
            status_code=404, 
            detail="❌ 레시피를 찾을 수 없습니다"
        )
    
    recipe = recipes_db[recipe_id]
    recipe_with_id = {**recipe, "id": recipe_id}
    
    # 현재 사용자 정보 확인
    current_user = None
    can_edit = False
    
    if session_id:
        current_user = get_current_user(session_id)
        if current_user and recipe["user_id"] == current_user.id:
            can_edit = True
    
    error_message = None
    if error:
        if error == "permission_denied":
            error_message = "자신이 작성한 레시피만 수정할 수 있습니다"
        else:
            error_message = error.replace("_", " ")
    
    return templates.TemplateResponse(
        "recipe_detail.html", 
        {
            "request": request, 
            "recipe": recipe_with_id,
            "current_user": current_user,
            "can_edit": can_edit,
            "error_message": error_message
        }
    )

@app.post("/recipes/{recipe_id}/edit")
def update_recipe(
    recipe_id: str,
    title: str = Form(...), 
    content: str = Form(...),
    current_user = Depends(get_authenticated_user)
):
    """레시피 수정 (작성자만 가능)"""
    if recipe_id not in recipes_db:
        raise HTTPException(
            status_code=404, 
            detail="❌ 레시피를 찾을 수 없습니다"
        )
    
    recipe = recipes_db[recipe_id]
    
    # 권한 검증 - 작성자가 아닌 경우 에러 메시지와 함께 상세 페이지로 리다이렉트
    if recipe["user_id"] != current_user.id:
        return RedirectResponse(
            f"/recipes/{recipe_id}?error=permission_denied", 
            status_code=303
        )
    
    try:
        # 텍스트 정리 및 검증
        title = clean_text(title)
        content = clean_text(content)
        validate_recipe_input(title, content)
        
        # 레시피 업데이트
        recipes_db[recipe_id].update({
            "title": title,
            "content": content,
            "updated_at": datetime.now()
        })
    
        return RedirectResponse(f"/recipes/{recipe_id}", status_code=303)

    except HTTPException as e:
        # 입력 검증 에러도 URL 파라미터로 전달
        error_message = e.detail.replace("❌ ", "").replace(" ", "_")
        return RedirectResponse(
            f"/recipes/{recipe_id}?error={error_message}", 
            status_code=303
        )

@app.post("/recipes/{recipe_id}/delete")
def delete_recipe(
    recipe_id: str,
    current_user = Depends(get_authenticated_user)
):
    """레시피 삭제 (작성자만 가능)"""
    if recipe_id not in recipes_db:
        raise HTTPException(
            status_code=404, 
            detail="❌ 레시피를 찾을 수 없습니다"
        )
    
    recipe = recipes_db[recipe_id]
    
    if recipe["user_id"] != current_user.id:
        return RedirectResponse(
            f"/recipes/{recipe_id}?error=permission_denied", 
            status_code=303
        )
    
    del recipes_db[recipe_id]
    
    return RedirectResponse("/recipes", status_code=303)

# ==================== ChatGPT API 엔드포인트 ====================

@app.post("/chat", response_model=ChatResponse)
async def chat_with_gpt(
    chat_request: ChatRequest,
    current_user = Depends(get_authenticated_user)
):
    """ChatGPT와 요리/레시피 상담"""
    try:
        # ChatGPT 서비스 호출
        answer = await chatgpt_service.get_recipe_advice(chat_request.question)

        # 채팅 기록 저장
        user_id = current_user.id
        if user_id not in chat_history_db:
            chat_history_db[user_id] = []
        
        chat_entry = {
            "question": chat_request.question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        chat_history_db[user_id].append(chat_entry)

        return ChatResponse(
            question=chat_request.question,
            answer=answer
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ChatGPT 서비스 오류: {str(e)}"
        )

@app.get("/chat-page", response_class=HTMLResponse)
def chat_page(request: Request, current_user = Depends(get_authenticated_user)):
    """ChatGPT 채팅 페이지"""
    return templates.TemplateResponse(
        "chat.html", 
        {
            "request": request, 
            "user": current_user
        }
    )

@app.get("/chat/history")
async def get_chat_history(current_user = Depends(get_authenticated_user)):
    """사용자별 채팅 기록 조회"""
    user_history = chat_history_db.get(current_user.id, [])
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_chats": len(user_history),
        "history": user_history
    }

@app.delete("/chat/history")
async def clear_chat_history(current_user = Depends(get_authenticated_user)):
    """사용자 채팅 기록 삭제"""
    user_id = current_user.id
    if user_id in chat_history_db:
        del chat_history_db[user_id]
    
    return {"message": "채팅 기록이 삭제되었습니다."}

@app.get("/my-recipes", response_class=HTMLResponse)
def get_my_recipes(request: Request, current_user = Depends(get_authenticated_user)):
    """현재 사용자가 작성한 레시피만 조회"""
    # 현재 사용자가 작성한 레시피만 필터링
    user_recipes = {
        recipe_id: recipe_data 
        for recipe_id, recipe_data in recipes_db.items() 
        if recipe_data["user_id"] == current_user.id
    }
    
    # 최신순으로 정렬
    sorted_recipes = sorted(
        user_recipes.items(), 
        key=lambda x: x[1]["created_at"], 
        reverse=True
    )
    
    # 템플릿에 전달할 데이터 준비
    my_recipes_list = [
        {
            "id": recipe_id,
            "title": recipe_data["title"],
            "content": recipe_data["content"][:100] + "..." if len(recipe_data["content"]) > 100 else recipe_data["content"],
            "author": recipe_data["author"],
            "created_at": recipe_data["created_at"],
            "updated_at": recipe_data["updated_at"],
            "is_from_chatgpt": recipe_data.get("is_from_chatgpt", False),
            "original_question": recipe_data.get("original_question", "")
        }
        for recipe_id, recipe_data in sorted_recipes
    ]
    
    return templates.TemplateResponse(
        "my_recipes.html", 
        {
            "request": request, 
            "user": current_user,
            "recipes": my_recipes_list
        }
    )