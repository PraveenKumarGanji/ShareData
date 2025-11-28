from pydantic import BaseModel
from typing import Dict, List, Optional

from langchain.output_parsers import PydanticOutputParser

class IntentOutput(BaseModel):
    intent: str
    provided_params: Dict[str, Optional[str]]
    missing_required_params: List[str]

intent_parser = PydanticOutputParser(pydantic_object=IntentOutput)
