import requests
import os

API_KEY = os.getenv("API_KEY")
TRANSCRIPTION_REQUEST_URL = os.getenv("TRANSCRIPTION_REQUEST_URL")
OUTPUT_DIR = os.getenv("OUTPUT_DIR")


def transcribe_audio(file_path, api_key):
    try:
        # Open the audio file in binary mode
        with open(file_path, "rb") as audio_file:
            # Prepare the headers and data
            headers = {"Authorization": f"Bearer {api_key}"}
            files = {
                "file": (
                    os.path.basename(file_path),
                    audio_file,
                    "application/octet-stream",
                )
            }
            data = {"model": "whisper-1"}
            # Send POST request to the OpenAI API
            response = requests.post(
                TRANSCRIPTION_REQUEST_URL,
                headers=headers,
                files=files,
                data=data,
            )

        # Check the response
        if response.status_code == 200:
            transcript = response.json()
            return transcript["text"]
        else:
            print(
                f"Request failed with status code {response.status_code}: {response.text}"
            )
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def transcribe_segments(folder_path, API_KEY):
    transcripts = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".mp3") and filename.startswith("segment_"):
            file_path = os.path.join(folder_path, filename)
            print(f"Transcribing {file_path}...")
            transcription = transcribe_audio(file_path, API_KEY)
            if transcription:
                transcripts.append(transcription)
            else:
                print(f"Failed to transcribe {filename}")
    return transcripts


full_transcript_list = transcribe_segments(output_dir, API_KEY)

# Combine transcripts
combined_transcript = " ".join(full_transcript_list)

# Specify the output text file path
output_text_file = os.path.join(output_dir, "transcript.txt")

# Write the combined transcript to the text file
with open(output_text_file, "w", encoding="utf-8") as f:
    f.write(combined_transcript)

print(f"\nFull transcription has been written to {output_text_file}")
