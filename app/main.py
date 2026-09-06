import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Temporary medication data
medications = [
    {
        "name": "Paracetamol",
        "dosage": "500 mg",
        "time": "8:00 AM",
        "instructions": "Take after breakfast"
    },
    {
        "name": "Metformin",
        "dosage": "500 mg",
        "time": "8:00 PM",
        "instructions": "Take after dinner"
    }
]


# Tools
def get_medicines():
    return medications


def get_medicine_by_name(name):
    for medicine in medications:
        if medicine["name"].lower() == name.lower():
            return medicine

    return {"error": "Medicine not found"}


# Tool schemas
get_medicines_tool = {
    "type": "function",
    "function": {
        "name": "get_medicines",
        "description": "Get the user's complete medication list and schedule.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


get_medicine_by_name_tool = {
    "type": "function",
    "function": {
        "name": "get_medicine_by_name",
        "description": "Get the details of a medicine by its name.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the medicine."
                }
            },
            "required": ["name"]
        }
    }
}


tools = [
    get_medicines_tool,
    get_medicine_by_name_tool
]


# Map tool names to Python functions
available_tools = {
    "get_medicines": get_medicines,
    "get_medicine_by_name": get_medicine_by_name
}


# Conversation
messages = [
    {
        "role": "system",
        "content": """
        You are an AI Medication Assistant.

        Use the available tools whenever medication information is required.
        Only use information returned by the tools.
        Never invent medication information or change prescribed dosages.
        """
    },
    {
        "role": "user",
        "content": "Give me the details of both Paracetamol and Metformin."
    }
]


# Tool-calling loop
while True:

    response = client.chat.completions.create(
        model="gemini-3.1-flash-lite",
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    if not message.tool_calls:
        print(message.content)
        break

    messages.append(message)

    for tool_call in message.tool_calls:

        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        function_to_call = available_tools[function_name]

        tool_result = function_to_call(**arguments)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(tool_result)
        })