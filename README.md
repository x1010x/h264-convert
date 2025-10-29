# h264-convert
A python script to convert video files to h264/MP4 format for better media server compatibility.

## Requirements

- Python 3
- ffmpeg

## Usage

```bash
python3 convert_to_h264.py --source SOURCE_DIR --destination DEST_DIR --archive ARCHIVE_DIR
```

## Parameters

- `--source` or `-s`: Directory containing original video files
- `--destination` or `-d`: Directory for converted MP4 files
- `--archive` or `-a`: Directory to store original files after conversion
- `--log` or `-l`: Log file name (optional, default: conversion.log)
- `--progress` or `-p`: Progress file name (optional, default: conversion_progress.json)

## Example

```bash
python3 convert_to_h264.py -s /incoming/movies/ -d /media/movies/ -a /archive/
```

## Features

- Scans source directory for video files
- Skips files already in h264 format
- Converts to h264 with CRF 18 quality
- Preserves all audio and subtitle streams
- Maintains original resolution
- Moves original files to archive after successful conversion
- Creates conversion log with timestamps
- Resumes interrupted conversions
