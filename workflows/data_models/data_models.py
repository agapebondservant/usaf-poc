from pydantic import BaseModel
from typing import List

class UserStory(BaseModel):
    title: str
    body: str
    acceptance_criteria: str

class UserStoryList(BaseModel):
    stories: List[UserStory]