import os
from dotenv import load_dotenv
import httpx
from openai import OpenAI
from openai.types.chat import ChatCompletionToolParam
import json
import gradio as gr


load_dotenv(override=True)
openai = OpenAI()

smartsuite_api_key = os.getenv("SMARTSUITE_API_KEY")
smartsuite_account_id = os.getenv("SMARTSUITE_ACCOUNT_ID")


tables = {"CRUD": "687662a8780fb19d5a1277d8", "Blabla": "686e6d12db86cd32da256d86"}


def get_table(tableId):
    url = f"https://app.smartsuite.com/api/v1/applications/{tableId}/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "content-type": "application/json",
    }
    response = httpx.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def create_record(tableId, fields):
    print(f"fields: {fields}")
    url = f"https://app.smartsuite.com/api/v1/applications/{tableId}/records/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "content-type": "application/json",
    }
    response = httpx.post(url, headers=headers, content=json.dumps(fields))
    response.raise_for_status()
    return response.json()


system_prompt = f"""You are a SmartSuite assistant that performs Create Record operations.
You will create a record based on the user's request using the following tables: {tables}.

Before creating a record:
- Retrieve the fields of the specified table.
- Map the user's input to the appropriate fields.

When calling the `create_record` function:
- Extract all user-specified fields (like title, status, due_date, etc.) from get_table tool call
- Nest them under a `fields` object
- Only keep `tableId` at the top level
- use the slugs in fields as it is case sensitive

If no matching field label is found:
- Create a new field.
- Set its label and value based on the user's input.\n
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

tools: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_table",
            "description": "Get the table and it's fields information",
            "parameters": {
                "type": "object",
                "properties": {
                    "tableId": {
                        "type": "string",
                        "description": "The ID of the table (application) to fetch records or fields from.",
                    }
                },
                "required": ["tableId"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_record",
            "description": "Create a record in a given table",
            "parameters": {
                "type": "object",
                "properties": {
                    "tableId": {
                        "type": "string",
                        "description": "The ID of the table (application) to create a record in.",
                    },
                    "fields": {
                        "type": "object",
                        "description": "The fields of the record to create. The fields are the same as the fields of the table.",
                    },
                },
                "required": ["tableId", "fields"],
            },
        },
    },
]

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"arguments: {arguments}")
        print(f"Tool called: {name}", flush=True)
        if name == "get_table":
            result = get_table(**arguments)
            results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
        elif name == "create_record":
            result = create_record(**arguments)
            results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
    return results




def chat(user_message, history):
    print(f"history: {history}")
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": user_message}]
    done = False
    while not done:

        response = openai.chat.completions.create(model="gpt-4.1", messages=messages, tools=tools, tool_choice="auto")

        finish_reason = response.choices[0].finish_reason
        
        # If the LLM wants to call a tool, we do that!
        print(f"finish_reason: {finish_reason}")
         
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            print(message)
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True  
    print(f"response: {response}")
    return response.choices[0].message.content


def main():
    gr.ChatInterface(fn=chat, title="HypePilot SmartSuite Assistant", type="messages").launch()


if __name__ == "__main__":
    main()
