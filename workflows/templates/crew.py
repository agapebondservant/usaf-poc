##############################################################################
# Crews
##############################################################################

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool, DirectoryReadTool
from crewai.tools import tool
import os
from tools import github_util, file_tools
from data_models.data_models import UserStory, UserStoryList
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

        base_url=os.getenv(f'{model_prefix}_LLM_URL'),

        max_tokens=128_000,
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

    agents_config = "agents/release_planning/agents.yaml"

    tasks_config = "agents/release_planning/tasks.yaml"

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
                   file_tools.read_file_by_name]
        )

    @task
    def product_owner_prep_task(self) -> Task:
        """Generated a concatenated document of the provided file patterns."""
        return Task(
            config=self.tasks_config["product_owner_prep"],
        )

    @task
    def product_owner_task(self) -> Task:
        """Converts specs into user stories and backlog items."""
        return Task(
            config=self.tasks_config["product_owner"],
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

# @CrewBase
# class SprintCycle():
#     """
#     The sprint cycle covers the following phases of the AI software
#     development cycle:
#     - Sprint Planning
#     - Sprint Implementation
#     - Sprint Evaluation
#     - Sprint Delivery
#     """
#
#     def __init__(self, selected_model: str, feature: str):
#         self.selected_model = selected_model
#         self.feature = feature
#
#     agents: List[BaseAgent]
#
#     tasks: List[Task]
#
#     sprint_planning_tasks_config = "agents/sprint_planning/tasks.yaml"
#
#     sprint_planning_agents_config = "agents/sprint_planning/agents.yaml"
#
#     sprint_implementation_tasks_config = "agents/sprint_implementation/tasks.yaml"
#
#     sprint_implementation_agents_config = "agents/sprint_implementation/agents.yaml"
#
#     sprint_evaluation_tasks_config = "agents/sprint_evaluation/tasks.yaml"
#
#     sprint_evaluation_agents_config = "agents/sprint_evaluation/agents.yaml"
#
#     sprint_delivery_tasks_config = "agents/sprint_delivery/tasks.yaml"
#
#     sprint_delivery_agents_config = "agents/sprint_delivery/agents.yaml"
#
#     selected_model: str
#
#     @agent
#     def sprint_planner(self) -> Agent:
#         """
#         Works on the "planning phase" of the AI software development cycle.
#         Defines the scope of the sprint; also provides more essential detail
#         for the sprint tasks by providing various technical plans, documents and
#         specifications which will be used as goldens
#         or anchors for the code or spec generation process.
#         Mainly owned by the Tech Lead, although there is collaboration with
#         the Technical Writer and the Prodyct Owner.
#         """
#         return Agent(
#             config=self.sprint_planning_agents_config["sprint_planner"],
#             llm=get_selected_model(self.selected_model),
#         )
#
#     @task
#     def sprint_planner_task(self) -> Task:
#         return Task(
#             config=self.sprint_planning_tasks_config["sprint_planner"],
#         )
#
#     @agent
#     def developer(self) -> Agent:
#         """
#         Akin to the "implementation phase" of the AI software development cycle.
#         Involves the iterative implementation of the code, documents and/or tests
#         indicated/"specified" by the specs in the planning phase.
#         Mainly owned by the Senior Software Engineer.
#         """
#         return Agent(
#             config=self.sprint_implementation_agents_config["developer"],
#             llm=get_selected_model(self.selected_model),
#         )
#
#     @task
#     def developer_task(self) -> Task:
#         return Task(
#             config=self.sprint_implementation_tasks_config["developer"],
#         )
#
#     @agent
#     def reviewer(self) -> Agent:
#         """
#         Akin to the "evaluation / quality assurance phase" of the AI software
#         development cycle.
#         (Although this is normally performed in parallel with the
#         implementation phase, for ease of automation it is being performed
#         separately here.)
#         Involves the comprehensive evaluation of the code, documents and/or tests
#         which have been implemented in the implementation phase.
#         Often owned by the QA Analyst, although it can also be owned by the
#         Technical Lead or others depending on the specific project and the release.
#         """
#         return Agent(
#             config=self.sprint_evaluation_agents_config["reviewer"],
#             llm=get_selected_model(self.selected_model),
#         )
#
#     @task
#     def reviewer_task(self) -> Task:
#         return Task(
#             config=self.sprint_evaluation_tasks_config["reviewer"],
#         )
#
#     @agent
#     def release_engineer(self) -> Agent:
#         """
#         Involves the creation of readiness artifacts which will be used in the
#         decision to restart the cycle or end it. The readiness artifacts are
#         the unit test suite and the CI
#         workflow which triggers the next task if the current one passes.
#         Mainly owned by the Release Engineer.
#         """
#         return Agent(
#             config=self.sprint_delivery_agents_config["release_engineer"],
#             llm=get_selected_model(self.selected_model),
#         )
#
#     @task
#     def release_engineer_task(self) -> Task:
#         return Task(
#             config=self.sprint_delivery_tasks_config["release_engineer"],
#         )
#
#     @agent
#     def release_delivery(self) -> Agent:
#         """
#         Involves the delivery of the code and the documentation to the
#         product owner for review and approval.
#         Mainly owned by the Tech Lead.
#         """
#         return Agent(
#             config=self.sprint_delivery_agents_config["tech_lead"],
#             llm=get_selected_model(self.selected_model),
#         )
#
#     @task
#     def release_delivery_task(self) -> Task:
#         return Task(
#             config=self.sprint_delivery_tasks_config["tech_lead"],
#         )
#
#     @crew
#     def crew(self) -> Crew:
#         """Creates the PlanningCycle crew"""
#
#         return Crew(
#             agents=self.agents,
#             tasks=self.tasks,
#             process=Process.sequential,
#             verbose=True,
#             cache=False,
#         )
