# jiratools
This is a set of jira scripts that will gather JIRA stats or create spreadsheets


## Getting started

These instructions are more mac OS.

1. Install [miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/)
1. After this is installed, open up "terminal".  Click the magnifying glass on the top right corner and type terminal and click it.
1. Create your conda environment

    ```
    conda create -n jira python=3.10
    conda activate jira
    ```

1. Install your Python dependencies

    ```
    pip install jira pandas ipython
    ```


## Usage


1. Make sure to create a JIRA api token: https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
1. Run this code from the terminal by typing in `ipython`

    ```
    from jira import JIRA
    username = "@sagebase.org"
    api_token = "..."
    jira_client = JIRA(
        server='https://sagebionetworks.jira.com/',
        basic_auth=(username, api_token)
    )
    issue = jira_client.issue('JRA-9')
    print(issue.fields.project.key)
    print(issue.fields.issuetype.name)
    print(issue.fields.reporter.displayName)
    ```

1. Try to run this query

    ```
    TODO: this is TBD
    # project in (IBCDPE) AND (status changed to (closed) after '2023/02/12') AND (status changed to (closed) before '2023/02/28') and type not in (subTaskIssueTypes(), epic)

    # Sprint = 539 AND type not in (subTaskIssueTypes(), epic)
    ```

1. For more information on how to use the jira API, go [here](https://jira.readthedocs.io/)