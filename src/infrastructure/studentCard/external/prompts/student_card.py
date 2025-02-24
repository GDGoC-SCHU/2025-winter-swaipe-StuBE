from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()

# 프롬프트 최적화
SYSTEM_TEMPLATE = """
당신은 학생증 이미지를 분석하여 정확한 학생 정보를 추출하는 전문가입니다.
이미지에서 다음 정보를 찾아 정확하게 추출해주세요.

필수 정보:
1. 이름 (2-3글자 한글)
2. 학과 (XX학과 형식)
3. 학년 (1-4 사이 숫자)

주의사항:
- 이름은 반드시 한글이어야 합니다
- 학과명은 반드시 '학과'로 끝나야 합니다
- 학년은 1-4 사이의 숫자여야 합니다
- 불확실한 정보는 빈 값으로 남겨두세요

이전 분석 사례:
{chat_history}

{format_instructions}
"""

student_card_prompt = (
    ChatPromptTemplate.from_messages(
        [("system", SYSTEM_TEMPLATE), ("human", "이미지를 분석해주세요.")]
    )
    | ChatOpenAI(temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    | StrOutputParser()
)
