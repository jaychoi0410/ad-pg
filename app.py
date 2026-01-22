import streamlit as st
from google import genai
from google.genai import types
import os

# 페이지 설정
st.set_page_config(page_title="TV 광고 편성 위치 분석기", layout="wide")
st.title("📺 TV 광고 편성 위치 분석 전문 AI")
st.info("광고 탐지 결과, 포함 편성표, 제외 편성표 3개 파일을 업로드해 주세요.")

# API 키 설정 (Streamlit Secrets용)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("API 키가 설정되지 않았습니다. Streamlit Settings -> Secrets에 GEMINI_API_KEY를 등록하세요.")
    st.stop()

client = genai.Client(api_key=api_key)

# 파일 업로드 섹션
uploaded_files = st.file_uploader(
    "엑셀 또는 CSV 파일을 업로드하세요 (3개 이상)", 
    accept_multiple_files=True, 
    type=['xlsx', 'csv']
)

if st.button("AI 분석 시작"):
    if len(uploaded_files) >= 3:
        with st.spinner("AI가 고도의 분석(Thinking)을 수행 중입니다. 잠시만 기다려 주세요..."):
            try:
                # 파일 데이터를 AI 전송용 Part로 변환
                file_parts = []
                for file in uploaded_files:
                    file_bytes = file.read()
                    # MIME 타입 설정
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file.name.endswith('xlsx') else "text/csv"
                    file_parts.append(
                        types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                    )

                # AI Studio 로직 반영
                model = "gemini-1.5-flash-latest" # 현재 가장 안정적인 최신 모델
                
                prompt_text = """당신은 TV 광고 편성 위치(전/중/후) 분석 전문가입니다. 업로드된 3개 파일을 결합하여 각 광고의 정확한 위치를 판정하세요.
                반드시 Python Code Execution을 활용하여 데이터의 시간과 텍스트를 정밀하게 매칭하고 분석 보고서를 작성하세요."""
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt_text)] + file_parts
                    )
                ]

                # 도구 설정 (코드 실행 및 검색)
                tools = [
                    types.Tool(code_execution=types.ToolCodeExecution),
                    types.Tool(google_search=types.GoogleSearch()),
                ]

                generate_content_config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_level="HIGH"),
                    tools=tools,
                )

                # 스트리밍 결과 출력
                response_container = st.empty()
                full_text = ""
                
                for chunk in client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                ):
                    # 텍스트 파트 추출 및 출력
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        for part in chunk.candidates[0].content.parts:
                            if part.text:
                                full_text += part.text
                                response_container.markdown(full_text)
                
                st.success("분석 완료!")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생: {e}")
    else:

        st.warning("분석을 위해 최소 3개의 파일을 업로드해야 합니다.")

