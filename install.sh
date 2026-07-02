#!/bin/bash

# Set alias for DroidRemote3
echo "alias DroidRemote3='python3 /data/data/com.termux/files/usr/bin/DroidRemote3.py'" >> ~/.bashrc
source ~/.bashrc

# Install dependencies
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Set up the framework
cp -r * /data/data/com.termux/files/home/DroidRemote3/
cd /data/data/com.termux/files/home/DroidRemote3/

# Start the web server
python3 DroidRemote3.py
