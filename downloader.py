import os
import subprocess
import json

# Define the directory where downloads will be stored.
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Removes characters that are invalid for file names."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def download_youtube_video(url: str, quality: str = "720p") -> str | None:
    """
    Downloads and merges a YouTube video using the yt-dlp command-line tool directly,
    forcing a re-encode to guarantee audio inclusion.
    """
    print("--- Starting Video Download with yt-dlp (Forced Re-encode Method) ---")
    try:
        # Step 1: Get video metadata (like the title) using yt-dlp
        info_command = [
            'yt-dlp',
            '--print-json',
            '--quiet',
            url
        ]
        
        print(f"Fetching video metadata for URL: {url}")
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        info_dict = json.loads(result.stdout)
        title = sanitize_filename(info_dict.get('title', 'video'))
        
        # Step 2: Construct the download command
        # Note: We let yt-dlp handle the filename for recoding, then rename it.
        # This is more reliable when temporary files are created.
        temp_filename_template = os.path.join(DOWNLOAD_DIR, f"{title}_temp.%(ext)s")
        final_filename = f"{title}_{quality}.mp4"
        final_path = os.path.join(DOWNLOAD_DIR, final_filename)

        # --- KEY CHANGE IS HERE ---
        # We now use '--recode-video mp4' to force ffmpeg to create a new,
        # compatible MP4 file with both video and audio streams.
        # This is the most reliable method for ensuring audio is present.
        download_command = [
            'yt-dlp',
            '--recode-video', 'mp4',
            '-S', f'res:{quality.replace("p", "")},ext:mp4:m4a', # Sort by resolution and prefer mp4
            '-o', temp_filename_template,
            # No --quiet flag, we want to see all output for debugging
            url
        ]

        print(f"Executing download command: {' '.join(download_command)}")
        
        # Step 3: Run the download command
        subprocess.run(download_command, check=True)

        # After download, yt-dlp will have created a file like "title_temp.mp4".
        # We need to find it and rename it to our desired final filename.
        temp_file_path = os.path.join(DOWNLOAD_DIR, f"{title}_temp.mp4")
        if os.path.exists(temp_file_path):
             os.rename(temp_file_path, final_path)
             print(f"Download and recode complete. File saved at: {final_path}")
             return final_path
        else:
             print(f"Error: Expected temporary file not found at {temp_file_path}")
             # Check for other possible extensions if recoding failed
             for ext in ['.mkv', '.webm']:
                 temp_file_path_alt = os.path.join(DOWNLOAD_DIR, f"{title}_temp{ext}")
                 if os.path.exists(temp_file_path_alt):
                     os.rename(temp_file_path_alt, final_path)
                     print(f"Download complete (container might differ). File saved at: {final_path}")
                     return final_path

        print(f"Error: Expected file not found after download.")
        return None

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running yt-dlp subprocess for video.")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error Output: {e.stderr}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred in download_youtube_video: {e}")
        raise e


def download_youtube_audio(url: str) -> str | None:
    """
    Downloads and converts audio using the yt-dlp command-line tool directly.
    """
    print("--- Starting Audio Download with yt-dlp (Subprocess Method) ---")
    try:
        # Step 1: Get metadata to determine the filename
        info_command = ['yt-dlp', '--print-json', '--quiet', url]
        result = subprocess.run(info_command, capture_output=True, text=True, check=True)
        info_dict = json.loads(result.stdout)
        title = sanitize_filename(info_dict.get('title', 'audio'))
        
        final_path_template = os.path.join(DOWNLOAD_DIR, f"{title}.%(ext)s")
        final_path_mp3 = os.path.join(DOWNLOAD_DIR, f"{title}.mp3")

        # Step 2: Construct and run the download/conversion command
        download_command = [
            'yt-dlp',
            '-x', # Extract audio
            '--audio-format', 'mp3',
            '--audio-quality', '192K',
            '-o', final_path_template,
            '--quiet',
            '--progress',
            url
        ]
        
        print(f"Executing audio download command: {' '.join(download_command)}")
        subprocess.run(download_command, check=True)

        if os.path.exists(final_path_mp3):
            print(f"MP3 conversion successful: {final_path_mp3}")
            return final_path_mp3
        else:
            print(f"Error: Expected file not found at {final_path_mp3}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running yt-dlp subprocess for audio.")
        print(f"Return Code: {e.returncode}")
        print(f"Output: {e.stdout}")
        print(f"Error Output: {e.stderr}")
        raise e
    except Exception as e:
        print(f"An unexpected error occurred in download_youtube_audio: {e}")
        raise e

