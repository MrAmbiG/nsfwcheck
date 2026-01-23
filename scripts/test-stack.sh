#!/bin/bash

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
TEST_DIR=${TEST_DIR:-"tests"}
URL_FILE="$TEST_DIR/urls.txt"

echo "--------------------------------------------------------"
echo "Running nsfwcheck stack tests..."
echo "API URL: $API_URL"
echo "Waiting for API to be ready..."

# Wait up to 30 seconds for the API
timeout=30
while ! curl -s "$API_URL/health" > /dev/null; do
    echo -n "."
    sleep 1
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo -e "\nError: API did not become ready in time."
        exit 1
    fi
done
echo -e "\nAPI is ready!"
echo "--------------------------------------------------------"

# 1. Test URLs from tests/urls.txt
if [ -f "$URL_FILE" ]; then
    echo "Checking URLs in $URL_FILE..."
    while IFS= read -r url || [ -n "$url" ]; do
        # Skip empty lines and comments
        [[ -z "$url" || "$url" =~ ^# ]] && continue

        echo -n "Checking URL [$url]: "
        result=$(curl -s -S -X POST -F "url=$url" "$API_URL/check/url")
        if [ $? -eq 0 ]; then
            echo "$result"
        else
            echo "FAILED to connect to API"
        fi
    done < "$URL_FILE"
    echo "--------------------------------------------------------"
else
    echo "Warning: $URL_FILE not found, skipping URL checks."
fi

# 2. Test Images in tests/
echo "Checking images in $TEST_DIR..."
# Iterate over common image extensions
# Use a temporary flag to see if we found any images
found_images=false
for img in "$TEST_DIR"/*.{jpg,jpeg,png,webp,gif,svg}; do
    # Check if the glob matched anything (skip if it didn't)
    [ -e "$img" ] || continue

    found_images=true
    filename=$(basename "$img")
    echo -n "Checking Image [$filename]: "

    # Send image to API
    result=$(curl -s -S -X POST -F "image=@$img" "$API_URL/check/image")

    if [ $? -eq 0 ]; then
        echo "$result"
    else
        echo "FAILED to connect to API"
    fi
done

if [ "$found_images" = false ]; then
    echo "No images found in $TEST_DIR."
fi

echo "--------------------------------------------------------"
echo "Tests complete."
