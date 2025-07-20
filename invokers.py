from get_env import getSmartSuiteEnv
from pydantic_models import GetTableArgs, CreateRecordArgs, UrlBuilderArgs
from agents import RunContextWrapper
import httpx
from typing import Any
import json

async def run_get_table_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    smartsuite_api_key, smartsuite_account_id = getSmartSuiteEnv()
    args = GetTableArgs.model_validate_json(args_json)
    tableId = args.tableId
    print(f"context: {context}")
    print(f"args: {args}")
    url = f"https://app.smartsuite.com/api/v1/applications/{tableId}/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "content-type": "application/json",
    }
    try:
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        message = str(e)
        return f"Failed to get table: {message}"

async def run_create_record_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    smartsuite_api_key, smartsuite_account_id = getSmartSuiteEnv()
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


async def run_url_builder_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    smartsuite_account_id = getSmartSuiteEnv()[1]
    args = UrlBuilderArgs.model_validate_json(args_json)
    tableId = args.application_id
    recordId = args.id
    print(f"args: {args}")
    print(f"context: {context}")
    return f"https://app.smartsuite.com/{smartsuite_account_id}/solution/68110662fc8e5e3d8678d825/{tableId}?editRecord={recordId}"


async def run_get_members_tool(context: RunContextWrapper[Any], args_json: str) -> str:
    smartsuite_api_key, smartsuite_account_id = getSmartSuiteEnv()
    print(f"context: {context}")
    url = f"https://app.smartsuite.com/api/v1/members/list/"
    headers = {
        "Authorization": f"Token {smartsuite_api_key}",
        "ACCOUNT-ID": smartsuite_account_id,
        "Content-Type": "application/json"
    }
    try:
        response = httpx.post(url, headers=headers)
        response.raise_for_status()
        members = [
            {"id": member["id"], "fullName": member["full_name"]["sys_root"]}
            for member in response.json()["items"]
            if "email" in member and member["email"]
        ]
        return members
    except Exception as e:
        message = str(e)
        return f"Failed to get members: {message}"