import asyncio
import sounddevice as sd
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

live_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

SAMPLE_RATE = 16000
BLOCK_SIZE = 1600
MIC_DEVICE = 1


async def get_voice_input():

    config = types.LiveConnectConfig(
        response_modalities=["TEXT"],
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                disabled=True
            )
        ),
        input_audio_transcription=types.AudioTranscriptionConfig()
    )

    async with live_client.aio.live.connect(
        model="gemini-3.5-transcribe-live",
        config=config
    ) as session:

        print("🎤 Speak now...")

        await session.send_realtime_input(
            activity_start=types.ActivityStart()
        )

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=BLOCK_SIZE,
            device=MIC_DEVICE
        ) as stream:

            for _ in range(150):  # ~15 seconds

                audio_chunk, _ = stream.read(BLOCK_SIZE)

                await session.send_realtime_input(
                    audio=types.Blob(
                        data=audio_chunk.tobytes(),
                        mime_type="audio/pcm;rate=16000"
                    )
                )

        await session.send_realtime_input(
            activity_end=types.ActivityEnd()
        )

        print("⏳ Processing...")

        transcript = ""

        try:

            async with asyncio.timeout(15):

                async for response in session.receive():

                    if (
                        response.server_content
                        and response.server_content.input_transcription
                    ):

                        text = response.server_content.input_transcription.text

                        if text:
                            transcript += text

        except TimeoutError:
            pass

        return transcript.strip()