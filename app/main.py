import os
import json
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from prompts.system_prompt import system_prompt

load_dotenv()

# Gemini client
client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# Tools

def get_medicines():
    result = (
        supabase
        .table("medications")
        .select("id, name, dosage, instructions, start_date, end_date")
        .execute()
    )
    return result.data


def get_medicine_by_name(name):
    result = (
        supabase
        .table("medications")
        .select(
            "id, name, dosage, instructions, start_date, end_date, "
            "medication_schedules(scheduled_time, frequency)"
        )
        .ilike("name", name)
        .execute()
    )

    if not result.data:
        return {"error": "Medicine not found"}

    medicine = result.data[0]
    schedule = medicine.pop("medication_schedules", [])

    if schedule:
        medicine["scheduled_time"] = schedule[0]["scheduled_time"]
        medicine["frequency"] = schedule[0]["frequency"]

    return medicine


def get_current_time():
    return datetime.now().strftime("%H:%M")


def get_due_medicines():
    current_time = datetime.now().strftime("%H:00:00")
    current_date = datetime.now().date().isoformat()

    result = (
        supabase
        .table("medication_schedules")
        .select(
            "scheduled_time, frequency, medications(id, name, dosage, instructions, start_date, end_date)"
        )
        .eq("scheduled_time", current_time)
        .execute()
    )

    due_medicines = []

    for item in result.data:
        medicine = item["medications"]

        if (
            medicine["start_date"] <= current_date
            and (
                medicine["end_date"] is None
                or current_date <= medicine["end_date"]
            )
        ):
            due_medicines.append(item)

    return due_medicines


# Testing helper
def get_due_medicines_at(time):
    result = (
        supabase
        .table("medication_schedules")
        .select(
            "scheduled_time, frequency, medications(id, name, dosage, instructions, start_date, end_date)"
        )
        .eq("scheduled_time", time)
        .execute()
    )
    return result.data


def get_medication_information(name):

    result = (
        supabase
        .table("medications")
        .select(
            "name, dosage, purpose, prescribed_for, instructions, start_date, end_date, "
            "medication_schedules(scheduled_time, frequency)"
        )
        .ilike("name", name)
        .execute()
    )

    if not result.data:
        return {"error": "Medicine not found"}

    medicine = result.data[0]

    schedule = medicine.pop("medication_schedules", [])

    if schedule:
        medicine["scheduled_time"] = schedule[0]["scheduled_time"]
        medicine["frequency"] = schedule[0]["frequency"]

    return medicine


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


get_due_medicines_tool = {
    "type": "function",
    "function": {
        "name": "get_due_medicines",
        "description": "Get the medicines scheduled for the current time.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


get_medication_information_tool = {
    "type": "function",
    "function": {
        "name": "get_medication_information",
        "description": "Get detailed information about a specific medicine, including its purpose and what it was prescribed for.",
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
    get_medicine_by_name_tool,
    get_due_medicines_tool,
    get_medication_information_tool
]


# Map tool names to Python functions
available_tools = {
    "get_medicines": get_medicines,
    "get_medicine_by_name": get_medicine_by_name,
    "get_due_medicines": get_due_medicines,
    "get_medication_information": get_medication_information
}


# Conversation

messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": "What are the medicines i shld take in a day"
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