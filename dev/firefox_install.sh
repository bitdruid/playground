#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

cwd=$(pwd)
mkdir -p $cwd/firefox

# download and install firefoxdriver
curl -sSL https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz -o $cwd/firefox/geckodriver.tar.gz
tar -xzf $cwd/firefox/geckodriver.tar.gz -C $cwd/firefox/
rm $cwd/firefox/geckodriver.tar.gz

# install firefox
curl -sSL https://ftp.mozilla.org/pub/firefox/releases/127.0/linux-x86_64/en-US/firefox-127.0.tar.bz2 -o $cwd/firefox/firefox.tar.bz2
tar -xjf $cwd/firefox/firefox.tar.bz2 -C $cwd/firefox/
rm $cwd/firefox/firefox.tar.bz2

# create symbolic link for firefox
ln -s $cwd/firefox/firefox /usr/bin/firefox
chmod +x /usr/bin/firefox