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