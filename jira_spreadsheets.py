import os
from typing import List

from atlassian import Jira
import pandas as pd


class JiraUtils:
    def __init__(self, username: str = None, api_token: str = None):
        self.username = username or os.environ['JIRA_USERNAME']
        self.api_token = api_token or os.environ['JIRA_API_TOKEN']
    
    def client(self):
        jira_client = Jira(
            url='https://sagebionetworks.jira.com/',
            username=self.username,
            password=self.api_token,
            cloud=True
        )
        return jira_client
    
    def get_jira_issues_for_epic(self, epic_id: str) -> pd.DataFrame:
        """Get JIRA issues under a JIRA epic and convert to df

        Args:
            epic_id (str): JIRA EPIC id

        Returns:
            pd.DataFrame: dataframe of JIRA issues
        """
        jira = self.client()
        issues_under_epic = jira.epic_issues(epic=epic_id)
        epic_details = jira.get_issue(issue_id_or_key=epic_id)
        result = [
            {
                'epic': epic_id,
                "issuetype": epic_details['fields']['issuetype']['name'],
                "target_start": epic_details['fields']['customfield_12113'],
                "key": epic_details['key'],
                "summary": epic_details['fields']['summary'],
                "description": epic_details['fields']['description'],
                'status': epic_details['fields']['status']['name'],
                "assignee": epic_details['fields']['assignee']['displayName'],
                "sprint": None,
                "due_date": epic_details['fields']['duedate']
            }
        ]
        for issue in issues_under_epic['issues']:
            key = issue['key']
            # priority = issue['fields']['priority']['name']
            if issue['fields']['sprint'] is not None:
                sprint = issue['fields']['sprint']['name']
            else:
                sprint = None
            
            if issue['fields']['assignee'] is not None:
                assignee = issue['fields']['assignee']['displayName']
            else:
                assignee = None
            due_date = issue['fields']['duedate']
            # story_points = issue['fields']['customfield_10014']
            status = issue['fields']['status']['name']
            summary = issue['fields']['summary']
            description = issue['fields']['description']
            issue_type = issue['fields']['issuetype']['name']
            target_start = issue['fields']['customfield_12113']
            result.append({
                'epic': epic_id,
                "issuetype": issue_type,
                "key": key,
                "summary": summary,
                "description": description,
                'status': status,
                "assignee": assignee,
                "sprint": sprint,
                "target_start": target_start,
                "due_date": due_date
            })
        jira_issues_df = pd.DataFrame(result)
        return jira_issues_df

    def get_jira_issues_for_epics(self, epic_ids: List[str]) -> pd.DataFrame:
        """Get JIRA issues under a list of JIRA epics and convert to df

        Args:
            epic_ids (List[str]): List of JIRA epic ids

        Returns:
            pd.DataFrame: dataframe of JIRA issues
        """
        jira_issues_df = pd.DataFrame()
        for epic_id in epic_ids:
            issue_df = self.get_jira_issues_for_epic(epic_id)
            jira_issues_df = pd.concat([jira_issues_df, issue_df])
        return jira_issues_df