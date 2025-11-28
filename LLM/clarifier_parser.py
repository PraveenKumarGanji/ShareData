# app/parsers/clarifier_parser.py
from pydantic import BaseModel
from typing import Optional
from langchain.output_parsers import PydanticOutputParser

class ClarifierOutput(BaseModel):
    question: str  # empty string if extraction succeeded
    extracted_parameter_name: Optional[str]
    extracted_parameter_value: Optional[str]

clarifier_parser = PydanticOutputParser(pydantic_object=ClarifierOutput)
