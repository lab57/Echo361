import sounddevice as sd
import soundfile as sf
import numpy as np
import openai
import os
from openai import OpenAI
from pyannote.audio import Pipeline
import torch
from pydub import AudioSegment
# The API key is now set as an environment variable, so we don't need to set it explicitly in the code

from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found in environment variables")

print(f"API Key loaded: {api_key[:5]}...") # Print first 5 characters for security

# Set the API key for the OpenAI client
client = openai.OpenAI(api_key=api_key)

# Rest of your code...

def record_audio(duration, sample_rate):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording complete.")
    return audio

def transcribe_audio(audio, sample_rate):
    # Save the audio to a temporary file
    temp_file = "temp_audio.wav"
    sf.write(temp_file, audio, sample_rate)

    # Transcribe using OpenAI Whisper model
    client = openai.OpenAI()  # Initialize the client
    with open(temp_file, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

    # Remove the temporary file
    # os.remove(temp_file)

    return transcript.text

def main():
    duration = 5  # Recording duration in seconds
    sample_rate = 16000  # Sample rate in Hz

    audio = record_audio(duration, sample_rate)
    transcript = transcribe_audio(audio, sample_rate)

    with open("transcript.txt", "w") as f:
        f.write(transcript)

    print("Transcription saved to transcript.txt")

if __name__ == "__main__":
    main()