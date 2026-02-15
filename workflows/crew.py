##############################################################################
# Crews
##############################################################################

from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import SerperDevTool
from crewai.tools import tool
import os


##############################################################################
# LLMs
##############################################################################

main_llm = LLM(
    
    model=os.getenv('MAIN_LLM_ID'),
    
    api_key=os.getenv('OPENROUTER_TOKEN'),
    
    base_url=os.getenv('OPENROUTER_API_BASE'),

    max_tokens = 100_000,
)

def get_selected_model(model_prefix: str):
    print(model_prefix)
    llm = LLM(

        model=os.getenv(f'{model_prefix}_LLM_ID'),

        api_key=os.getenv(f'{model_prefix}_LLM_TOKEN'),

        base_url=os.getenv(f'{model_prefix}_LLM_URL'),

        max_tokens=100_000,
    )

    return llm

@CrewBase
class CodeToSummary():
    """Generates summary for the code in a given source language"""

    def __init__(self, selected_model: str):
        self.selected_model = selected_model

    agents: List[BaseAgent]
    
    tasks: List[Task]

    tasks_config = "code-to-summary/tasks.yaml"

    agents_config = "code-to-summary/agents.yaml"

    selected_model: str
        
    @agent
    def code_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['code_analyzer'],
            llm=get_selected_model(self.selected_model),
        )
            
    @task
    def code_analyzer_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_analyzer"], 
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Code-To-Spec crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
        )

@CrewBase
class SummaryToSpec():
    """Generates spec file for the code + summary provided in a given source language"""
    def __init__(self, selected_model: str):
        self.selected_model = selected_model

    agents: List[BaseAgent]
    
    tasks: List[Task]

    tasks_config = "summary-to-spec/tasks.yaml"

    agents_config = "summary-to-spec/agents.yaml"

    selected_model: str

    @agent
    def code_scribe(self) -> Agent:
        return Agent(
            config=self.agents_config['code_scribe'],
            llm=get_selected_model(self.selected_model),
        )

    @task
    def code_scribe_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_scribe"], 
        )

    
    @crew
    def crew(self) -> Crew:
        """Creates the Summary-to-Spec crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
        )

@CrewBase
class SpecToCode():
    """Generates code in a given target language from a spec"""
    def __init__(self, selected_model: str):
        self.selected_model = selected_model

    agents: List[BaseAgent]
    
    tasks: List[Task]

    agents_config = "spec-to-code/agents.yaml"

    tasks_config = "spec-to-code/tasks.yaml"

    selected_model: str

    @agent
    def code_translator(self) -> Agent:
        return Agent(
            config=self.agents_config['code_translator'],
            llm=get_selected_model(self.selected_model),
        )

    @task
    def code_translator_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_translator"],
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Code Translation crew"""

        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            cache=False,
        )