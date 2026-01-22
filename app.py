import streamlit as st
from google import genai
from google.genai import types
import os

# 페이지 설정
st.set_page_config(page_title="TV 광고 분석기", layout="wide")
st.title("📺 TV 광고 편성 위치 분석 AI")

# API 키 설정 (오류 방지 로직 강화)
api_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 API 키가 설정되지 않았습니다. Streamlit Cloud의 Settings -> Secrets에 GEMINI_API_KEY를 등록해주세요.")
    st.stop()

# 클라이언트 생성
client = genai.Client(api_key=api_key)

# 파일 업로드
uploaded_files = st.file_uploader("분석할 엑셀/CSV 파일 3개를 올려주세요", accept_multiple_files=True, type=['xlsx', 'csv'])

if st.button("분석 시작"):
    if len(uploaded_files) >= 3:
        with st.spinner("AI가 데이터를 정밀 분석 중입니다..."):
            try:
                # 파일 처리
                file_parts = []
                for file in uploaded_files:
                    m_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if file.name.endswith('xlsx') else "text/csv"
                    file_parts.append(types.Part.from_bytes(data=file.read(), mime_type=m_type))

                # 모델 설정 (가장 안정적인 1.5-flash 사용)
                model_id = "gemini-1.5-flash" 
                
                prompt = "업로드된 파일들을 분석하여 광고 위치(전/중/후)를 판정해줘. Python Code Execution을 사용해서 계산해."
                
                contents = [
                    types.Content(role="user", parts=[types.Part.from_text(text=prompt)] + file_parts)
                ]

                # 도구 설정
                tools = [types.Tool(code_execution=types.ToolCodeExecution)]

                # 결과 출력
                res_area = st.empty()
                full_text = ""
                
                for chunk in client.models.generate_content_stream(
                    model=model_id,
                    contents=contents,
                    config=types.GenerateContentConfig(tools=tools)
                ):
                    if chunk.text:
                        full_text += chunk.text
                        res_area.markdown(full_text)
                
                st.success("분석이 완료되었습니다!")

            except Exception as e:
                # 에러 메시지를 더 자세히 출력하도록 수정
                st.error(f"분석 중 오류 발생: {e}")
    else:
        st.warning("파일을 3개 이상 업로드해야 분석이 가능합니다.")
