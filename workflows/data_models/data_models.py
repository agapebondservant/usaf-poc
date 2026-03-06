from pydantic import BaseModel, ConfigDict
from typing import List, Any, Optional

class UserStory(BaseModel):
    title: str
    body: str
    acceptance_criteria: str

class UserStoryList(BaseModel):
    stories: List[UserStory]

class DocDetails(BaseModel):
    file_name: str = ""
    document_type: str = ""
    reference_file_locations: str = ""
    result_content: Any = ""

class EvalElementDetails(BaseModel):
    baseline: str = ""
    candidate: str = ""
    reference: list = [""]
    eval_scores_relevancy: float = 0.0
    eval_reasons_relevancy: str = ""

class EvalDetails(BaseModel):
    data: List[EvalElementDetails] = []
    result_content: Any = {}

class AggregateDetails(BaseModel):
    doc_detail: Optional[DocDetails] = DocDetails()
    eval_detail: Optional[EvalDetails] = EvalDetails()
