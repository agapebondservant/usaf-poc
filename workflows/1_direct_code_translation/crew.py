##############################################################################
# Crews
##############################################################################

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, DirectoryReadTool, FileWriterTool
from crewai.tools import tool
import os
from tools import github_util, file_tools
from data_models.data_models import UserStory, UserStoryList, DocumentDetails
import logging
from dotenv import load_dotenv
load_dotenv()

##############################################################################
# LLMs
##############################################################################

def get_selected_model(model_prefix: str):

    llm = LLM(

        model=os.getenv(f'{model_prefix}_LLM_PROVIDER') + "/" +
              os.getenv(f'{model_prefix}_LLM_ID'),

        api_key=os.getenv(f'{model_prefix}_LLM_TOKEN'),

        base_url=os.getenv(f'{model_prefix}_LLM_API_BASE'),

        max_tokens=128_000,

        temperature=0,
    )

    return llm

@CrewBase
class DirectCodeTranslationCycle():
    """
    The release cycle covers the release planning, including the kickoff and
    signoff for the sprints within the release.
    """

    def __init__(self, feature: str, selected_model: str):
        self.selected_model = selected_model
        self.feature = feature

    agents: List[BaseAgent]

    tasks: List[Task]

    agents_config = "implementation/agents.yaml"

    tasks_config = "implementation/tasks.yaml"

    @agent
    def coder(self) -> Agent:
        """
        Responsible for the direct code translation.
        """
        logging.info(f"Selected model: {self.selected_model}")
        return Agent(
            config=self.agents_config["coder"],
            llm=get_selected_model(self.selected_model),
            tools=[file_tools.read_files_by_pattern,
                   file_tools.read_file_by_name],
            result_as_answer=True,
        )

    @task
    def coder_task(self) -> Task:
        """Direct code translation task."""
        return Task(
            config=self.tasks_config["coder"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DirectCodeTranslationCycle crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            cache=False,
        )
