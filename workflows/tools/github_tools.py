"""Custom CrewAI tools for GitHub operations using PyGithub.

Uses the GraphQL API for GitHub Projects V2 (replacing the deprecated
classic Projects columns/cards API).
"""

import os
from crewai.tools import tool
from github import Github, GithubException
from git import Repo
from typing import Any
from tools import github_util, graphql_util

_GITHUB_TOKEN = os.getenv("CODEAGENT_GITHUB_PAT")

_GITHUB_REPO = os.getenv("DEVSPACES_GIT_REPO")

_LOCAL_PATH = "tmp"

@tool("Clone Repo")
def clone_repo(local_path=_LOCAL_PATH, branch="main"):
    """Clone a GitHub repo locally."""
    github_util.clone_repo(local_path, branch)

@tool("Create feature branch")
def create_feature_branch(feature_branch: str, local_path: str=_LOCAL_PATH):
    """Creates a new feature branch from the current branch and pushes it remotely."""
    github_util.create_feature_branch(feature_branch, local_path)


@tool("Create GitHub Issue")
def create_issue(title: str, body: str = "",
                 project: str = "Release 1") -> int:
    """Create a new GitHub issue and add it to the "Backlog" status of the given project.

    Assumes that the project has a Status field with a "Backlog" option.

    Args:
        title: The issue title.
        body: The issue body/description.
        project: The project to create the issue in.

    Returns:
        The generated issue number.
    """
    return github_util.create_issue(title, body, project=project)


@tool("Get Top Issue In Status")
def get_top_issue_in_status(status_name: str, project: str = "Release 1") -> Any:
    """Get the first issue with the given status in a ProjectV2, or None if
    no issues have that status.

    Returns a dict with 'item_id', 'issue_number', and 'issue_title', or None.
    """
    github_util.get_top_issue_in_status(status_name, project)


@tool("Move Top Issue To New Status")
def move_top_issue_to_status(old_status: str, new_status: str,
                             project: str = "Release 1"):
    """Move the top issue from one status to another in the given project."""
    github_util.move_top_issue_to_status(old_status, new_status, project)

@tool("Check if Project is Empty")
def is_project_empty(project: str = "Release 1") -> bool:
    """Check whether a Kanban project board has no issues."""
    github_util.is_project_empty(project)


@tool("Create Pull Request For Issue")
def create_pull_request_for_issue(title: str, head: str, issue_number: int,
                                  local_path: str = _LOCAL_PATH, base: str = "main",
                                  body: str = ""):
    github_util.create_pull_request_for_issue(title, head, issue_number, local_path, base, body)


@tool("Merge Pull Request")
def merge_pull_request(pr_number: int,
                       head: str,
                       base: str = "main",
                       local_path: str = _LOCAL_PATH,
                       merge_method: str = "merge"):
    """Merge a pull request.
    NOTE: This function will fail if the PR has conflicts.
    To remedy this, only serial workflows are currently supported (not
    parallel).
    This should be sufficient for many use cases, but may need to be enhanced
    depending on requirements.

    Args:
        pr_number: The PR number to merge.
        head: The branch containing changes (head branch).
        base: The branch to merge into (base branch). Defaults to 'main'.
        local_path: The path to the local repo. Defaults to tmp.
        merge_method: Merge method - 'merge', 'squash', or 'rebase'.
    """
    github_util.merge_pull_request(pr_number, head, base, local_path, merge_method)
