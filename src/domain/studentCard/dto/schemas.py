from pydantic import BaseModel, Field, validator


class StudentCardInfo(BaseModel):
    name: str = Field(description="학생 이름 (2-3글자 한글)")
    department: str = Field(description="학과명 (XX학과 형식)")
    year: int = Field(description="학년 (1-4 사이의 숫자)")
    student_number: str = Field(description="학번", default="")

    @validator("name")
    def validate_name(cls, v):
        if not v:
            return v
        if not (2 <= len(v) <= 3):
            raise ValueError("이름은 2-3글자여야 합니다")
        if not all(0xAC00 <= ord(c) <= 0xD7A3 for c in v):
            raise ValueError("이름은 한글이어야 합니다")
        return v

    @validator("department")
    def validate_department(cls, v):
        if not v:
            return v
        if not v.endswith("학과"):
            raise ValueError("학과명은 '학과'로 끝나야 합니다")
        return v

    @validator("year")
    def validate_year(cls, v):
        if not v:
            return 0
        if not (1 <= v <= 4):
            raise ValueError("학년은 1-4 사이여야 합니다")
        return v
