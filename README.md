# to create environment:
first step, upgrade:
* python -m pip install --upgrade pip setuptools virtualenv
second step, create environment:
* python -m venv venv
* source venv/bin/activate
* python -m pip install kivy[base] kivy_examples python-dateutil==2.8.2

* pip install --user --upgrade buildozer

# Require for buildozer:
link for the Buildozer documentation: https://buildozer.readthedocs.io/en/latest/
Linux (the virtual image may not work) or OSX to be able to compile for Android
I am using Linux Mint 21 Xfce which it requires to compile on Android:
Cython==0.29.10  # below how to install
javac [openjdk-8-jdk from apt]
* pip install --user --upgrade Cython==0.29.19 virtualenv  # the --user should be removed if you do this in a venv
* sudo apt update
* sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev
libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

add the following line at the end of your ~/.bashrc file
* export PATH=$PATH:~/.local/bin/

# now we need initialize buildozer and edit the buildozer.spec
* buildozer init

# then run compile process
* buildozer -v android debug
compilation will take a long time

# then connect the phone with turn on developer mode to the usb port, then:
* buildozer -v android deploy run logcat
# I am adding to the end and can see application errors on phone
* "| grep python"
