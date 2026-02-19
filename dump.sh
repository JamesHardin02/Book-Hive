#!/usr/bin/env bash

# Output file
OUTPUT="codebase_dump.txt"

# Remove old dump if it exists
rm -f "$OUTPUT"

# Run the find command
find . -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/.vscode/*" \
  ! -path "*/.ruff_cache/*" \
  ! -path "*/playwright-report/*" \
  ! -path "*/frontend/test-results/*" \
  ! -path "*/.venv/*" \
  ! -name "package-lock.json" \
  ! -name ".env*" \
  ! -name "$OUTPUT" \
  ! -iregex ".*\.\(jpg\|jpeg\|png\|gif\|bmp\|tiff\|ico\|svg\|webp\)" \
  ! -iregex ".*\.\(mp3\|wav\|flac\|ogg\|m4a\)" \
  ! -iregex ".*\.\(mp4\|mkv\|mov\|avi\|wmv\|webm\)" \
  ! -iregex ".*\.\(zip\|tar\|gz\|rar\|7z\)" \
  ! -iregex ".*\.\(exe\|dll\|so\|bin\|class\)" \
  -exec sh -c '
    FILE="$1"
    echo "===== FILE: ${FILE#./} =====" >> "'"$OUTPUT"'"
    cat "$FILE" >> "'"$OUTPUT"'"
    echo "" >> "'"$OUTPUT"'"
  ' sh {} \;

echo "Codebase exported to $OUTPUT"
