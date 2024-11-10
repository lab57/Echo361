import os
import shutil
import sounddevice as sd
import soundfile as sf
from dotenv import load_dotenv
from pydub import AudioSegment
import json
import csv

# Load environment variables
load_dotenv()

def record_audio(duration, sample_rate):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    print("Recording complete.")
    return audio

def save_audio_to_file(audio, sample_rate, file_name):
    sf.write(file_name, audio, sample_rate)
    print(f"Audio saved to file: {file_name}")

def save_segments(audio_file, csv_file, output_dir="segments"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    segments_metadata = []

    # Read segment start times from CSV file
    start_times = []
    if os.path.exists(csv_file):
        print(f"Reading start times from {csv_file}")
        with open(csv_file, newline='') as f:
            reader = csv.reader(f, delimiter='\n')
            next(reader)  # Skip the header row
            for row in reader:
                if row:  # Skip any empty rows
                    try:
                        start_time = float(row[0])
                        start_times.append(start_time)
                        print(f"Read start time: {start_time}")
                    except ValueError:
                        print(f"Could not convert row to float: {row[0]}")
    else:
        print(f"CSV file {csv_file} not found!")
        return
    
    print(f"Total start times read: {len(start_times)}")

    # Process custom cuts from the CSV file
    audio = AudioSegment.from_wav(audio_file)
    for i, start in enumerate(start_times):
        end = start_times[i + 1] if i + 1 < len(start_times) else len(audio) / 1000  # Set end to audio length if last segment
        segment_file = os.path.join(output_dir, f"custom_cut_{i}.wav")
        segment = audio[int(start * 1000):int(end * 1000)]
        segment.export(segment_file, format="wav")
        print(f"Created segment: {segment_file} from {start} to {end}")

        segments_metadata.append({
            "segment_file": segment_file,
            "speaker": "unknown",
            "start": start,
            "end": end
        })

    with open(os.path.join(output_dir, "segments_metadata.json"), "w") as f:
        json.dump(segments_metadata, f, indent=4)

    print(f"Segments and metadata saved to {output_dir}")

def clear_segments_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    print(f"Recreated folder: {folder_path}")

def main():
    segments_directory = "./segments"
    clear_segments_folder(segments_directory)
    
    duration = 10  # Recording duration in seconds
    sample_rate = 16000  # Sample rate in Hz

    audio = record_audio(duration, sample_rate)
    audio_file = "recorded_audio.wav"
    save_audio_to_file(audio, sample_rate, audio_file)

    csv_file = "./output/slide_timestamps.csv"  # Path to the CSV file with start times
    save_segments(audio_file, csv_file)

if __name__ == "__main__":
    main()