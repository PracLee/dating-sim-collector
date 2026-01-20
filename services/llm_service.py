from openai import OpenAI
import streamlit as st
from config.settings import OPENAI_API_KEY, OPENAI_MODEL

# 클라이언트 초기화
if not OPENAI_API_KEY:
    # st.secrets에서 시도 (Streamlit Cloud 배포용)
    if "OPENAI_API_KEY" in st.secrets:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client = None
else:
    client = OpenAI(api_key=OPENAI_API_KEY)

import json

def get_ai_response(messages):
    """
    OpenAI API를 통해 챗봇 응답을 받아옵니다.
    messages: game_view에서 관리하는 대화 내역 리스트 (System Prompt 포함)
    Returns: dict {"response": str, "score": int}
    """
    if not client:
        return {"response": "🚨 API Key가 설정되지 않았습니다.", "score": 0}

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"} # JSON 모드 강제
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"response": f"🚨 오류 발생: {str(e)}", "score": 0}


def analyze_conversation(history):
    """
    대화 기록을 분석하여 사용자의 연애 성향을 파악합니다.
    history: 각 라운드별 대화 기록 리스트 [{"round": 1, "persona": "EMOTIONAL", "messages": [...], "final_score": 70}, ...]
    Returns: dict (my_persona, ideal_preference, summary)
    """
    from config.prompts import get_analysis_prompt
    
    if not client:
        return {"error": "API Key가 설정되지 않았습니다."}

    # 대화 내용을 텍스트로 정리
    conversation_text = ""
    for entry in history:
        round_num = entry.get("round", "?")
        persona = entry.get("persona", "UNKNOWN")
        score = entry.get("final_score", "N/A")
        messages = entry.get("messages", [])
        
        conversation_text += f"\n\n### 라운드 {round_num}: {persona} 타입 (최종 호감도: {score})\n"
        for msg in messages:
            if msg["role"] == "user":
                conversation_text += f"[USER]: {msg['content']}\n"
            elif msg["role"] == "assistant":
                conversation_text += f"[AI]: {msg['content']}\n"

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": get_analysis_prompt()},
                {"role": "user", "content": f"다음 대화 기록을 분석해줘:\n{conversation_text}"}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"error": f"분석 실패: {str(e)}"}
