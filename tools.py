
from agents import FunctionTool
from pydantic_models import EmptyArgs, GetTableArgs, CreateRecordArgs, UrlBuilderArgs
from invokers import run_get_members_tool, run_get_table_tool, run_create_record_tool, run_url_builder_tool


get_table_tool = FunctionTool(
    name="get_table",
    description="Get the table and it's fields information.",
    params_json_schema=GetTableArgs.model_json_schema(),
    on_invoke_tool=run_get_table_tool,
    strict_json_schema=False
)


create_record_tool = FunctionTool(
    name="create_record",
    description="Create a SmartSuite record in a specified table with dynamic fields.",
    params_json_schema=CreateRecordArgs.model_json_schema(),
    on_invoke_tool=run_create_record_tool,
    strict_json_schema=False
)

url_builder_tool = FunctionTool(
    name="url_builder",
    description="Build the url of the created record.",
    params_json_schema=UrlBuilderArgs.model_json_schema(),
    on_invoke_tool=run_url_builder_tool,
    strict_json_schema=False
)

get_members_tool = FunctionTool(
    name="get_members",
    description="Get the list of members of the account.",
    params_json_schema=EmptyArgs.model_json_schema(),
    on_invoke_tool=run_get_members_tool,
    strict_json_schema=False
)
