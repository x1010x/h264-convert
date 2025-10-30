#!/bin/bash
set -e

#######################################
# Configuration
#######################################
SRC_DIR="."                       # Source directory to scan
DEST_DIR="/store/media/movies/es/"     # Destination for converted files
THREADS=$(nproc)                  # Auto-detect CPU threads
VIDEO_CODEC_OK="h264"        # Skip re-encoding for these codecs

#######################################
# Start
#######################################
echo "🔍 Scanning source: $SRC_DIR"
echo "📦 Destination: $DEST_DIR"
echo "🧠 Using $THREADS CPU threads"
echo

mkdir -p "$DEST_DIR"
shopt -s globstar nullglob

for file in "$SRC_DIR"/**/*.mkv; do
    [ -f "$file" ] || continue

    echo "📂 Checking: $file"

    # Get relative path and create mirror structure in destination
    rel_path="${file#$SRC_DIR/}"
    dest_path="$DEST_DIR/${rel_path%.*}.mp4"
    dest_dir=$(dirname "$dest_path")

    mkdir -p "$dest_dir"

    # Skip if already converted
    if [ -f "$dest_path" ]; then
        echo "⏭️  Skipping (already exists): $dest_path"
        echo
        continue
    fi

    # Get codec info
    vcodec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name \
        -of default=noprint_wrappers=1:nokey=1 "$file" || echo "unknown")
    acodec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name \
        -of default=noprint_wrappers=1:nokey=1 "$file" || echo "unknown")

    # Decide video conversion
    if [[ "$vcodec" =~ ^($VIDEO_CODEC_OK)$ ]]; then
        echo "🎞️  Video codec OK ($vcodec) → copying"
        vopts="-c:v copy"
    else
        echo "🔧 Non-H.264/HEVC video ($vcodec) → re-encoding to H.264"
        vopts="-c:v libx264 -preset medium -crf 26 -threads $THREADS"
    fi

    # Decide audio conversion
    if [[ "$acodec" == "aac" ]]; then
        echo "🎧 Audio codec OK (aac) → copying"
        aopts="-c:a copy"
    else
        echo "🎵 Converting audio ($acodec → aac)"
        aopts="-c:a aac -b:a 128k"
    fi

    echo "⚙️   Processing → $dest_path"
    ffmpeg -hide_banner -stats -y -i "$file" $vopts $aopts -movflags +faststart "$dest_path"

    if [ $? -eq 0 ]; then
        echo "✅ Done: $dest_path"
    else
        echo "❌ Error converting: $file"
        rm -f "$dest_path"  # Clean up partial files
    fi
    echo
done

echo "🏁 All finished!"

