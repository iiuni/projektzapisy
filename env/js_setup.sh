#!/usr/bin/env bash

# Install nodejs
curl -sL https://deb.nodesource.com/setup_9.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install yarn, needed globally
sudo npm i -g yarn

# Create node dir outside VM shared folder for Windows compatibility
# (npm uses symlinks and they don't work inside the shared folder on Windows)
# Do it in this script because we need root
cd /vagrant/zapisy
./webpack_resources/create_modules_dir.sh ubuntu
