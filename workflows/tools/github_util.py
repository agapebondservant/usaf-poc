"""Custom CrewAI tools for GitHub operations using PyGithub.

Uses the GraphQL API for GitHub Projects V2 (replacing the deprecated
classic Projects columns/cards API).
"""

import os
from github import Github, GithubException
from git import Repo
import logging
import traceback
import shutil
from typing import Any
from tools import graphql_util
from ruamel.yaml import YAML

logging.basicConfig(level=logging.INFO)

_GITHUB_TOKEN = os.getenv("CODEAGENT_GITHUB_PAT")

_GITHUB_REPO = os.getenv("DEVSPACES_GIT_REPO")

_LOCAL_PATH = "tmp"

_YAML = YAML()


def _get_github_client(default_branch: str = "refactored"):
    """Get an authenticated GitHub repo."""

    logging.info(f"Repo name: {_GITHUB_REPO}")

    repo = Github(_GITHUB_TOKEN).get_repo(_GITHUB_REPO)

    repo.edit(default_branch="refactored")

    return repo

def _get_github_user():
    """Get an authenticated GitHub user."""

    logging.info(f"Repo name: {_GITHUB_REPO}")

    return Github(_GITHUB_TOKEN).get_user()

def _get_project_metadata(project_name):
    """Returns metadata for this project searched by name.

    Returns (project_id, status_field_id, {option_name: option_id}).
    """
    try:
        owner = _get_github_user().login

        try:
            logging.debug(f"Trying project search by organization...")

            query = graphql_util.get_query_string("get_nodes_and_pageinfo_by_org")

            data = graphql_util.query(query, _GITHUB_TOKEN, {"owner": owner})

            projects = data["organization"]["projectsV2"]["nodes"]

        except Exception:
            logging.debug(f"Failed, trying project search by user...")

            query = graphql_util.get_query_string("get_nodes_and_pageinfo_by_user")

            data = graphql_util.query(query, _GITHUB_TOKEN,  {"owner": owner})

            projects = data["user"]["projectsV2"]["nodes"]

        project_id = [p["id"] for p in projects if p["title"] == project_name][0]

        logging.debug("Querying project fields for status options...")

        field_query = graphql_util.get_query_string("get_project_status_field_data")

        data = graphql_util.query(field_query, _GITHUB_TOKEN, {"projectId": project_id})

        for field in data["node"]["fields"]["nodes"]:

            if field.get("name") == "Status":

                option_map = {opt["name"]: opt["id"] for opt in field["options"]}

                return project_id, field["id"], option_map

        raise Exception(f"No 'Status' field found in project '{project_name}'.")

    except Exception as e:
        logging.error(f"Error getting project metadata: {e}")

        logging.error(traceback.format_exc())

def clone_repo(local_path=_LOCAL_PATH, branch="main"):
    """Clone a GitHub repo locally."""
    logging.info(f'Cloning repo to {local_path}...')

    try:

        if os.path.exists(local_path):
            logging.info(f'Repo {local_path} already exists. Removing...')

            shutil.rmtree(local_path)

        client = _get_github_client()

        repo_url = client.clone_url

        print(f"Found repository: {client.name}")

        Repo.clone_from(repo_url, local_path, branch=branch)

    except Exception as e:

        logging.error(f'Error cloning repo to {local_path}...')

        logging.error(traceback.format_exc())

def create_feature_branch(feature_branch: str, local_path: str=_LOCAL_PATH):
    """Creates a new feature branch from the current branch and pushes it remotely."""
    logging.info(f"Creating feature branch {feature_branch} in {local_path}...")

    try:

        client = _get_github_client()

        repo_url = client.clone_url.replace("https://github.com",
                                            f"https://{_GITHUB_TOKEN}@github.com")

        repo = Repo(local_path)

        origin = repo.remotes.origin

        origin.set_url(repo_url)

        new_branch = repo.create_head(feature_branch)

        new_branch.checkout()

        logging.debug(f"Pushing {feature_branch} to remote...")

        origin.push(refspec=f"{feature_branch}:{feature_branch}",
                    env={"GIT_ASKPASS": "echo",
                         "GIT_USERNAME": "x-access-token",
                         "GIT_PASSWORD": _GITHUB_TOKEN})

        print(f"Feature branch {feature_branch} created and pushed successfully.")

    except Exception as e:

        logging.error(f'Error creating feature branch {feature_branch} in {local_path}...')

        logging.error(traceback.format_exc())

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
    try:
        client = _get_github_client()

        issue = client.create_issue(title=title, body=body)

        logging.info(f"Issue #{issue.number} created: {issue.html_url}. "
                     f"Adding issue to project {project}...")

        project_id, status_field_id, status_options = _get_project_metadata(project)

        if "Backlog" not in status_options:

            raise Exception(f"Project '{project}' must have a 'Backlog' status option.")

        logging.info(f"Adding issue to project '{project}'...")

        add_issue_mutation = graphql_util.get_query_string("add_project_issue_mutation")

        data = graphql_util.query(add_issue_mutation, _GITHUB_TOKEN,{
            "projectId": project_id,
            "contentId": issue.node_id,
        })

        item_id = data["addProjectV2ItemById"]["item"]["id"]

        logging.info(f"Setting issue status to 'Backlog'...")

        status_mutation = graphql_util.get_query_string("update_project_status_mutation")

        graphql_util.query(status_mutation, _GITHUB_TOKEN,{
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": status_field_id,
            "optionId": status_options["Backlog"],
        })

        logging.info(f"Successfully added issue #{issue.number} to project "
                     f"'{project}' with status 'Backlog'")

        return issue.number
    except Exception as e:
        logging.error(f"Error creating issue in project {project}: {e}")

        logging.error(traceback.format_exc())

