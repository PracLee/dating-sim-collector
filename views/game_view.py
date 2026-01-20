import streamlit as st
import time
from services.llm_service import get_ai_response
from config.prompts import get_system_prompt, get_persona_name, get_first_greeting

def show_game():
    st.title(f"{st.session_state.get('nickname', '익명')}님의 소개팅 💕")
    
    # 0. 기본 설정값 가져오기
    user_gender = st.session_state.get("gender", "F") # 기본값 F
    
    # 세션 상태 초기화
    if "current_round" not in st.session_state:
        st.session_state["current_round"] = 1
        
    current_round = st.session_state["current_round"]
    
    # 라운드별 설정
    ROUND_TYPES = {1: "EMOTIONAL", 2: "LOGICAL", 3: "TOUGH"}
    current_type = ROUND_TYPES[current_round]
    
    # 이름 가져오기
    persona_name = get_persona_name(current_type, user_gender)
    
    ROUND_LABELS = {
        1: f"1라운드: {persona_name} (공감형 🥺)",
        2: f"2라운드: {persona_name} (이성형 🤓)",
        3: f"3라운드: {persona_name} (직진형 😉)"
    }

    # 대화 히스토리 초기화 (앱 켜질 때 or 라운드 변경 직후 메시지가 비어있을 때 contents가 비어있으면 초기화)
    if "messages" not in st.session_state:
        # 프롬프트 생성
        sys_prompt = get_system_prompt(current_type, user_gender)
        # 첫 인사 생성
        greeting = get_first_greeting(current_type, user_gender)
        
        st.session_state["messages"] = [
            {"role": "system", "content": sys_prompt},
            {"role": "assistant", "content": greeting}
        ]

    # 2. UI 표시
    # 진행 상황 (Progress Bar)
    st.info(f"현재 진행 중: **{ROUND_LABELS[current_round]}**")
    st.progress(current_round / 3)

    # 채팅 기록 표시
    for msg in st.session_state["messages"]:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 3. 사용자 입력 처리
    if prompt := st.chat_input("메시지를 입력하세요..."):
        # 사용자 메시지 UI 표시 및 저장
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # AI 응답 생성
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("상대방이 입력 중입니다..."):
                ai_response = get_ai_response(st.session_state["messages"])
                
            # 타자기 효과
            for chunk in ai_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        # AI 메시지 저장
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

    # 4. 라운드 종료 / 넘기기 (임시 버튼)
    st.divider()
    st.divider()
    if st.button("다음 라운드로 넘어가기 (대화 종료)"):
        # 현재 대화 로그 저장 (history)
        if "history" not in st.session_state:
            st.session_state["history"] = []
            
        st.session_state["history"].append({
            "round": current_round,
            "persona": current_type,
            "messages": st.session_state["messages"]
        })
        
        # 다음 라운드 진행 판단
        if current_round < 3:
            st.session_state["current_round"] += 1
            next_round = st.session_state["current_round"]
            
            # 다음 라운드 정보 준비
            next_type = ROUND_TYPES[next_round]
            next_name = get_persona_name(next_type, user_gender)
            
            # 메시지함 리셋 (새로운 페르소나 적용)
            new_sys_prompt = get_system_prompt(next_type, user_gender)
            new_greeting = get_first_greeting(next_type, user_gender)
            
            st.session_state["messages"] = [
                {"role": "system", "content": new_sys_prompt},
                {"role": "assistant", "content": new_greeting}
            ]
            
            st.toast(f"{next_name}님과의 대화가 시작됩니다!")
            time.sleep(1)
            st.rerun()
        else:
            # 모든 라운드 종료 -> 결과 화면
            st.success("모든 소개팅이 종료되었습니다! 결과를 분석합니다.")
            time.sleep(1)
            st.session_state["step"] = "result"
            st.rerun()
