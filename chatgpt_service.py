import httpx
from typing import Dict, Any, List
from fastapi import HTTPException

# ChatGPT 프록시 URL
CHATGPT_PROXY_URL = "https://dev.wenivops.co.kr/services/openai-api"

class ChatGPTService:
    def __init__(self):
        self.proxy_url = CHATGPT_PROXY_URL
    
    async def get_recipe_advice(self, question: str) -> str:
        """ChatGPT API를 통해 요리/레시피 조언 받기"""
        
        # 질문에 "요리"나 "레시피" 관련 키워드가 없으면 제한
        if not self._is_cooking_related(question):
            raise HTTPException(
                status_code=400, 
                detail="요리나 레시피 관련 질문만 가능합니다."
            )
        
        # 요리/레시피 관련 시스템 프롬프트 추가
        messages = [
            {
                "role": "system", 
                "content": "당신은 요리 전문가입니다. 요리 레시피, 재료, 조리법, 맛에 대한 질문에만 답변해주세요. 친근하고 자세하게 설명해주세요."
            },
            {
                "role": "user", 
                "content": question
            }
        ]
        
        try:
            # 비동기 HTTP 클라이언트로 API 요청
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.proxy_url,
                    json=messages,  # 메시지 배열을 JSON으로 전송
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                # 응답 상태 확인
                response.raise_for_status()
                
                # JSON 응답 파싱
                data = response.json()
                
                # OpenAI API 응답 형식에서 답변 추출
                if "choices" in data and len(data["choices"]) > 0:
                    answer = data["choices"][0]["message"]["content"]
                    return answer
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="ChatGPT로부터 올바른 응답을 받지 못했습니다."
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="ChatGPT 서비스 응답 시간이 초과되었습니다."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=500,
                detail=f"ChatGPT API 오류: {e.response.status_code}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"ChatGPT 서비스 오류: {str(e)}"
            )
    
    async def get_general_chat_response(self, messages: List[Dict[str, str]]) -> str:
        """일반 채팅 응답 받기 (메시지 히스토리 포함)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.proxy_url,
                    json=messages,
                    headers={"Content-Type": "application/json"},
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="ChatGPT로부터 올바른 응답을 받지 못했습니다."
                    )
                    
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="ChatGPT 서비스 응답 시간이 초과되었습니다."
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=500,
                detail=f"ChatGPT API 오류: {e.response.status_code}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"ChatGPT 서비스 오류: {str(e)}"
            )
    
    def _is_cooking_related(self, question: str) -> bool:
        """요리/레시피 관련 질문인지 확인"""
        cooking_keywords = [
            "요리", "레시피", "음식", "조리", "맛", "재료", "식재료",
            "김치", "찌개", "국", "밥", "면", "고기", "야채", "채소",
            "만들기", "끓이기", "볶기", "굽기", "삶기", "튀기기",
            "간장", "설탕", "소금", "후추", "마늘", "양파", "생강",
            "식당", "맛집", "메뉴", "요리법", "쿠킹", "베이킹",
            "cake", "cook", "recipe", "food", "dish"
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in cooking_keywords)

# ChatGPT 서비스 인스턴스
chatgpt_service = ChatGPTService()