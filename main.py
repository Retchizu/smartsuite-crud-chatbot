
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, Tool, trace
from tools import get_members_tool, get_table_tool, create_record_tool, url_builder_tool
from prompts import create_record_prompt
import gradio as gr


load_dotenv(override=True)
openai = OpenAI()

# SmartSuite Create Record Agent
smartsuite_create_agent_tools: list[Tool] = [get_table_tool, create_record_tool, url_builder_tool, get_members_tool]
smartsuite_create_agent = Agent(name="SmartSuite Create Agent", instructions=create_record_prompt, tools=smartsuite_create_agent_tools)

async def chat(user_message, history):
    with trace("Create Record"):
        response = await Runner.run(smartsuite_create_agent, user_message)
        return response.final_output

def main():
    gr.ChatInterface(fn=chat, title="HypePilot SmartSuite Assistant", type="messages").launch()

if __name__ == "__main__":
    main()
