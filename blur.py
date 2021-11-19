#!/usr/bin/env python

import argparse
import signal
import time

import cv2
import mediapipe as mp
import numpy as np
import pyfakewebcam

def post_processing(mask):
    mask = cv2.dilate(mask, np.ones((10, 10), np.uint8), iterations=1)
    #mask = cv2.blur(mask.astype(float), (30, 30))
    mask = cv2.blur(mask.astype(float), (10, 10))
    return mask

def blur(image):
    return cv2.GaussianBlur(image, (55, 55), 0)

def process(image, selfie_segmentation):
    # output device works in RGB color space
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    mask = selfie_segmentation.process(image).segmentation_mask
    image.flags.writeable = True

    background = blur(image)
    #background = np.zeros(image.shape, dtype=np.uint8)
    #background[:] = (192, 192, 192)

    mask = post_processing(mask)
    mask_inverted = 1 - mask
    for c in range(image.shape[2]):
        image[:,:,c] = image[:,:,c]*mask + background[:,:,c]*mask_inverted

    return cv2.flip(image, 1)

def limit_frequency(f, period=1.):
    time_before = time.time()
    f()
    while (time.time() - time_before) < period:
        time.sleep(0.001)

def run(input_device_name, output_device_name):
    global shutdown_requested

    print("Running backgroundblur...")

    input_device = cv2.VideoCapture(input_device_name)
    #width, height = 1280, 720
    #width, height = 640, 480
    #input_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #input_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    #input_device.set(cv2.CAP_PROP_FPS, 24)

    target_width = int(input_device.get(cv2.CAP_PROP_FRAME_WIDTH))
    target_height = int(input_device.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_device = pyfakewebcam.FakeWebcam(output_device_name, target_width, target_height)

    def frame():
        success, image = input_device.read()
        if not success:
            return
        image = process(image, selfie_segmentation)

        output_device.schedule_frame(image)

    with mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1) as selfie_segmentation:
        while input_device.isOpened() and not shutdown_requested:
            limit_frequency(frame, 1/30.)

    print("Shutting down...")

    input_device.release()

    print("Done.")

def signal_handler(_s, _f):
    global shutdown_requested
    shutdown_requested = True

shutdown_requested = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple background blur for your webcam')
    parser.add_argument('-i', '--input', required=True, help='input video device')
    parser.add_argument('-o', '--output', required=True, help='output video device')
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    run(args.input, args.output)
