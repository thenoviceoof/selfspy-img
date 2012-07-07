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
    parser.add_argument('-i', '--interval', dest='interval', default=10,
                        type=int,
                        help=('Time interval in seconds between snapshots'))
    parser.add_argument('-s', '--size', dest='size', default='320x240',
                        help=('Size of the stored image in <wxh> format '
                              '(ex. 640x480)'))
    parser.add_argument('-p', '--password', dest='password', default=None,
                        type=str,
                        help=('Passkey with which to encrypt the images, ' 
                              'after optional compression with -c. If '
                              'neither -p nor -n are specified, then '
                              'a passkey will be queried.'))
    parser.add_argument('-n', '--no-password', dest='passwordp', default=False,
                        const=True, action='store_const',
                        help='Overrides -p, stores the images unencrypted')
    parser.add_argument('-nc', '--no-compress', dest='compress', default=True,
                        const=False, action='store_const',
                        help='Disables compression on the images')
    parser.add_argument('--dir', dest='dir', default=None,
                        help=('Directory in which to store the images: '
                              'default is ~/.selfspy/photolog/'))
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        const=True, default=False, action='store_const',
                        help='Daemonizes the process')
    parser.add_argument('-f', '--format', dest='format',
                        default='%Y-%m-%dT%H-%M-%S', type=str,
                        help=('Override the file name formatting of the '
                              'generated image files. Note that if you do '
                              'not include a time unit granular enough for '
                              'your interval, your files will be overwritten.'))
    args = parser.parse_args()

    ########################################
    # start photologging
    cap = cv.CaptureFromCAM(0)

    home = os.getenv("HOME")
    if args.dir is None:
        directory = "%s/.selfspy/photolog/" % home
    else:
        directory = args.dir
    if not os.path.exists(directory):
        os.makedirs(directory)

    size = tuple([int(s) for s in args.size.split("x")])[0:2]

    # do an initial computation
    frame = cv.QueryFrame(cap)
    if cv.GetSize(frame) == size:
        resize = False
    else:
        resize = True

    # run the main event loop
    while True:
        frame = cv.QueryFrame(cap)
        if resize:
            resized = cv.CreateMat(size[1], size[0], cv.CV_8UC3)
            cv.Resize(frame, resized)
            frame = resized

        timestamp = time.strftime(args.format+'.jpg')

        cv.SaveImage(directory + timestamp, resized)
        time.sleep(args.interval)
