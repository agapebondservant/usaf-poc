"""Custom CrewAI tools for GitHub operations using PyGithub."""

import os
from crewai.tools import tool
from github import Github, GithubException


def _get_github_client():
    """Get an authenticated GitHub client and repo."""
    token = os.getenv("CODEAGENT_GITHUB_PAT")

    repo_name = os.getenv("GITHUB_REPO")

    return Github(token).get_repo(repo_name)


@tool("Create GitHub Issue")
def create_issue(title: str, body: str = "", labels: str = "") -> str:
    """Create a new GitHub issue.

    Args:
        title: The issue title.
        body: The issue body/description.
        labels: Comma-separated list of label names to apply.
    """
    try:
        repo = _get_github_client()
        label_list = [l.strip() for l in labels.split(",") if l.strip()] if labels else []
        github_labels = []
        for name in label_list:
            try:
                github_labels.append(repo.get_label(name))
            except GithubException:
                pass  # skip labels that don't exist
        issue = repo.create_issue(title=title, body=body, labels=github_labels)
        return f"Issue #{issue.number} created: {issue.html_url}"
    except GithubException as e:
        return f"Error creating issue: {e.data.get('message', str(e))}"


@tool("List GitHub Issues")
def list_issues(state: str = "open") -> str:
    """List GitHub issues in the repository.

    Args:
        state: Filter by state - 'open', 'closed', or 'all'.
    """
    try:
        repo = _get_github_client()
        issues = repo.get_issues(state=state)
        results = []
        for issue in issues[:20]:
            if issue.pull_request is None:  # exclude PRs
                labels = ", ".join(l.name for l in issue.labels)
                label_str = f" [{labels}]" if labels else ""
                results.append(f"#{issue.number}: {issue.title}{label_str}")
        if not results:
            return f"No {state} issues found."
        return "\n".join(results)
    except GithubException as e:
        return f"Error listing issues: {e.data.get('message', str(e))}"


@tool("Create Pull Request")
def create_pull_request(title: str, head: str, base: str = "main", body: str = "") -> str:
    """Create a new pull request.

    Args:
        title: The PR title.
        head: The branch containing changes (head branch).
        base: The branch to merge into (base branch). Defaults to 'main'.
        body: The PR body/description.
    """
    try:
        repo = _get_github_client()
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return f"PR #{pr.number} created: {pr.html_url}"
    except GithubException as e:
        return f"Error creating PR: {e.data.get('message', str(e))}"


@tool("List Pull Requests")
def list_pull_requests(state: str = "open") -> str:
    """List pull requests in the repository.

    Args:
        state: Filter by state - 'open', 'closed', or 'all'.
    """
    try:
        repo = _get_github_client()
        pulls = repo.get_pulls(state=state)
        results = []
        for pr in pulls[:20]:
            results.append(f"#{pr.number}: {pr.title} ({pr.head.ref} -> {pr.base.ref})")
        if not results:
            return f"No {state} pull requests found."
        return "\n".join(results)
    except GithubException as e:
        return f"Error listing PRs: {e.data.get('message', str(e))}"


@tool("Link Issue to Pull Request")
def link_issue_to_pr(issue_number: int, pr_number: int) -> str:
    """Link a GitHub issue to a pull request by adding 'Closes #N' to the PR body.

    Args:
        issue_number: The issue number to link.
        pr_number: The PR number to update.
    """
    try:
        repo = _get_github_client()
        pr = repo.get_pull(pr_number)
        close_ref = f"Closes #{issue_number}"
        current_body = pr.body or ""
        if close_ref.lower() in current_body.lower():
            return f"PR #{pr_number} already references issue #{issue_number}."
        new_body = f"{current_body}\n\n{close_ref}".strip()
        pr.edit(body=new_body)
        return f"Linked issue #{issue_number} to PR #{pr_number}."
    except GithubException as e:
        return f"Error linking issue to PR: {e.data.get('message', str(e))}"


@tool("Merge Pull Request")
def merge_pull_request(pr_number: int, merge_method: str = "merge") -> str:
    """Merge a pull request.

    Args:
        pr_number: The PR number to merge.
        merge_method: Merge method - 'merge', 'squash', or 'rebase'.
    """
    try:
        repo = _get_github_client()
        pr = repo.get_pull(pr_number)
        if pr.merged:
            return f"PR #{pr_number} is already merged."
        if pr.state == "closed":
            return f"PR #{pr_number} is closed and cannot be merged."
        try:
            result = pr.merge(merge_method=merge_method)
            if result.merged:
                return f"PR #{pr_number} merged successfully via {merge_method}."
            return f"Failed to merge PR #{pr_number}: {result.message}"
        except GithubException as e:
            if e.status not in (405, 409):
                raise
            # Conflict detected — force merge by creating a merge commit
            # with the PR branch's tree (PR changes win on conflicts)
            base_sha = pr.base.sha
            head_sha = pr.head.sha
            head_commit = repo.get_git_commit(head_sha)
            merge_commit = repo.create_git_commit(
                message=f"Merge PR #{pr_number} (forced): {pr.title}",
                tree=head_commit.tree,
                parents=[repo.get_git_commit(base_sha), head_commit],
            )
            base_ref = repo.get_git_ref(f"heads/{pr.base.ref}")
            base_ref.edit(merge_commit.sha, force=True)
            pr.edit(state="closed")
            return (f"PR #{pr_number} force-merged (conflicts overwritten "
                    f"with PR changes).")
    except GithubException as e:
        return f"Error merging PR: {e.data.get('message', str(e))}"
