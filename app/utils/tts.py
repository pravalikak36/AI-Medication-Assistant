import os
import wave

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

tts_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def generate_speech(text, output_file="medimate_response.wav"):

    response = tts_client.models.generate_content(
        model="gemini-3.1-flash-tts-preview",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name="Kore"
                    )
                )
            )
        )
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    with wave.open(output_file, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    return output_file  