import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing_extensions import Dict
from typing import Any
import httpx
from openai import OpenAI
import gradio as gr
from agents import Agent, FunctionTool, RunContextWrapper, Runner, Tool, trace


load_dotenv(override=True)
openai = OpenAI()

smartsuite_api_key = os.getenv("SMARTSUITE_API_KEY")
smartsuite_account_id = os.getenv("SMARTSUITE_ACCOUNT_ID")


tables = {"CRUD": "687662a8780fb19d5a1277d8", "Blabla": "686e6d12db86cd32da256d86"}

class CreateRecordArgs(BaseModel):
    tableId: str
    fields: Dict[str, Any]

class GetTableArgs(BaseModel):
    tableId: str

class UrlBuilderArgs(BaseModel):
    application_id: str
    id: str

async def run_get_table_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    args = GetTableArgs.model_validate_json(args_json)
    tableId = args.tableId
    print(f"tableId: {context}")
    print(f"args: {args}")
    url = f"https://app.smartsuite.com/api/v1/applications/{tableId}/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "content-type": "application/json",
    }
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

get_table_tool = FunctionTool(
    name="get_table",
    description="Get the table and it's fields information.",
    params_json_schema=GetTableArgs.model_json_schema(),
    on_invoke_tool=run_get_table_tool,
    strict_json_schema=False
)

async def run_create_record_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    args = CreateRecordArgs.model_validate_json(args_json)
    print(f"args: {args}")
    print(f"context: {context}")
    tableId = args.tableId
    fields = args.fields
    print(json.dumps(fields, indent=4))
    # Mock SmartSuite request — replace with your actual API logic
    url = f"https://app.smartsuite.com/api/v1/applications/{tableId}/records/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "Content-Type": "application/json"
    }

    try:
        response = httpx.post(url, headers=headers, content=json.dumps(fields))
        print(f"response: {response.json()}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        message = str(e)
        return f"Failed to create record: {message}"

create_record_tool = FunctionTool(
    name="create_record",
    description="Create a SmartSuite record in a specified table with dynamic fields.",
    params_json_schema=CreateRecordArgs.model_json_schema(),
    on_invoke_tool=run_create_record_tool,
    strict_json_schema=False
)

async def run_url_builder_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    args = UrlBuilderArgs.model_validate_json(args_json)
    tableId = args.application_id
    recordId = args.id
    print(f"args: {args}")
    print(f"context: {context}")
    return f"https://app.smartsuite.com/{smartsuite_account_id}/solution/68110662fc8e5e3d8678d825/{tableId}?editRecord={recordId}"

url_builder_tool = FunctionTool(
    name="url_builder",
    description="Build the url of the created record.",
    params_json_schema=UrlBuilderArgs.model_json_schema(),
    on_invoke_tool=run_url_builder_tool,
    strict_json_schema=False
)




system_prompt = f"""You are a SmartSuite assistant that performs Create Record operations.
You will create a record based on the user's request using the following tables: {tables}.

Before creating a record:
- Retrieve the fields of the specified table using the get_table tool.
- Map the user's input to the appropriate fields.

When calling the `create_record` function:
- Extract all user-specified fields (like title, status, due_date, etc.) from get_table tool call
- Nest them under a `fields` object
- Only keep `tableId` at the top level
- use the slugs in fields as it is case sensitive

When record is created successfully:
- Build the url of the created record using the url_builder tool
- application_id is the id of the table
- id is the id of the created record from create_record tool response
- Return the url of the created record.

If no matching field label is found:
- Create a new field.
- Set its label and value based on the user's input.

If an error occurs while creating the record:
- Extract the error message from the response.
- Respond with a human-friendly explanation of the error.\n
"""

system_prompt += """
The create_record tool requires:
{
  "tableId": "tableId",
  "fields": {
    "field_slug_or_label": "value"
  }
}
All user-provided fields **MUST be nested under `fields`**, not top-level keys."""

system_prompt += """
# example of creating record

curl -X POST https://app.smartsuite.com/api/v1/applications/646536cac79b49252b0f94f5/records/ \
  -H "Authorization: Token YOUR_API_KEY" \
  -H "ACCOUNT-ID: WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  --data '{
  "title": "Record 1",
  "description": {
    "data": {},
    "html": "<div class=\"rendered\">\n    \n</div>"
  },
  "assigned_to": [
    "5dd812b9d8b7863532d3ddd2",
    "5e6ec7dadc8a90f33bcb02c9"
  ],
  "status": {
    "value": "in_progress"
  },
  "due_date": {
    "from_date": {
      "date": "2021-09-03T03:00:00Z",
      "include_time": true
    },
    "to_date": {
      "date": "2021-09-04T03:15:00Z",
      "include_time": true
    },
    "is_overdue": false
  },
  "priority": "1",
  "sef1a6a113": {
    "from_date": {
      "date": "2021-09-01T00:00:00Z",
      "include_time": false
    },
    "to_date": {
      "date": "2021-09-03T00:00:00Z",
      "include_time": false
    }
  }
}'

"""

smartsuite_create_agent_tools: list[Tool] = [get_table_tool, create_record_tool, url_builder_tool]

smartsuite_create_agent = Agent(name="SmartSuite Create Agent", instructions=system_prompt, tools=smartsuite_create_agent_tools)

async def chat(user_message, history):
    with trace("Create Record"):
        response = await Runner.run(smartsuite_create_agent, user_message)
        return response.final_output



def main():
    gr.ChatInterface(fn=chat, title="HypePilot SmartSuite Assistant", type="messages").launch()



import asyncio

if __name__ == "__main__":
    main()
