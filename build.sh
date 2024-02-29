#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Download and extract LibreOffice
echo "Downloading LibreOffice..."
wget -q https://download.documentfoundation.org/libreoffice/stable/24.2.0/deb/x86_64/LibreOffice_24.2.0_Linux_x86-64_deb.tar.gz
tar -xzf LibreOffice_24.2.0_Linux_x86-64_deb.tar.gz

cd LibreOffice_*_Linux_x86-64_deb/DEBS
# Navigate to the DEBS directory

# Install LibreOffice locally
echo "Installing LibreOffice..."
# Create the target directory
mkdir -p "${HOME}/libreoffice"
echo "${HOME}/libreoffice"

# Extract each .deb package into the target directory
for deb in *.deb; do
    dpkg -x "$deb" "${HOME}/libreoffice"
done

# Add the LibreOffice program directory to PATH
echo "export PATH=\$PATH:${HOME}/libreoffice/opt/libreoffice*/program" >> ${HOME}/.profile