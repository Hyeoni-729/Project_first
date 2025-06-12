from pydantic import BaseModel
from typing import Dict, Optional
import hashlib
import uuid
from datetime import datetime, timedelta

# 사용자 모델
class User(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    created_at: datetime

# 메모리 저장소
users_db: Dict[str, User] = {}
sessions_db: Dict[str, str] = {}  # session_id -> username

def hash_password(password: str) -> str:
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == password_hash

def create_user(username: str, email: str, password: str) -> Dict:
    """
    새 사용자 생성
    """
    # 사용자명 중복 검사
    for user in users_db.values():
        if user.username == username:
            return {
                "success": False,
                "message": "❌ 이미 존재하는 사용자명입니다",
                "user": None
            }
    
    # 이메일 중복 검사
    for user in users_db.values():
        if user.email == email:
            return {
                "success": False,
                "message": "❌ 이미 존재하는 이메일입니다",
                "user": None
            }
    
    # 입력 검증
    if not username or not username.strip():
        return {
            "success": False,
            "message": "❌ 사용자명을 입력해주세요",
            "user": None
        }
    
    if not email or not email.strip():
        return {
            "success": False,
            "message": "❌ 이메일을 입력해주세요",
            "user": None
        }
    
    if not password or len(password) < 4:
        return {
            "success": False,
            "message": "❌ 비밀번호는 4자 이상이어야 합니다",
            "user": None
        }
    
    # 새 사용자 생성
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        username=username.strip(),
        email=email.strip(),
        password_hash=hash_password(password),
        created_at=datetime.now()
    )
    
    # 저장
    users_db[user_id] = new_user
    
    return {
        "success": True,
        "message": "✅ 회원가입이 완료되었습니다",
        "user": new_user
    }

def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    사용자 인증
    """
    # 사용자명으로 사용자 찾기
    for user in users_db.values():
        if user.username == username:
            # 비밀번호 확인
            if verify_password(password, user.password_hash):
                return user
            break
    
    return None

def create_session(username: str) -> str:
    """
    세션 생성
    """
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = username
    return session_id

def get_current_user(session_id: str) -> Optional[User]:
    """
    세션 ID로 현재 사용자 조회
    """
    if session_id not in sessions_db:
        return None
    
    username = sessions_db[session_id]
    
    # 사용자명으로 사용자 찾기
    for user in users_db.values():
        if user.username == username:
            return user
    
    return None

def logout_user(session_id: str) -> bool:
    """
    로그아웃 (세션 삭제)
    """
    if session_id in sessions_db:
        del sessions_db[session_id]
        return True
    return False

def get_user_by_username(username: str) -> Optional[User]:
    """
    사용자명으로 사용자 조회
    """
    for user in users_db.values():
        if user.username == username:
            return user
    return None

def get_user_by_email(email: str) -> Optional[User]:
    """
    이메일로 사용자 조회
    """
    for user in users_db.values():
        if user.email == email:
            return user
    return None