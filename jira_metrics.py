"""This script will generate the sprint info csv that gets injested into snowflake
https://docs.google.com/spreadsheets/d/1mp_1Tpy-dWv73bd9eZeaClT7EkWdkXJq3DxcgI9RgaU/edit#gid=0
spreadsheet containing headers we care about
"""
import os
import datetime
import pytz

from jira import JIRA
import jira
import pandas as pd
import requests


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
        # Create dict with headers to update later
        # headers = get_custom_headers(issue_id=issue_info.key)
        # issues_with_headers = {}
        # for key in issue_info.raw['fields'].keys():
        #     if 'customfield' in key:
        #         new_header = headers[key]
        #         issues_with_headers[new_header] = issue_info.raw['fields'][key]

        # issue_info.raw['fields'].update(issues_with_headers)

        # Story points
        issue_story_points = issue_info.raw['fields'].get("customfield_10014")
        epic_link = issue_info.raw['fields'].get("customfield_11040")
        pair_details = issue_info.raw['fields'].get("customfield_12185")
        if pair_details is not None:
            pair = pair_details['displayName']
        else:
            pair = None
        validator = issue_info.raw['fields'].get("customfield_11140")
        time_in_status = issue_info.raw['fields'].get("customfield_10000")
        request_type = issue_info.raw['fields'].get("customfield_12101")
        start_date = issue_info.raw['fields'].get("customfield_12100")
        # print(issue_info.raw['fields'].get("customfield_10440"))
        # 'customfield_12105': '6.0',
        # Status of ticket
        last_status = extract_last_status(sprint.endDate, issue.id)
        # issue_status = issue_info.fields.status.name
        issue_summary = issue_info.fields.summary
        # issue_desc = issue_info.fields.description
        issue_type_name = issue_info.fields.issuetype.name
        labels = issue.fields.labels
        priority = issue_info.fields.priority.name
        reporter = issue_info.fields.reporter.displayName
        parent_details = issue_info.raw['fields'].get('parent')
        if parent_details is not None:
            parent = parent_details['key']
        else:
            parent = None
        due_date = issue_info.raw['fields'].get('duedate')
        # TODO inward and outward issues....
        linked_issues = []
        for linked in issue_info.raw['fields'].get('issuelinks'):
            if linked.get("outwardIssue") is not None:
                linked_issues.append(linked.get("outwardIssue")['key'])
            else:
                linked_issues.append(linked.get("inwardIssue")['key'])
        # linked_issues = [linked.outwardIssue.key for linked in issue_info.fields.issuelinks]
        # subtasks = issue_info.fields.subtasks
        resolution_date = issue_info.fields.resolutiondate
        created_on = issue_info.fields.created
        resolution = issue_info.fields.resolution

        result.append({
            'sprint_id': sprint.id,
            "issuetype": issue_type_name,
            "id": issue.id,
            "key": issue_info.key,
            "labels": labels,
            "summary": issue_summary,
            #"description": issue_desc,
            'status': last_status,
            "assignee": issue_assignee,
            'story_points': issue_story_points,
            "sprint": sprint.name,
            "epic_link": epic_link,
            "pair": pair,
            "validator": validator,
            "time_in_status": time_in_status,
            "request_type": request_type,
            "start_date": start_date,
            "priority": priority,
            "reporter": reporter,
            "parent": parent,
            "due_date": due_date,
            "resolution_date": resolution_date,
            "created_on": created_on,
            "resolution": resolution,
            "linked_issues": linked_issues,
            # "subtasks": subtasks
        })
    jira_issues_df = pd.DataFrame(result)
    return jira_issues_df


def extract_last_status(end_date: str, ticket_id: str) -> str:
    """Go through changelog and extract the last status

    Args:
        end_date: End date of a sprint
        ticket_id: Jira ticket id

    Return:
        Status"""
    username = os.environ['JIRA_USERNAME']
    api_token = os.environ['JIRA_API_TOKEN']
    base_url = 'https://sagebionetworks.jira.com/'
    auth = requests.auth.HTTPBasicAuth(username, api_token)
    timezone = pytz.timezone('UTC')

    # start_datetime = timezone.localize(datetime.datetime.strptime(start_date, "%Y-%m-%d"))
    end_datetime = timezone.localize(datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ"))

    # Set up the request headers with authentication
    headers = {
        "Accept": "application/json"
    }
    url = f"{base_url}/rest/api/3/issue/{ticket_id}/changelog"

    response = requests.get(url, headers=headers, auth=auth)

    if response.status_code == 200:
        data = response.json()
        changes_log_df = pd.DataFrame(pd.DataFrame(data)['values'].tolist())
        changes_log_df['created'] = pd.to_datetime(changes_log_df['created'], utc=True)
        # Get the latest status prior to the closure of a sprint
        change_types = changes_log_df[changes_log_df.created <= end_datetime].sort_values('created', ascending=False)['items']
        for changes in change_types:
            for change in changes:
                if change['field'] == "status":
                    status = change['toString']
                    return status

def get_custom_headers(server='https://sagebionetworks.jira.com/', issue_id='BS-1'):
    username = os.environ['JIRA_USERNAME']
    api_token = os.environ['JIRA_API_TOKEN']
    # base_url = 'https://sagebionetworks.jira.com/'
    auth = requests.auth.HTTPBasicAuth(username, api_token)
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(f"{server}/rest/api/latest/issue/{issue_id}?expand=names", headers=headers, auth=auth)
    data = response.json()
    print(data)
    return data['names']


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
    current_day = datetime.datetime.today()

    for sprint in all_sprints:
        timezone = pytz.timezone('UTC')
        end_datetime = timezone.localize(datetime.datetime.strptime(sprint.endDate, "%Y-%m-%dT%H:%M:%S.%fZ"))
        if (sprint.name.startswith("DPE") and
            "Sprint" not in sprint.name and
            "12.19.22" not in sprint.name and
            end_datetime < timezone.localize(current_day)):
            print(sprint.name, sprint.id, sprint.startDate, sprint.endDate)
            df = get_issues_per_sprint(jira_client=jira_client, sprint=sprint)
            all_sprint_info = pd.concat([all_sprint_info, df])
    all_sprint_info.to_csv("dpe_sprint_info.csv", index=False)


if __name__ == "__main__":
    main()
