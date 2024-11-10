import os
import sounddevice as sd
import soundfile as sf
from pyannote.audio import Pipeline
from dotenv import load_dotenv
from pydub import AudioSegment
import json

# Load environment variables
load_dotenv()

# Check if the Hugging Face token is loaded
hf_token = os.getenv('HF_TOKEN')
if hf_token is None:
    raise ValueError("Hugging Face token not found in environment variables")

# Ensure the TORCH_HOME environmental variable is set
os.environ['TORCH_HOME'] = os.path.expanduser('~/.cache/torch')
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'

def initialize_pipeline(token):
    try:
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

def save_segments(audio_file, diarization, output_dir="segments"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments_metadata = []

    for i, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
        segment_file = os.path.join(output_dir, f"segment_{i}.wav")
        audio = AudioSegment.from_wav(audio_file)
        segment = audio[int(turn.start * 1000):int(turn.end * 1000)]
        segment.export(segment_file, format="wav")

        segments_metadata.append({
            "segment_file": segment_file,
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })

    with open(os.path.join(output_dir, "segments_metadata.json"), "w") as f:
        json.dump(segments_metadata, f, indent=4)

    print(f"Segments and metadata saved to {output_dir}")

def main():
    duration = 30  # Recording duration in seconds
    sample_rate = 16000  # Sample rate in Hz

    audio = record_audio(duration, sample_rate)
    audio_file = "recorded_audio.wav"
    save_audio_to_file(audio, sample_rate, audio_file)

    diarization = diarize_audio(audio_file)
    if diarization is None:
        print("Failed to complete diarization. Exiting.")
        return

    save_segments(audio_file, diarization)

if __name__ == "__main__":
    main()