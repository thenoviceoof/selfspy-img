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
                        default='%FT%T', type=str,
                        help=('Override the file name formatting of the '
                              'generated image files. Note that if you do '
                              'not include a time unit granular enough for '
                              'your interval, your files will be overwritten.')
    parser.add_argument('-s', '--seperator', dest='seperator',
                        default='')
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
        timestamp = time.strftime(args.format+'.jpg').replace("-","_").replace(":","_")
        path = directory + timestamp
        cv.SaveImage(path, f)
        time.sleep(args.interval)
