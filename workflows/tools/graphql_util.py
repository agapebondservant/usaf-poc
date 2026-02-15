import requests
import logging
logging.basicConfig(level=logging.INFO)

_GRAPHQL_URL = "https://api.github.com/graphql"

_QUERIES = {
    "get_nodes_and_pageinfo_by_org" : """query($owner: String!, $cursor: String) {
      organization(login: $owner) {
        projectsV2(first: 50, after: $cursor) {
          nodes { id title }
          pageInfo { hasNextPage endCursor }
        }
      }
    }""",
    "get_nodes_and_pageinfo_by_user" : """query($owner: String!, $cursor: String) {
      user(login: $owner) {
        projectsV2(first: 50, after: $cursor) {
          nodes { id title }
          pageInfo { hasNextPage endCursor }
        }
      }
    }""",
    "get_project_status_field_data": """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 50) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id name
                    options { id name }
                  }
                }
              }
            }
          }
        }
        """,
    "add_project_issue_mutation": """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """,
    "update_project_status_mutation": """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId, itemId: $itemId,
            fieldId: $fieldId,
            value: {singleSelectOptionId: $optionId}
          }) { projectV2Item { id } }
        }
        """,
    "nodes_with_issue_content": """
        query($projectId: ID!, $cursor: String) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 50, after: $cursor) {
                nodes {
                  id
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name field { ... on ProjectV2SingleSelectField { id } }
                      }
                    }
                  }
                  content {
                    ... on Issue { number title url }
                  }
                }
                pageInfo { hasNextPage endCursor }
              }
            }
          }
        }
        """
}

def get_query_string(query_name):
    """Return the query string for the given query name."""
    return _QUERIES[query_name]

def query(query, token, variables):
    """Execute a GitHub GraphQL query and return the response data."""
    logging.debug(f"Executing GraphQL query: {query}")

    response = requests.post(
        _GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers={
            "Authorization": f"Bearer {token}"},
    )

    response.raise_for_status()

    body = response.json()

    if "errors" in body:
        raise Exception(f"GraphQL errors: {body['errors']}")

    return body["data"]