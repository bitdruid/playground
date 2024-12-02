#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

cwd=$(pwd)
mkdir -p $cwd/chrome

# download and install chromedriver
curl -sSL https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip -o $cwd/chrome/chromedriver_linux64.zip
unzip $cwd/chrome/chromedriver_linux64.zip -d $cwd/chrome/
# install chrome
curl -sSL https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chrome-linux64.zip -o $cwd/chrome/chrome-linux64.zip
unzip $cwd/chrome/chrome-linux64.zip -d $cwd/chrome/
mv $cwd/chrome/chrome-linux64/* $cwd/chrome/
rm -rf $cwd/chrome/chrome-linux64
ln -s $cwd/chrome/chrome /usr/bin/chrome
chmod +x /usr/bin/chrome

# remove trash files
rm $cwd/chrome/chromedriver_linux64.zip
rm $cwd/chrome/chrome-linux64.zip