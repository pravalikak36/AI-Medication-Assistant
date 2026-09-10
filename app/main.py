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


# --------------------------------------------------
# Tools
# --------------------------------------------------


def get_medicines():

    result = (
        supabase
        .table("medications")
        .select(
            """
            id,
            name,
            dosage,
            purpose,
            prescribed_for,
            instructions,
            medication_schedules(
                id,
                dose_quantity,
                dose_unit,
                scheduled_time,
                frequency_type,
                frequency_count,
                frequency_unit,
                duration_value,
                duration_unit,
                day_of_week,
                meal_relation,
                meal_offset_minutes,
                start_date,
                end_date
            )
            """
        )
        .execute()
    )

    medicines = []

    for medicine in result.data:

        schedules = medicine.pop("medication_schedules", [])

        medicine["schedules"] = schedules

        medicines.append(medicine)

    return medicines


def get_medicine_by_name(name):

    result = (
        supabase
        .table("medications")
        .select(
            """
            id,
            name,
            dosage,
            purpose,
            prescribed_for,
            instructions,
            medication_schedules(
                id,
                dose_quantity,
                dose_unit,
                scheduled_time,
                frequency_type,
                frequency_count,
                frequency_unit,
                duration_value,
                duration_unit,
                day_of_week,
                meal_relation,
                meal_offset_minutes,
                start_date,
                end_date
            )
            """
        )
        .ilike("name", name)
        .execute()
    )

    if not result.data:
        return {"error": "Medicine not found"}

    medicine = result.data[0]

    schedules = medicine.pop("medication_schedules", [])

    medicine["schedules"] = schedules

    return medicine


def get_medicines_by_day(day):

    current_date = datetime.now().date().isoformat()

    result = (
        supabase
        .table("medication_schedules")
        .select(
            """
            id,
            medication_id,
            dose_quantity,
            dose_unit,
            scheduled_time,
            frequency_type,
            frequency_count,
            frequency_unit,
            duration_value,
            duration_unit,
            day_of_week,
            meal_relation,
            meal_offset_minutes,
            start_date,
            end_date,
            medications(
                id,
                name,
                dosage,
                purpose,
                prescribed_for,
                instructions
            )
            """
        )
        .execute()
    )

    medicines = []

    for item in result.data:

        start_date = item["start_date"]
        end_date = item["end_date"]

        if start_date and current_date < start_date:
            continue

        if end_date and current_date > end_date:
            continue

        if item["day_of_week"]:
            if item["day_of_week"].lower() != day.lower():
                continue

        elif (
            item["frequency_type"] == "times_per"
            and item["frequency_unit"] == "week"
        ):
            continue

        medicine = item["medications"]

        medicines.append({
            "medicine_id": medicine["id"],
            "name": medicine["name"],
            "dosage": medicine["dosage"],
            "purpose": medicine["purpose"],
            "prescribed_for": medicine["prescribed_for"],
            "instructions": medicine["instructions"],
            "schedule": {
                "schedule_id": item["id"],
                "dose_quantity": item["dose_quantity"],
                "dose_unit": item["dose_unit"],
                "scheduled_time": item["scheduled_time"],
                "frequency_type": item["frequency_type"],
                "frequency_count": item["frequency_count"],
                "frequency_unit": item["frequency_unit"],
                "duration_value": item["duration_value"],
                "duration_unit": item["duration_unit"],
                "day_of_week": item["day_of_week"],
                "meal_relation": item["meal_relation"],
                "meal_offset_minutes": item["meal_offset_minutes"],
                "start_date": item["start_date"],
                "end_date": item["end_date"]
            }
        })

    return medicines


def get_medicines_by_time(time):

    current_date = datetime.now().date().isoformat()
    current_day = datetime.now().strftime("%A")

    result = (
        supabase
        .table("medication_schedules")
        .select(
            """
            id,
            medication_id,
            dose_quantity,
            dose_unit,
            scheduled_time,
            frequency_type,
            frequency_count,
            frequency_unit,
            duration_value,
            duration_unit,
            day_of_week,
            meal_relation,
            meal_offset_minutes,
            start_date,
            end_date,
            medications(
                id,
                name,
                dosage,
                purpose,
                prescribed_for,
                instructions
            )
            """
        )
        .eq("scheduled_time", time)
        .execute()
    )

    medicines = []

    for item in result.data:

        start_date = item["start_date"]
        end_date = item["end_date"]

        if start_date and current_date < start_date:
            continue

        if end_date and current_date > end_date:
            continue

        if item["day_of_week"]:

            if item["day_of_week"].lower() != current_day.lower():
                continue

        elif (
            item["frequency_type"] == "times_per"
            and item["frequency_unit"] == "week"
        ):
            continue

        medicine = item["medications"]

        medicines.append({
            "medicine_id": medicine["id"],
            "name": medicine["name"],
            "dosage": medicine["dosage"],
            "purpose": medicine["purpose"],
            "prescribed_for": medicine["prescribed_for"],
            "instructions": medicine["instructions"],
            "schedule": {
                "schedule_id": item["id"],
                "dose_quantity": item["dose_quantity"],
                "dose_unit": item["dose_unit"],
                "scheduled_time": item["scheduled_time"],
                "frequency_type": item["frequency_type"],
                "frequency_count": item["frequency_count"],
                "frequency_unit": item["frequency_unit"],
                "duration_value": item["duration_value"],
                "duration_unit": item["duration_unit"],
                "day_of_week": item["day_of_week"],
                "meal_relation": item["meal_relation"],
                "meal_offset_minutes": item["meal_offset_minutes"],
                "start_date": item["start_date"],
                "end_date": item["end_date"]
            }
        })

    return medicines


