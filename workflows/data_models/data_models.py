from pydantic import BaseModel
from typing import List

class UserStory(BaseModel):
    title: str
    body: str
    acceptance_criteria: str

class UserStoryList(BaseModel):
    stories: List[UserStory]

class DocDetails(BaseModel):
    file_name: str
    document_type: str
    reference_file_locations: str

class EvalElementDetails(BaseModel):
    baseline: str = ""
    candidate: str = ""
    reference: list = [""]

class EvalDetails(BaseModel):
    data: List[EvalElementDetails]


