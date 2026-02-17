from pydantic import BaseModel

class UserStory(BaseModel):
    title: str
    body: str
    acceptance_criteria: str

class UserStoryList(BaseModel):
    issues: list[UserStory]