def get_due_medicines():

    now = datetime.now()

    current_date = now.date()
    current_time = now.strftime("%H:00:00")
    current_day = now.strftime("%A")

    result = (
        supabase
        .table("medication_schedules")
        .select(
            """
            id,
            medication_id,
            dose_quantity,
            dose_unit,
            scheduled_time,
            frequency_type,
            frequency_count,
            frequency_unit,
            duration_value,
            duration_unit,
            day_of_week,
            meal_relation,
            meal_offset_minutes,
            start_date,
            end_date,
            medications(
                id,
                name,
                dosage,
                purpose,
                prescribed_for,
                instructions
            )
            """
        )
        .eq("scheduled_time", current_time)
        .execute()
    )

    due_medicines = []

    for item in result.data:

        start_date = item["start_date"]
        end_date = item["end_date"]

        # Check whether the medicine is active today

        if start_date and current_date.isoformat() < start_date:
            continue

        if end_date and current_date.isoformat() > end_date:
            continue

        # Check specific weekday

        day_of_week = item["day_of_week"]

        if day_of_week and day_of_week != current_day:
            continue

        # Check every N days schedule

        if (
            item["frequency_type"] == "every"
            and item["frequency_unit"] == "day"
        ):

            start = datetime.fromisoformat(start_date).date()

            days_passed = (current_date - start).days

            if days_passed % item["frequency_count"] != 0:
                continue

        medicine = item["medications"]

        due_medicines.append({
            "medicine_id": medicine["id"],
            "name": medicine["name"],
            "dosage": medicine["dosage"],
            "purpose": medicine["purpose"],
            "prescribed_for": medicine["prescribed_for"],
            "instructions": medicine["instructions"],
            "schedule": {
                "schedule_id": item["id"],
                "dose_quantity": item["dose_quantity"],
                "dose_unit": item["dose_unit"],
                "scheduled_time": item["scheduled_time"],
                "frequency_type": item["frequency_type"],
                "frequency_count": item["frequency_count"],
                "frequency_unit": item["frequency_unit"],
                "duration_value": item["duration_value"],
                "duration_unit": item["duration_unit"],
                "day_of_week": item["day_of_week"],
                "meal_relation": item["meal_relation"],
                "meal_offset_minutes": item["meal_offset_minutes"],
                "start_date": item["start_date"],
                "end_date": item["end_date"]
            }
        })

    return due_medicines


# --------------------------------------------------
# Tool schemas
# --------------------------------------------------


get_medicines_tool = {
    "type": "function",
    "function": {
        "name": "get_medicines",
        "description": "Get the user's complete medication list with all schedules.",
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
        "description": "Get complete information about a medicine, including dosage, purpose, instructions, and all schedules.",
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


get_medicines_by_day_tool = {
    "type": "function",
    "function": {
        "name": "get_medicines_by_day",
        "description": "Get medicines scheduled for a particular day of the week.",
        "parameters": {
            "type": "object",
            "properties": {
                "day": {
                    "type": "string",
                    "description": "Day of the week."
                }
            },
            "required": ["day"]
        }
    }
}


get_medicines_by_time_tool = {
    "type": "function",
    "function": {
        "name": "get_medicines_by_time",
        "description": "Get medicines scheduled for a particular time.",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "Time in HH:MM:SS format."
                }
            },
            "required": ["time"]
        }
    }
}


get_due_medicines_tool = {
    "type": "function",
    "function": {
        "name": "get_due_medicines",
        "description": "Get medicines that are due right now using the current date and time.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


tools = [
    get_medicines_tool,
    get_medicine_by_name_tool,
    get_medicines_by_day_tool,
    get_medicines_by_time_tool,
    get_due_medicines_tool
]


# --------------------------------------------------
# Map tool names to Python functions
# --------------------------------------------------


available_tools = {
    "get_medicines": get_medicines,
    "get_medicine_by_name": get_medicine_by_name,
    "get_medicines_by_day": get_medicines_by_day,
    "get_medicines_by_time": get_medicines_by_time,
    "get_due_medicines": get_due_medicines
}


# --------------------------------------------------
# Conversation
# --------------------------------------------------


messages = [
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": "What are the medicines I should take in a day?"
    }
]


# --------------------------------------------------
# Tool-calling loop
# --------------------------------------------------


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