def get_top_issue_in_status(status_name: str, project: str = "Release 1") -> Any:
    """Get the first issue with the given status in a ProjectV2, or None if
    no issues have that status.

    Returns a dict with 'item_id', 'issue_number', and 'issue_title', or None.
    """
    try:
        project_id, status_field_id, status_options = _get_project_metadata(project)

        if status_name not in status_options:
            raise Exception(f"Status '{status_name}' not found in project '{project}'.")

        query = graphql_util.get_query_string("nodes_with_issue_content")

        data = graphql_util.query(query, _GITHUB_TOKEN, {"projectId": project_id})

        for item in data["node"]["items"]["nodes"]:

            content = item.get("content")

            if not content or "number" not in content:
                continue

            for fv in item["fieldValues"]["nodes"]:
                if (fv.get("field", {}).get("id") == status_field_id
                        and fv.get("name") == status_name):

                    logging.info(f"Returning issue #{content['number']} with "
                                 f"status '{status_name}'")
                    return {
                        "item_id": item["id"],
                        "issue_number": content["number"],
                        "issue_title": content["title"],
                    }
        return None

    except Exception as e:

        logging.error(f"Error getting top issue with status '{status_name}': {e}")

        logging.error(traceback.format_exc())


def move_top_issue_to_status(old_status: str, new_status: str,
                             project: str = "Release 1"):
    """Move the top issue from one status to another in the given project."""
    try:
        logging.info(f"Moving top issue from '{old_status}' to '{new_status}'...")

        project_id, status_field_id, status_options = _get_project_metadata(project)

        if new_status not in status_options:
            raise Exception(f"Status '{new_status}' not found in project '{project}'.")

        item = get_top_issue_in_status(old_status, project)
        if not item:
            raise Exception(f"No issues found with status '{old_status}'.")

        mutation = graphql_util.get_query_string("update_project_status_mutation")

        logging.info(f"Updating issue status to '{new_status}'...")

        graphql_util.query(mutation, _GITHUB_TOKEN, {
            "projectId": project_id,
            "itemId": item["item_id"],
            "fieldId": status_field_id,
            "optionId": status_options[new_status],
        })

        logging.info(f"Successfully moved issue #{item['issue_number']} from "
                     f"'{old_status}' to '{new_status}'")
    except Exception as e:
        logging.error(f"Error moving issue to status '{new_status}': {e}")
        logging.error(traceback.format_exc())


def is_project_empty(project: str = "Release 1") -> bool:
    """Check whether a Kanban project board has no issues."""
    try:
        project_id, _, _ = _get_project_metadata(project)

        query = graphql_util.get_query_string("nodes_with_issue_content")

        data = graphql_util.query(query, _GITHUB_TOKEN, {
            "projectId": project_id,
        })

        items = data["node"]["items"]["nodes"]

        has_issues = any(
            item.get("content") and "number" in item["content"]
            for item in items
        )

        logging.info(f"Checking whether Project '{project}' found issues on "
                     f"the board: {has_issues}")

        return not has_issues

    except Exception as e:
        logging.error(f"Error checking if project '{project}' is empty: {e}")
        logging.error(traceback.format_exc())
        return False


def is_sprint_blocked(project: str = "Release 1") -> bool:
    """Check whether the sprint is blocked.

    Returns True if:
      - Any issue has status "Blocked"
      - No issues have status "Ready" or "Backlog"

    Returns False otherwise.
    """
    try:
        project_id, status_field_id, _ = _get_project_metadata(project)

        query = graphql_util.get_query_string("nodes_with_issue_content")

        data = graphql_util.query(query, _GITHUB_TOKEN, {
            "projectId": project_id,
        })

        items = data["node"]["items"]["nodes"]

        has_ready_or_backlog = False

        for item in items:

            content = item.get("content")

            if not content or "number" not in content:
                continue

            for fv in item["fieldValues"]["nodes"]:
                if fv.get("field", {}).get("id") != status_field_id:
                    continue

                status = fv.get("name")

                if status == "Blocked":
                    logging.info(f"Issue #{content['number']} is Blocked.")
                    return True

                if status in ("Ready", "Backlog"):
                    has_ready_or_backlog = True

        if not has_ready_or_backlog:
            logging.info(f"No issues with status 'Ready' or 'Backlog' in "
                         f"project '{project}'.")
            return True

        return False

    except Exception as e:
        logging.error(f"Error checking if sprint is blocked for '{project}': {e}")
        logging.error(traceback.format_exc())
        return True


