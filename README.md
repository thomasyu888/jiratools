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
1. Run this code in the terminal (assuming you've followed instructions above)

    ```
    conda activate jira
    export JIRA_API_TOKEN="your jira token above
    export JIRA_USERNAME="your sage email"
    python jira_metrics.py
    ```

1. A file named `dpe_sprint_info.csv` will be created, you can view this file in excel.

For more information on how to use the jira API, go [here](https://jira.readthedocs.io/)