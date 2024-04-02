#!/bin/bash

# Directory where fonts will be installed
FONT_DIR="$HOME/.fonts"

echo "Creating font directory if it doesn't exist"
mkdir -p $FONT_DIR

echo "Copying fonts to font directory"
cp helpers/.fonts*.ttf $FONT_DIR/

echo "Updating font cache"
fc-cache -fv