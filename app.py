import streamlit as st
from google import genai
from google.genai import types
import os

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="TV 광고 위치 분석기", layout="wide")
st.title("📺 TV 광고 편성 위치 분석 전문 AI")
st.write("광고 탐지 결과 및 편성표 엑셀 파일을 업로드하여 정확한 위치(전/중/후)를 판정합니다.")

# 2. API 키 설정 (Streamlit 클라우드 배포 시 Secrets 설정 필요)
# 로컬 테스트 시에는 환경 변수나 직접 입력을 사용할 수 있습니다.
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

client = genai.Client(api_key=api_key)

# 3. 파일 업로드 섹션
st.subheader("1. 분석 파일 업로드")
uploaded_files = st.file_uploader(
    "3개 파일(광고 탐지, 광고 포함 편성표, 광고 제외 편성표)을 한꺼번에 선택해주세요.", 
    accept_multiple_files=True, 
    type=['xlsx', 'csv']
)

# 4. 분석 실행 버튼
if st.button("AI 분석 시작"):
    if len(uploaded_files) >= 3:
        with st.spinner("AI가 데이터를 매칭하고 분석 중입니다. 잠시만 기다려주세요..."):
            try:
                # 파일 데이터를 AI에게 전달할 준비
                file_parts = []
                for file in uploaded_files:
                    file_bytes = file.read()
                    file_parts.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=file.type)
                    )

                # AI Studio에서 가져온 핵심 분석 프롬프트
                model = "gemini-2.0-flash-exp" # 최신 모델로 유지
                
                # 프롬프트 구성 (사용자님이 작성하신 로직 유지)
                prompt_text = """당신은 TV 광고 편성 위치(전/중/후) 분석 전문가입니다. 
                업로드된 파일들을 결합하여 각 광고의 정확한 위치를 판정하고 분석 보고서를 작성하세요."""
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt_text)] + file_parts
                    )
                ]

                # 코드 실행 도구 및 검색 도구 설정
                tools = [
                    types.Tool(code_execution=types.ToolCodeExecution),
                    types.Tool(googleSearch=types.GoogleSearch()),
                ]

                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    tools=tools,
                )

                # 결과 출력 영역
                result_placeholder = st.empty()
                full_response = ""

                # 스트리밍 출력
                for chunk in client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if chunk.text:
                        full_response += chunk.text
                        result_placeholder.markdown(full_response)
                
                st.success("분석이 완료되었습니다!")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.warning("분석을 위해 최소 3개의 파일을 업로드해야 합니다.")
