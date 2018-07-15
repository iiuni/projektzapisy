#!/usr/bin/env bash

# Install nodejs
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install yarn, needed globally
sudo npm i -g yarn
