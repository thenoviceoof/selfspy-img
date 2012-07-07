#!/usr/bin/env python
################################################################################
# selfspy_webcam.py
# photologs through your webcam

import argparse
import daemon

import os
import time
import cv

import Image # PIL

def main_loop(filename_format, data_directory, compression, resize):
    while True:
        timestamp = time.strftime(filename_format)
        path = data_directory + timestamp + '.jpg'

        frame = cv.QueryFrame(cap)
        # BGR is the default colorspace for opencv
        cv.CvtColor(frame,frame, cv.CV_BGR2RGB)
        img = Image.fromstring("RGB", cv.GetSize(frame), frame.tostring())

        if resize:
            img = img.resize(resize)

        f = open(path, "wb")
        img.save(f, 'JPEG', quality=compression)
        f.close()

        time.sleep(args.interval)

if __name__=="__main__":
    # get args
    parser = argparse.ArgumentParser(description='Photolog through your webcam')
    parser.add_argument('-i', '--interval', dest='interval',
                        default=10, type=int,
                        help=('Time interval in seconds between snapshots'))
    parser.add_argument('-s', '--size', dest='size', default='320x240',
                        help=('Size of the stored image in <wxh> format '
                              '(ex. 640x480)'))
    parser.add_argument('-p', '--password', dest='password',
                        default=None, type=str,
                        help=('Passkey with which to encrypt the images, ' 
                              'after optional compression with -c. If '
                              'neither -p nor -n are specified, then '
                              'a passkey will be queried.'))
    parser.add_argument('-np', '--no-password', dest='passwordp', default=False,
                        const=True, action='store_const',
                        help='Overrides -p, stores the images unencrypted')
    parser.add_argument('-c', '--compression', dest='compression',
                        default=70, type=int,
                        help='Parameter for jpeg compression (1-95)')
    parser.add_argument('--dir', dest='dir', default=None,
                        help=('Directory in which to store the images: '
                              'default is ~/.selfspy/photolog/'))
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        const=True, default=False, action='store_const',
                        help='Daemonizes the process')
    parser.add_argument('-f', '--format', dest='format',
                        default='%Y_%m_%dT%H_%M_%S', type=str,
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

    resize = tuple([int(s) for s in args.size.split("x")])[0:2]
    compression = max(1, min(args.compression, 95))

    # do an initial computation
    frame = cv.QueryFrame(cap)
    if cv.GetSize(frame) == resize:
        resize = None

    if args.daemonize:
        with daemon.DaemonContext():
            main_loop(args.format, directory, compression, resize)
    main_loop(args.format, directory, compression, resize)
