backgroundblur
==============

Simple background blur for your webcam.


## Installation (venv)

    python -m venv venv
    source venv/bin/activate
    
    pip install -r requirements.txt


## Setup video device

    sudo modprobe v4l2loopback exclusive_caps=1 devices=1 video_nr=20 card_label=backgroundblur

There should now be a new video device under `/dev/video20`.


## Run

    ./blur.py --input /dev/video0 --output /dev/video20


Tested with python 3.9.7
