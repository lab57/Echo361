import os
import sounddevice as sd
import soundfile as sf
import openai
from pyannote.audio import Pipeline
from dotenv import load_dotenv
from pydub import AudioSegment

# Load environment variables
load_dotenv()

# Check if the API key is loaded
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError("API key not found in environment variables")
print(f"API Key loaded: {api_key[:5]}...")  # Print first 5 characters for security

# Check if the Hugging Face token is loaded
hf_token = os.getenv('HF_TOKEN')
if hf_token is None:
    raise ValueError("Hugging Face token not found in environment variables")

# Set the API key for the OpenAI client
openai.api_key = api_key

# Ensure the TORCH_HOME environmental variable is set
os.environ['TORCH_HOME'] = os.path.expanduser('~/.cache/torch')
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

def initialize_pipeline(token):
    try:
        # Initialize the pyannote pipeline with the correct model name
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)
        print("Pipeline initialized successfully")
        return pipeline
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        return None

pipeline = initialize_pipeline(hf_token)

def record_audio(duration, sample_rate):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording complete.")
    return audio

def save_audio_to_file(audio, sample_rate, file_name):
    sf.write(file_name, audio, sample_rate)
    print(f"Audio saved to file: {file_name}")

def diarize_audio(audio_file):
    if pipeline is None:
        print("Pipeline is not initialized. Exiting diarization.")
        return None

    try:
        print("Starting diarization...")
        diarization = pipeline(audio_file)
        print("Diarization completed successfully.")
        return diarization
    except Exception as e:
        print(f"Error during diarization: {e}")
        return None

def extract_audio_segment(audio_file, start, end):
    try:
        audio = AudioSegment.from_wav(audio_file)
        segment = audio[int(start * 1000):int(end * 1000)]
        segment_file = f"temp_segment_{start}_{end}.wav"
        segment.export(segment_file, format="wav")
        return segment_file
    except Exception as e:
        print(f"Error extracting audio segment: {e}")
        return None

def transcribe_audio(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript['text']
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None

def main():
    duration = 5  # Recording duration in seconds
    sample_rate = 16000  # Sample rate in Hz

    # Record audio
    audio = record_audio(duration, sample_rate)
    audio_file = "recorded_audio.wav"
    save_audio_to_file(audio, sample_rate, audio_file)

    # Perform diarization
    diarization = diarize_audio(audio_file)
    if diarization is None:
        print("Failed to complete diarization. Exiting.")
        return

    transcripts = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segment_file = extract_audio_segment(audio_file, turn.start, turn.end)
        if segment_file:
            transcript = transcribe_audio(segment_file)
            if transcript:
                transcripts.append(f"Speaker {speaker}: {transcript}")

    # Write transcripts to a file
    try:
        with open("transcript.txt", "w") as f:
            f.write("\n".join(transcripts))
        print("Transcription with speaker diarization saved to transcript.txt")
    except Exception as e:
        print(f"Error saving transcripts to file: {e}")

if __name__ == "__main__":
    main()