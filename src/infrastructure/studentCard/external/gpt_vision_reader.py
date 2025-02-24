from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.output_parsers import PydanticOutputParser
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.memory import BaseMemory
from dotenv import load_dotenv
import base64
import json
import os
from src.domain.studentCard.dto.schemas import StudentCardInfo
from typing import List
import logging


# 환경 변수 로드
load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)


class GPTVisionReaderInterface(ABC):
    @abstractmethod
    async def extract_info(self, image_bytes: bytes) -> StudentCardInfo:
        pass


class GPTVisionReader(GPTVisionReaderInterface):
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다")

        logger.info("GPTVisionReader 초기화 시작")

        # 캐시 초기화
        self._cache = {}

        # LLM 설정
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=1000,
            api_key=os.getenv("OPENAI_API_KEY"),
        )

        # Parser 설정
        self.parser = PydanticOutputParser(pydantic_object=StudentCardInfo)

        # Vector Store 설정
        persist_directory = os.getenv("PERSIST_DIRECTORY", "./vector_db")
        os.makedirs(persist_directory, exist_ok=True)

        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"), disallowed_special=()
        )

        try:
            self.vectorstore = Chroma(
                collection_name="student_card_analysis",
                embedding_function=self.embeddings,
                persist_directory=persist_directory,
            )

            # 메모리 초기화
            self.memory = CustomVectorStoreMemory(vectorstore=self.vectorstore)

        except Exception as e:
            print(f"Vector store 초기화 오류: {e}")
            # 기본 vectorstore 생성
            self.vectorstore = Chroma(
                collection_name="student_card_analysis",
                embedding_function=self.embeddings,
            )
            self.memory = CustomVectorStoreMemory(vectorstore=self.vectorstore)

        logger.info("GPTVisionReader 초기화 완료")

    async def extract_info(self, image_bytes: bytes) -> StudentCardInfo:
        try:
            # 캐시 확인
            image_hash = str(hash(image_bytes))
            if image_hash in self._cache:
                return self._cache[image_hash]

            # 벡터 DB 검색 최적화
            similar_cases = await self.memory.load_memory_variables({})

            # 이미지를 base64로 인코딩
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            # 프롬프트 준비 (수정된 부분)
            system_prompt = """
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
"""

            format_instructions = self.parser.get_format_instructions()
            prompt_with_format = system_prompt + "\n" + format_instructions

            # 이전 분석 결과 추가
            if similar_cases.get("chat_history"):
                prompt_with_format += (
                    "\n\n참고할 만한 이전 분석 사례:\n" + similar_cases["chat_history"]
                )

            # 메시지 구성
            messages = [
                SystemMessage(content=prompt_with_format),
                HumanMessage(
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    ]
                ),
            ]

            # GPT로 정보 추출
            response = await self.llm.ainvoke(messages)

            if not response.content or response.content.isspace():
                logger.error("GPT가 빈 응답을 반환했습니다")
                return StudentCardInfo(
                    name="", department="", year=0, student_number=""
                )

            try:
                # 응답 파싱
                result = self.parser.parse(response.content)

                # 분석 결과 저장
                self._save_to_vectorstore(image_bytes, result)

                return result
            except Exception as e:
                logger.error(f"GPT Vision 응답 파싱 실패: {str(e)}")
                logger.error(f"Raw response: {response.content}")
                return StudentCardInfo(
                    name="", department="", year=0, student_number=""
                )

        except Exception as e:
            logger.error(f"OCR 처리 중 예외 발생: {str(e)}")
            return StudentCardInfo(name="", department="", year=0, student_number="")

    def _save_to_vectorstore(self, image_bytes: bytes, result: StudentCardInfo):
        # 분석 결과를 문서화
        doc_content = {
            "analysis_result": result.dict(),
            "image_hash": str(hash(image_bytes)),  # 간단한 이미지 해시
        }

        # VectorDB에 저장
        document = Document(
            page_content=json.dumps(doc_content, ensure_ascii=False),
            metadata={
                "type": "student_card_analysis",
                "department": result.department,
                "year": result.year,
            },
        )

        self.vectorstore.add_documents([document])
        self.vectorstore.persist()  # 디스크에 저장


class CustomVectorStoreMemory(BaseMemory):
    memory_key: str
    return_messages: bool
    vectorstore: Chroma

    def __init__(self, vectorstore: Chroma):
        # 일반 객체 속성으로 초기화
        object.__setattr__(self, "memory_key", "chat_history")
        object.__setattr__(self, "return_messages", True)
        object.__setattr__(self, "vectorstore", vectorstore)

    @property
    def memory_variables(self) -> List[str]:
        """메모리 변수 반환"""
        return [self.memory_key]

    async def load_memory_variables(self, inputs: dict) -> dict:
        """메모리에서 관련 문서 검색"""
        try:
            # 문서가 있는지 먼저 확인
            collection_size = len(self.vectorstore.get())
            k = min(3, max(1, collection_size))  # 컬렉션 크기에 따라 k 조정

            if collection_size > 0:
                docs = self.vectorstore.similarity_search("", k=k)
                memory_data = "\n".join(doc.page_content for doc in docs)
            else:
                memory_data = ""

            return {self.memory_key: memory_data}
        except Exception as e:
            logger.error(f"메모리 로드 중 오류: {e}")
            return {self.memory_key: ""}

    def save_context(self, inputs: dict, outputs: dict) -> None:
        """컨텍스트 저장"""
        pass

    def clear(self) -> None:
        """메모리 초기화"""
        pass
