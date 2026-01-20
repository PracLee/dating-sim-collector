import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

print("--- [1단계] 진단 시작 ---")

# 1. .env 파일 로드 시도
print("--- [2단계] .env 파일 로딩 중...")
is_loaded = load_dotenv()
print(f"    > .env 로드 결과: {is_loaded}")

# 2. 키 확인
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url:
    print("❌ [오류] SUPABASE_URL을 찾을 수 없습니다.")
    print("    > 힌트: .env 파일이 debug_db.py와 같은 폴더에 있나요?")
    print("    > 힌트: .env 파일 안에 SUPABASE_URL=... 이라고 적혀 있나요?")
    sys.exit()

if not key:
    print("❌ [오류] SUPABASE_KEY를 찾을 수 없습니다.")
    sys.exit()

print(f"    > URL 확인: {url[:10]}... (OK)")
print(f"    > KEY 확인: {key[:10]}... (OK)")

# 3. 클라이언트 생성
print("--- [3단계] Supabase 클라이언트 연결 중...")
try:
    supabase: Client = create_client(url, key)
    print("    > 클라이언트 객체 생성 성공!")
except Exception as e:
    print(f"❌ [오류] 클라이언트 생성 실패: {e}")
    sys.exit()

# 4. 데이터 삽입 테스트
print("--- [4단계] 데이터 삽입(Insert) 시도 중...")
try:
    test_data = {
        "nickname": "Debug_Bot",
        "gender": "M",
        "marketing_agree": True
    }
    # users 테이블에 데이터 넣기
    response = supabase.table("users").insert(test_data).execute()
    
    print("🎉 [성공] 데이터가 정상적으로 들어갔습니다!")
    print(f"    > 응답 데이터: {response.data}")

except Exception as e:
    print(f"🔥 [치명적 오류] 데이터 삽입 실패: {e}")
    print("    > 힌트 1: Supabase 대시보드에서 'RLS'를 끄셨나요? (Table Editor > users > RLS Disabled)")
    print("    > 힌트 2: 테이블 이름이 'users'가 맞나요?")