import os

from jira import JIRA
import jira
import pandas as pd


def get_issues_per_sprint(jira_client: JIRA, sprint: jira.resources.Sprint) -> pd.DataFrame:
    """
    Get all issues in a sprint
    This does NOT take into account the specific status of
    an issue at the duration of the sprint
    For example, an issue could be "Waiting for review" at the
    end of the sprint, but can be "Closed" now. This will
    skew the "number of story points" per engineer over time.

    Args:
        jira_client (JIRA): _description_
        sprint (jira.resources.Sprint): _description_

    Returns:
        pd.DataFrame: all issues in a sprint
    """
    result = []
    issues = jira_client.search_issues(f"sprint={sprint.id}", maxResults=300)
    for issue in issues:
        issue_info = jira_client.issue(issue.id)
        # issue_info.raw will get you the raw data
        # issue_assignee = issue_info.fields.assignee.displayName
        if issue_info.fields.assignee is not None:
            issue_assignee = issue_info.fields.assignee.displayName
        else:
            issue_assignee = None
        # Story points
        issue_story_points = issue_info.raw['fields'].get("customfield_10014")
        # 'customfield_12105': '6.0',
        # Status of ticket
        issue_status = issue_info.fields.status.name
        issue_summary = issue_info.fields.summary
        issue_desc = issue_info.fields.description
        issue_type_name = issue_info.fields.issuetype.name
        # Target start
        # issue_start_date = issue_info.fields.customfield_12113
        # issue_due_date = issue_info.fields.duedate

        result.append({
            'sprint_id': sprint.id,
            "issuetype": issue_type_name,
            "key": issue.id,
            "summary": issue_summary,
            "description": issue_desc,
            'status': issue_status,
            "assignee": issue_assignee,
            'story_points': issue_story_points,
            "sprint": sprint.name,
            # "target_start": issue_start_date,
            # "due_date": issue_due_date
        })
    jira_issues_df = pd.DataFrame(result)
    return jira_issues_df


def main():
    username = os.environ['JIRA_USERNAME']
    api_token = os.environ['JIRA_API_TOKEN']
    jira_client = JIRA(
        server='https://sagebionetworks.jira.com/',
        basic_auth=(username, api_token)
    )
    # Get all sprints and issues
    # Board 189 is the DPE scrum board
    # BOard 228 is Synpy scrum b
    # oard
    # board 190 is ETL
    all_sprints = jira_client.sprints(board_id=190)
    all_sprint_info = pd.DataFrame()
    for sprint in all_sprints:
        if sprint.name.startswith("DPE") and "Sprint" not in sprint.name and "12.19.22" not in sprint.name:
            print(sprint.name)
            df = get_issues_per_sprint(jira_client=jira_client, sprint=sprint)
            all_sprint_info = pd.concat([all_sprint_info, df])
    all_sprint_info.to_csv("dpe_sprint_info.csv", index=False)

if __name__ == "__main__":
    main()
