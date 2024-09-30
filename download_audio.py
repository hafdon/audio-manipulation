import os
import sys
import re
import argparse
import shutil
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError


def check_dependency(command, name):
    """
    Check if a command-line tool is available.
    """
    if shutil.which(command) is None:
        print(f"Error: {name} is not installed or not found in PATH.")
        sys.exit(1)


def validate_youtube_url(url):
    """
    Validate if the provided URL is a valid YouTube URL.
    """
    youtube_regex = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$")
    return youtube_regex.match(url) is not None


def progress_hook(d):
    """
    Hook to display download progress.
    """
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0.0%")
        eta = d.get("eta", "Unknown")
        speed = d.get("_speed_str", "Unknown speed")
        print(f"Downloading: {percent} - ETA: {eta} - Speed: {speed}", end="\r")
    elif d["status"] == "finished":
        print("\nDownload finished, now converting...")


def download_mp3(youtube_url, output_dir, filename_template, audio_quality):
    """
    Download audio from YouTube and convert it to MP3.
    """
    if not validate_youtube_url(youtube_url):
        print("Invalid YouTube URL. Please enter a valid URL.")
        sys.exit(1)

    # Set default output directory
    if not output_dir:
        output_dir = os.getcwd()
    elif not os.path.isdir(output_dir):
        print(f"Output directory '{output_dir}' does not exist.")
        sys.exit(1)

    # Define output template
    if not filename_template:
        filename_template = "%(title)s.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(output_dir, filename_template),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_quality,
            }
        ],
        "noplaylist": True,
        "progress_hooks": [progress_hook],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print("Download and conversion to MP3 completed successfully!")
    except DownloadError as e:
        print(f"DownloadError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download YouTube videos as MP3 files."
    )
    parser.add_argument("url", nargs="?", help="YouTube video URL.")
    parser.add_argument(
        "-o", "--output", help="Output directory (default: current directory)."
    )
    parser.add_argument(
        "-f", "--filename", help="Filename template (default: '%(title)s.%(ext)s')."
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=str,
        default="192",
        help="Audio quality in kbps (default: 192).",
    )
    return parser.parse_args()


def main():
    # Parse command-line arguments
    args = parse_arguments()

    # Check dependencies
    check_dependency("yt-dlp", "yt-dlp")
    check_dependency("ffmpeg", "FFmpeg")

    # Get YouTube URL
    if args.url:
        youtube_url = args.url
    else:
        youtube_url = input("Please enter the YouTube URL: ")

    # Download MP3
    download_mp3(
        youtube_url=youtube_url,
        output_dir=args.output,
        filename_template=args.filename,
        audio_quality=args.quality,
    )


if __name__ == "__main__":
    main()
