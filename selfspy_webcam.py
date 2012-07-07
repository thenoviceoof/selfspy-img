#!/usr/bin/env python
################################################################################
# selfspy_webcam.py
# photologs through your webcam

import argparse

import os
import time
import cv

if __name__=="__main__":
    # get args
    parser = argparse.ArgumentParser(description='Photolog through your webcam')
    parser.add_argument('-i', '--interval', dest='interval', default=5,
                        type=int, help=('Time interval in seconds between '
                                        'snapshots'))
    parser.add_argument('-s', '--size', dest='size', default='320x240',
                        type=str, help=('Size of the stored image in <wxh> '
                                        'format (ex. 640x480)'))
    parser.add_argument('-p', '--password', dest='password', default=None,
                        help='')
    parser.add_argument('--dir', dest='dir', default=None,
                        help='')
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        const=True, default=False, action='store_const',
                        help='Enable automatic daemonization')
    args = parser.parse_args()

    # start photologging
    cap = cv.CaptureFromCAM(0)

    home = os.getenv("HOME")
    if args.dir is None:
        directory = "%s/.selfspy/photolog/" % home
    else:
        directory = args.dir
    if not os.path.exists(directory):
        os.makedirs(directory)

    while True:
        f = cv.QueryFrame(cap)
        timestamp = time.strftime("%FT%T.jpg").replace("-","_").replace(":","_")
        path = directory + timestamp
        cv.SaveImage(path, f)
        time.sleep(args.interval)
