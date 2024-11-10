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

# Load environment variables
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found in environment variables")

print(f"API Key loaded: {api_key[:5]}...") # Print first 5 characters for security

# Set the API key for the OpenAI client
client = openai.OpenAI(api_key=api_key)

# Function to transcribe audio using the OpenAI Whisper model
def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def process_audio_files(directory):
    transcript_file = "transcript.txt"
    with open(transcript_file, "w") as f:

        for file_name in os.listdir(directory):
            if file_name.endswith('.wav'):
                file_path = os.path.join(directory, file_name)
                print(f"Processing {file_path}...")

                transcript = transcribe_audio(file_path)

                # Write the file name and transcription to the transcript.txt file
                # f.write(f"\nFile: {file_name}\n")
                f.write(f"{transcript} | ")

                # print(f"Transcription for {file_name} added to transcript.txt")

def main():
    segments_directory = "./segments"  # Directory containing audio segments
    process_audio_files(segments_directory)

if __name__ == "__main__":
    main()