def is_sprint_in_progress(project: str = "Release 1") -> bool:
    """Check whether a sprint is currently in progress.

    Returns True if exactly 1 issue has a status not in
    ("Ready", "Backlog", "Done").

    Returns False otherwise.
    """
    try:
        project_id, status_field_id, _ = _get_project_metadata(project)

        query = graphql_util.get_query_string("nodes_with_issue_content")

        data = graphql_util.query(query, _GITHUB_TOKEN, {
            "projectId": project_id,
        })

        items = data["node"]["items"]["nodes"]

        active_count = 0

        for item in items:

            content = item.get("content")

            if not content or "number" not in content:
                continue

            for fv in item["fieldValues"]["nodes"]:
                if fv.get("field", {}).get("id") != status_field_id:
                    continue

                if fv.get("name") not in ("Ready", "Backlog", "Done"):
                    active_count += 1

        logging.info(f"Project '{project}' has {active_count} active issue(s).")

        return active_count == 1

    except Exception as e:
        logging.error(f"Error checking if sprint is in progress for '{project}': {e}")
        logging.error(traceback.format_exc())
        return False


def create_pull_request_for_issue(title: str, head: str, issue_number: int,
                                  local_path: str = _LOCAL_PATH, base: str = "main",
                                  body: str = ""):
    """Create a new pull request for the given issue and link it to the PR body.

    Args:
        title: The PR title.
        head: The branch containing changes (head branch).
        issue_number: The issue number to link to the PR.
        local_path: The path to the local repo.
        base: The branch to merge into (base branch). Defaults to 'main'.
        body: The PR body/description.
    """
    try:
        client = _get_github_client()

        repo = Repo(local_path)

        origin = repo.remotes.origin

        repo.git.add(A=True)

        repo.index.commit("Updates")

        origin.push(refspec=f"{head}:{head}")

        pr = client.create_pull(title=title,
                                body=f"{body}\ncloses #{issue_number}",
                                head=head,
                                base=base)

        logging.info(f"PR #{pr.number} created: {pr.html_url}")

        return pr.number

    except Exception as e:
        logging.error(f"Error creating PR: {e}")

        logging.error(traceback.print_exc())


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
    try:

        repo = Repo(local_path)

        origin = repo.remotes.origin

        repo.git.checkout(base)

        origin.pull()

        repo.git.merge(head, strategy_option="ours")

        origin.push(refspec=f"{base}:{base}", force=True)

        logging.info(f"PR #{pr_number} merged successfully via {merge_method}.")

    except Exception as e:
        logging.error(f"Error merging PR: {e}")

        logging.error(traceback.format_exc())

def sprint_kickoff_metadata(backlog_file: str,
                            sprint_description_file: str,
                            project: str = "Release 1",) -> Any:
    """
    Retrieves relevant metadata for the sprint backlog to be processed
    by the workflow.
    """

    try:

        sprint_started = not is_project_empty(project)

        if not sprint_started:

            with open(sprint_description_file, "r") as f:

                user_story_data = _YAML.safe_load(sprint_description_file)

                sprint_description = f.read()

                return {"title": "Sprint Kickoff", "description": sprint_description}

        else:

            with open(backlog_file, "r") as f:

                backlog_issue_data = f.readlines()

                for line in backlog_issue_data:

                    create_issue(title=line.strip(), project=project)

            next_ready_issue = get_top_issue_in_status("Ready", project)

            next_backlog_issue = get_top_issue_in_status("Backlog", project)

            next_blocked_issue = get_top_issue_in_status("Blocked", project)

            return {"title": next_ready_issue["issue_title"], "description": next_ready_issue["issue_number"]}

    except Exception as e:

        logging.error("Error while kicking off sprint: {}".format(e))

        logging.error(traceback.format_exc())





        return get_top_issue_in_status("Backlog", project)["issue_number"] if get_top_issue_in_status("Backlog", project) else create_issue(
            title=f"Issue #{retrieve_next_issue_netadata(project) + 1}",
            project=project,
        )

    except Exception as e:

        logging.error(f"Error retrieving next issue: {e}")

        logging.error(traceback.format_exc())

        return -1
