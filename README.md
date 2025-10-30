# h264-convert
Video conversion scripts to optimize files for better media server compatibility with h264/MP4 format.

## Requirements

- Python 3 (for convert.py)
- ffmpeg
- bash (for convert.sh)

## Scripts

### convert.py - Advanced Python Script
Full-featured conversion with progress tracking and archiving.

```bash
python3 convert.py --source SOURCE_DIR --destination DEST_DIR --archive ARCHIVE_DIR
```

### convert.sh - Simple Bash Script
Lightweight conversion for current directory processing.

```bash
./convert.sh
```

## Parameters (convert.py)

- `--source` or `-s`: Directory containing original video files
- `--destination` or `-d`: Directory for converted MP4 files
- `--archive` or `-a`: Directory to store original files after conversion
- `--log` or `-l`: Log file name (optional, default: conversion.log)
- `--progress` or `-p`: Progress file name (optional, default: conversion_progress.json)

## Examples

### Python Script
```bash
python3 convert.py -s /incoming/movies/ -d /media/movies/ -a /archive/
```

### Bash Script
```bash
# Edit SRC_DIR and DEST_DIR in script, then run:
./convert.sh
```

## Features

### Both Scripts
- Optimized h264 encoding (CRF 26, medium preset)
- Smart codec detection (skips optimal files)
- Converts non-AAC audio to 128k AAC
- CPU thread optimization
- Web-optimized MP4 output (faststart)

### convert.py Additional Features
- Progress tracking and resume capability
- Detailed logging with timestamps
- Automatic archiving of originals
- File size comparison reporting
- Recursive directory scanning
- Multiple video format support

### convert.sh Additional Features
- Mirror directory structure in destination
- Lightweight with minimal dependencies
- Real-time processing feedback
