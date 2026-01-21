# services/db_service.py
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 파일 로드 (로컬 환경용)
load_dotenv()

# 환경 변수 가져오기 (로컬 .env 우선, 없으면 st.secrets 확인)
def get_secret(key):
    return os.getenv(key) or (st.secrets[key] if key in st.secrets else None)

SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

# 클라이언트 생성
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("🚨 Supabase URL 또는 Key가 설정되지 않았습니다.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def register_user(nickname, gender):
    """
    새로운 사용자를 DB users 테이블에 등록하고, 생성된 user_id를 반환합니다.
    """
    try:
        user_data = {
            "nickname": nickname,
            "gender": gender,
            "marketing_agree": True # Intro에서 체크했다고 가정
        }
        
        # 1. Insert 하고 방금 생성된 데이터(user_id 포함)를 돌려받음
        response = supabase.table("users").insert(user_data).execute()
        
        # 2. 성공 시 user_id 반환
        if response.data:
            user_id = response.data[0]['user_id']
            return user_id
        return None

    except Exception as e:
        st.error(f"DB 저장 실패: {e}")
        return None


def create_game_session(user_id, final_choice=None, my_persona=None, ideal_preference=None):
    """
    게임 세션을 생성하고 session_id를 반환합니다.
    게임 시작 시 호출하여 session_id를 받고, 게임 종료 시 update로 결과를 채움.
    """
    try:
        session_data = {
            "user_id": user_id,
            "final_choice": final_choice,
            "my_persona": my_persona,
            "ideal_preference": ideal_preference
        }
        
        response = supabase.table("game_sessions").insert(session_data).execute()
        
        if response.data:
            return response.data[0]['session_id']
        return None

    except Exception as e:
        st.error(f"세션 생성 실패: {e}")
        return None


def update_game_session(session_id, final_choice, my_persona, ideal_preference):
    """
    게임 종료 시 세션 결과를 업데이트합니다.
    """
    try:
        update_data = {
            "final_choice": final_choice,
            "my_persona": my_persona,
            "ideal_preference": ideal_preference
        }
        
        response = supabase.table("game_sessions").update(update_data).eq("session_id", session_id).execute()
        return response.data is not None

    except Exception as e:
        st.error(f"세션 업데이트 실패: {e}")
        return False


def save_chat_log(session_id, partner_type, chat_history, turn_count):
    """
    각 라운드(파트너)별 채팅 로그를 저장합니다.
    partner_type: 'EMOTIONAL', 'LOGICAL', 'TOUGH'
    chat_history: OpenAI API 포맷의 메시지 리스트 (system 제외 권장)
    turn_count: 대화 턴 수
    """
    try:
        # system 메시지 제외한 대화만 저장
        filtered_history = [msg for msg in chat_history if msg["role"] != "system"]
        
        log_data = {
            "session_id": session_id,
            "partner_type": partner_type,
            "chat_history": filtered_history,
            "turn_count": turn_count
        }
        
        response = supabase.table("chat_logs").insert(log_data).execute()
        
        if response.data:
            return response.data[0]['log_id']
        return None

    except Exception as e:
        st.error(f"채팅 로그 저장 실패: {e}")
        return None


def save_analysis_result(session_id, analysis):
    """
    LLM 대화 분석 결과를 analysis_results 테이블에 저장합니다.
    
    Args:
        session_id: 게임 세션 ID
        analysis: LLM 분석 결과 dict (my_persona, compatibility, insights, summary)
    
    Returns:
        analysis_id: 저장된 분석 결과 ID (실패 시 None)
    """
    try:
        my_persona = analysis.get("my_persona", {})
        compatibility = analysis.get("compatibility", {})
        insights = analysis.get("insights", {})
        
        analysis_data = {
            "session_id": session_id,
            
            # 사용자 연애 스타일
            "style": my_persona.get("style"),
            "user_type": my_persona.get("type"),
            "keywords": my_persona.get("keywords", []),
            "strength": my_persona.get("strength"),
            "weakness": my_persona.get("weakness"),
            
            # 호환성 분석
            "best_match": compatibility.get("best_match"),
            "best_reason": compatibility.get("best_reason"),
            "similar_style": compatibility.get("similar_style"),
            "similar_chemistry": compatibility.get("similar_chemistry"),
            "opposite_style": compatibility.get("opposite_style"),
            "opposite_chemistry": compatibility.get("opposite_chemistry"),
            
            # 인사이트
            "positive": insights.get("positive"),
            "improvement": insights.get("improvement"),
            "dating_tip": insights.get("dating_tip"),
            "warning": insights.get("warning"),
            
            # 전체 요약
            "summary": analysis.get("summary")
        }
        
        response = supabase.table("analysis_results").insert(analysis_data).execute()
        
        if response.data:
            return response.data[0]['analysis_id']
        return None

    except Exception as e:
        st.error(f"분석 결과 저장 실패: {e}")
        return None