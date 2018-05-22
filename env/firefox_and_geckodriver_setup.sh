#!/usr/bin/env bash

# install firefox45 and geckodriver for selenium
wget --no-verbose https://ftp.mozilla.org/pub/firefox/releases/45.0/linux-x86_64/en-US/firefox-45.0.tar.bz2
tar -xjf firefox-45.0.tar.bz2
sudo rm -rf  /opt/firefox
sudo mv firefox /opt/firefox45
sudo ln -s /opt/firefox45/firefox /usr/bin/firefox

wget --no-verbose https://github.com/mozilla/geckodriver/releases/download/v0.13.0/geckodriver-v0.13.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/
