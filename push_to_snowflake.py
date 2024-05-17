from dotenv import dotenv_values
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
import synapseclient
import pandas as pd

syn = synapseclient.login()

config = dotenv_values(".env")

ctx = snowflake.connector.connect(
    user=config['user'],
    password=config['password'],
    account=config['snowflake_account'],
    database="sage",
    schema="DPE",
    role="SYSADMIN",
    warehouse="compute_xsmall"
)

cs = ctx.cursor()
ent_df = pd.read_csv("dpe_sprint_info.csv")

write_pandas(
    ctx,
    ent_df,
    "jira_metrics",
    auto_create_table=True,
    overwrite=True,
    quote_identifiers=False
)
