from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

# 회원가입 요청 모델
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "홍길동",
                "email": "hong@example.com",
                "password": "password123"
            }
        }

# 로그인 요청 모델
class UserLogin(BaseModel):
    username: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "홍길동",
                "password": "password123"
            }
        }

# 사용자 응답 모델
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "12345-abcde-67890",
                "username": "홍길동",
                "email": "hong@example.com"
            }
        }

# 일반적인 응답 모델
class MessageResponse(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "작업이 완료되었습니다"
            }
        }

# ChatGPT 요청 모델
class ChatRequest(BaseModel):
    question: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "김치찌개 레시피를 알려주세요"
            }
        }

# ChatGPT 응답 모델
class ChatResponse(BaseModel):
    question: str
    answer: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "김치찌개 레시피를 알려주세요",
                "answer": "김치찌개 레시피입니다..."
            }
        }

# 대화형 ChatGPT 요청 모델
class ConversationRequest(BaseModel):
    messages: List[Dict[str, str]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "김치찌개 만드는 법 알려주세요"},
                    {"role": "assistant", "content": "김치찌개 레시피를 알려드리겠습니다..."},
                    {"role": "user", "content": "여기서 김치는 어떤 걸 써야 하나요?"}
                ]
            }
        }

# 채팅 기록 응답 모델
class ChatHistoryResponse(BaseModel):
    user_id: str
    username: str
    total_chats: int
    history: List[Dict[str, str]]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "12345-abcde-67890",
                "username": "홍길동", 
                "total_chats": 5,
                "history": [
                    {
                        "question": "김치찌개 레시피 알려주세요",
                        "answer": "김치찌개 만드는 방법...",
                        "timestamp": "2024-01-01T12:00:00"
                    }
                ]
            }
        }