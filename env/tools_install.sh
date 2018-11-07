#!/usr/bin/env bash

apt-get -y install git
apt-get -y install libpq-dev
apt-get -y install unzip
apt-get -y install libxml2-dev libxslt1-dev
apt-get -y install libc6-dev
apt-get -y install libjpeg62-dev
apt-get -y install libfreetype6-dev
apt-get -y install xvfb
apt-get -y install firefox # This package is apparently installed to get the requirements for the firefox we get in firefox_and_geckodriver_setup.sh
apt-get -y install memcached
