from pydub import AudioSegment
import os

def split_mp3(input_file, output_folder, max_size_mb=250, bitrate='192k'):
    # Load the audio file
    audio = AudioSegment.from_mp3(input_file)

    # Convert max size from MB to bytes
    max_size_bytes = max_size_mb * 1024 * 1024

    # Bitrate in bits per second, assuming standard bitrates like '192k'
    bitrate_kbps = int(bitrate.replace('k', ''))
    bitrate_bps = bitrate_kbps * 1000

    # Calculate the approximate duration of each segment in milliseconds
    segment_duration_ms = (max_size_bytes * 8 * 1000) / bitrate_bps

    # Create output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Split and export audio segments
    start = 0
    segment_count = 0
    while start < len(audio):
        end = start + segment_duration_ms
        segment = audio[start:end]
        output_file = os.path.join(output_folder, f"segment_{segment_count}.mp3")
        segment.export(output_file, format="mp3", bitrate=bitrate)
        print(f"Exported {output_file}")
        start = end
        segment_count += 1

# Example usage
input_mp3 = '/Users/starkat/audio2/input.mp3'
output_dir = '/Users/starkat/audio/'
split_mp3(input_mp3, output_dir, max_size_mb=23, bitrate='192k')
