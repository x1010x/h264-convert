#!/usr/bin/env python3

import os
import subprocess
import json
import shutil
import argparse
from datetime import datetime
from pathlib import Path

def log_message(message, log_file):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    print(formatted_message)
    with open(log_file, "a") as f:
        f.write(f"{formatted_message}\n")

def load_progress(progress_file):
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            return json.load(f)
    return {"completed": [], "failed": []}

def save_progress(progress, progress_file):
    with open(progress_file, "w") as f:
        json.dump(progress, f, indent=2)

def is_h264(file_path):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "csv=p=0", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == "h264"
    except:
        return False

def get_video_files(source_dir):
    extensions = [".avi", ".mkv", ".mp4", ".mov", ".wmv", ".flv", ".webm"]
    files = []
    for ext in extensions:
        files.extend(Path(source_dir).rglob(f"*{ext}"))
    return [str(f) for f in files if f.is_file()]

def convert_file(input_path, output_path):
    cmd = [
        "ffmpeg", "-i", input_path,
        "-c:v", "libx264", "-crf", "18",
        "-preset", "faster",
        "-c:a", "copy", "-c:s", "copy",
        "-map", "0", "-y", output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_video_info(file_path):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-select_streams", "v:0", "-show_entries", "stream=codec_name,width,height", "-of", "csv=p=0", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        parts = result.stdout.strip().split(',')
        if len(parts) >= 3:
            return parts[0], f"{parts[1]}x{parts[2]}"
        return "unknown", "unknown"
    except:
        return "unknown", "unknown"

def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.2f} GB"

def main():
    parser = argparse.ArgumentParser(description='Convert videos to h264/MP4 format')
    parser.add_argument('--source', '-s', required=True, help='Source directory with video files')
    parser.add_argument('--destination', '-d', required=True, help='Destination directory for converted files')
    parser.add_argument('--archive', '-a', required=True, help='Archive directory for original files')
    parser.add_argument('--log', '-l', default='conversion.log', help='Log file name')
    parser.add_argument('--progress', '-p', default='conversion_progress.json', help='Progress file name')

    args = parser.parse_args()

    source_dir = args.source
    dest_dir = args.destination
    archive_dir = args.archive
    log_file = args.log
    progress_file = args.progress

    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    progress = load_progress(progress_file)
    video_files = get_video_files(source_dir)
    total_files = len(video_files)

    log_message(f"Found {total_files} video files in {source_dir}", log_file)

    for index, file_path in enumerate(video_files, 1):
        file_name = os.path.basename(file_path)

        if file_path in progress["completed"] or file_path in progress["failed"]:
            continue

        log_message(f"[{index}/{total_files}] Processing: {file_name}", log_file)

        codec, resolution = get_video_info(file_path)
        original_size = os.path.getsize(file_path)
        log_message(f"  Detected: {codec} codec at {resolution}", log_file)
        log_message(f"  Original size: {format_size(original_size)}", log_file)

        if is_h264(file_path):
            log_message(f"  Already h264, skipping", log_file)
            progress["completed"].append(file_path)
            save_progress(progress, progress_file)
            continue

        output_name = os.path.splitext(file_name)[0] + ".mp4"
        rel_path = os.path.relpath(file_path, source_dir)
        output_path = os.path.join(dest_dir, os.path.dirname(rel_path), output_name)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if os.path.exists(output_path):
            log_message(f"  Output exists, skipping: {output_name}", log_file)
            continue

        log_message(f"  Converting {codec} -> h264/MP4 at {resolution}", log_file)
        log_message(f"  Output: {output_path}", log_file)

        if convert_file(file_path, output_path):
            new_size = os.path.getsize(output_path)
            size_diff = new_size - original_size
            diff_percent = ((new_size - original_size) / original_size) * 100

            log_message(f"  Conversion successful!", log_file)
            log_message(f"  New size: {format_size(new_size)}", log_file)
            log_message(f"  Size difference: {format_size(abs(size_diff))} ({'+'if size_diff >= 0 else '-'}{abs(diff_percent):.1f}%)", log_file)

            archive_path = os.path.join(archive_dir, file_name)
            shutil.move(file_path, archive_path)
            log_message(f"  Original moved to: {archive_path}", log_file)

            progress["completed"].append(file_path)
        else:
            log_message(f"  Conversion failed!", log_file)
            progress["failed"].append(file_path)

        save_progress(progress, progress_file)

    log_message("Conversion complete!", log_file)

if __name__ == "__main__":
    main()
