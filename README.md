# jiratools
This is a set of jira scripts that will gather JIRA stats or create spreadsheets

```
pip install atlassian-python-api pandas
```


## Usage

1. Make sure to create a JIRA api token and set them as environmental variables
2. Run this code

    ```
    import jira_spreadsheets
    jc = jira_spreadsheets.JiraUtils()
    jira_issues_df = jc.get_jira_issues_for_epics(epic_ids = ["ORCA-1", "ORCA-12"])
    ```