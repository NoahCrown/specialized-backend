#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define LibreOffice version and AppImage URL
APPIMAGE_URL="https://appimages.libreitalia.org/LibreOffice-fresh.full-x86_64.AppImage"

# Download LibreOffice AppImage
echo "Downloading LibreOffice AppImage..."
wget -q -O "${HOME}/LibreOffice.AppImage" "$APPIMAGE_URL"

# Make the AppImage executable
chmod +x "${HOME}/LibreOffice.AppImage"

# Optionally, add a function to run LibreOffice to your .bashrc or .profile for convenience
echo "alias libreoffice='${HOME}/LibreOffice.AppImage'" >> ${HOME}/.bashrc

echo "LibreOffice AppImage download complete. You can run it with ./LibreOffice.AppImage or use the alias 'libreoffice' if you restart your terminal or source your profile/bashrc file."