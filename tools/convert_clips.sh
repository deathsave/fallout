#!/usr/bin/env bash
# Converts video clips to the Ogg Theora (.ogv) Godot plays, scaled to
# 1920x1080 (letterboxed), into videos/rads_multiball/.
#
#   tools/convert_clips.sh clip1.mp4 clip2.mkv ...
#   tools/convert_clips.sh -t 8 clip.mp4      # keep only the first 8 seconds
#   tools/convert_clips.sh -s 1:23 -t 6 clip.mp4   # 6 s starting at 1:23
#   tools/convert_clips.sh -c 800:800:560:140 rec.mov
#       crop to an 800x800 box whose top-left is at x=560, y=140 (in the
#       recording's pixels) - e.g. just the Vault Boy from a Pip-Boy capture
set -euo pipefail

out_dir="$(cd "$(dirname "$0")/.." && pwd)/videos/rads_multiball"
start="" dur="" crop=""
while getopts "s:t:c:" opt; do
    case $opt in
        s) start=$OPTARG ;;
        t) dur=$OPTARG ;;
        c) crop="crop=$OPTARG," ;;
        *) echo "usage: $0 [-s start] [-t seconds] [-c w:h:x:y] files..." >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))
[ $# -gt 0 ] || { echo "usage: $0 [-s start] [-t seconds] [-c w:h:x:y] files..." >&2; exit 1; }

if ! ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libtheora; then
    echo "this ffmpeg has no Theora encoder (Homebrew's stock build doesn't)." >&2
    echo "install one that does, e.g.:" >&2
    echo "  brew tap homebrew-ffmpeg/ffmpeg && brew install homebrew-ffmpeg/ffmpeg/ffmpeg" >&2
    echo "or on the Ubuntu cabinet: sudo apt install ffmpeg" >&2
    exit 1
fi

mkdir -p "$out_dir"
for f in "$@"; do
    name="$(basename "${f%.*}")"
    args=()
    [ -n "$start" ] && args+=(-ss "$start")
    [ -n "$dur" ] && args+=(-t "$dur")
    ffmpeg -hide_banner -loglevel error -y ${args[@]+"${args[@]}"} -i "$f" \
        -vf "${crop}scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" \
        -c:v libtheora -q:v 7 -c:a libvorbis -q:a 4 -ac 2 -ar 44100 \
        "$out_dir/$name.ogv"
    echo "wrote videos/rads_multiball/$name.ogv"
done
