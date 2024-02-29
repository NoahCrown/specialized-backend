#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Download and extract LibreOffice
echo "Downloading LibreOffice..."
wget -q https://www.libreoffice.org/donate/dl/deb-x86_64/24.2.0/en-US/LibreOffice_24.2.0_Linux_x86-64_deb.tar.gz
tar -xzf LibreOffice_24.2.0_Linux_x86-64_deb.tar.gz

# Navigate to the DEBS directory
cd LibreOffice_24.2.0_Linux_x86-64_deb/DEBS

# Install LibreOffice locally
echo "Installing LibreOffice..."
dpkg -x *.deb ${HOME}/libreoffice

# Navigate back to the original directory
cd ../../..

# Add LibreOffice program directory to PATH (modify .profile or similar)
echo "export PATH=\$PATH:${HOME}/libreoffice/opt/libreoffice*/program" >> ${HOME}/.profile