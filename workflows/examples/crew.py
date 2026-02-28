##############################################################################
# Crews
##############################################################################

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, DirectoryReadTool, FileWriterTool, FileReadTool
from crewai.tools import tool
import os
from tools import github_util, file_tools, evaluation_tools
from data_models.data_models import UserStory, UserStoryList, DocDetails, EvalDetails
import inspect
from pydantic import BaseModel
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
class ReleaseCycle():
    """
    The release cycle covers the release planning, including the kickoff and
    signoff for the sprints within the release.
    """

    def __init__(self, feature: str, selected_model: str):
        self.selected_model = selected_model
        self.feature = feature

    agents: List[BaseAgent]

    tasks: List[Task]

    agents_config = "multi-agent/agents/release_planning/agents.yaml"

    tasks_config = "multi-agent/agents/release_planning/tasks.yaml"

    @agent
    def product_owner(self) -> Agent:
        """
        Works on the "release kickoff" of the AI software
        development cycle.
        Plans and prepares the backlog for the current sprint by creating a
        tracking log.
        """
        logging.info(f"Product Owner: {self.selected_model}")
        return Agent(
            config=self.agents_config["product_owner"],
            llm=get_selected_model(self.selected_model),
            tools=[file_tools.read_files_by_pattern,
                   file_tools.read_file_by_name],
            result_as_answer=True,
        )

    @task
    def product_owner_user_stories(self) -> Task:
        """Converts specs into user stories and backlog items for building
        documentation."""
        return Task(
            config=self.tasks_config["product_owner_user_stories"],
            output_pydantic=UserStoryList,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ReleaseCycle crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            cache=False,
        )

@CrewBase
class SprintCycle:
    """
    The sprint cycle covers the following phases of the AI software
    development cycle:
    - Sprint Planning
    - Sprint Implementation
    - Sprint Evaluation
    - Sprint Delivery
    """

    def __init__(self, feature: str, selected_model: str, category: str):
        self.selected_model = selected_model
        self.feature = feature
        self.category = category
        self.agents_config = f"multi-agent/agents/sprint_planning/agents.yaml"
        self.tasks_config = (f"multi-agent/agents/sprint_planning/{category}/tasks.yaml")
        self.data_type = self.resolve_class(category)

    def resolve_class(self, category: str) -> type[BaseModel]:
        classname = f"{category.capitalize()}Details"

        cls = globals().get(classname)

        if cls is None or not inspect.isclass(cls) or not issubclass(cls, BaseModel):
            raise ValueError(f"'{classname}' is not a valid Pydantic model")

        return cls

    agents: List[BaseAgent]

    tasks: List[Task]

    agents_config: str

    tasks_config: str

    selected_model: str

    category: str

    file_writer_tool = FileWriterTool(overwrite=False, create_dir=True)

    file_reader_tool = FileReadTool()

    @agent
    def sprint_planner(self) -> Agent:
        """
        Works on the "planning phase" of the AI software development cycle.
        Defines the scope of the sprint; also provides more essential detail
        for the sprint tasks by providing various technical plans, documents and
        specifications which will be used as goldens
        or anchors for the sprint.
        """
        return Agent(
            config=self.agents_config["sprint_planner"],
            llm=get_selected_model(self.selected_model),
            tools=[file_tools.read_files_by_pattern,
                   file_tools.read_file_by_name,
                   self.file_writer_tool,
                   self.file_reader_tool],
            result_as_answer=True,
        )

    @agent
    def tech_writer(self) -> Agent:
        """
        Writes the artifacts (code, specifications, documents etc) specified in the planning phase.
        """
        return Agent(
            config=self.agents_config["tech_writer"],
            llm=get_selected_model(self.selected_model),
            tools=[file_tools.read_files_by_pattern,
                   file_tools.read_file_by_name,
                   self.file_writer_tool,
                   self.file_reader_tool],
            result_as_answer=True,
        )

    @agent
    def reviewer(self) -> Agent:
        """
        Akin to the "evaluation / quality assurance phase" of the AI software
        development cycle.
        (Although this is normally performed in parallel with the
        implementation phase, for ease of automation it is being performed
        serially here.)
        Involves the comprehensive evaluation of the code, documents and/or tests
        which have been implemented in the implementation phase.
        Often owned by the QA Analyst, although it can also be owned by the
        Technical Lead or others depending on the specific project and the release.
        """
        return Agent(
            config=self.agents_config["reviewer"],
            llm=get_selected_model(self.selected_model),
            tools=[file_tools.read_file_by_name,
                   self.file_writer_tool,
                   self.file_reader_tool,
                   evaluation_tools.get_llm_as_judge_evaluation_scores],
            verbose=True
        )

    @task
    def plan(self) -> Task:
        return Task(
            config=self.tasks_config["plan"],
            output_pydantic=self.data_type,
        )

    @task
    def pre_build(self) -> Task:
        return Task(
            config=self.tasks_config["pre-build"],
        )

    @task
    def build(self) -> Task:
        return Task(
            config=self.tasks_config["build"],
        )

    @task
    def reflect(self) -> Task:
        return Task(
            config=self.tasks_config["reflect"],
        )
    #
    # @agent
    # def release_engineer(self) -> Agent:
    #     """
    #     Involves the creation of readiness artifacts which will be used in the
    #     decision to restart the cycle or end it. The readiness artifacts are
    #     the unit test suite and the CI
    #     workflow which triggers the next task if the current one passes.
    #     Mainly owned by the Release Engineer.
    #     """
    #     return Agent(
    #         config=self.agents_config["release_engineer"],
    #         llm=get_selected_model(self.selected_model),
    #     )
    #
    # @task
    # def release_engineer_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["release_engineer"],
    #     )
    #
    # @agent
    # def release_delivery(self) -> Agent:
    #     """
    #     Involves the delivery of the code and the documentation to the
    #     product owner for review and approval.
    #     Mainly owned by the Tech Lead.
    #     """
    #     return Agent(
    #         config=self.agents_config["tech_lead"],
    #         llm=get_selected_model(self.selected_model),
    #     )
    #
    # @task
    # def release_delivery_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["tech_lead"],
    #     )
    #
    @crew
    def crew(self) -> Crew:
        """Creates the PlanningCycle crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            cache=False,
        )
