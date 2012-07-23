#!/usr/bin/env python
################################################################################
# selfspy_img.py
# photologs through your webcam

import argparse
import daemon

import os
import time
import cv

import Image # PIL
import zipfile

def main_loop(filename_format, data_directory, compression, resize, archive,
              verbose):
    if archive:
        archive_path = '%s/webcam_archive.zip' % data_directory
        archive = zipfile.ZipFile(archive_path, 'a', zipfile.ZIP_DEFLATED)

    while True:
        timestamp = time.strftime(filename_format)
        if verbose: print('[i] Taking shot at %s' % timestamp)
        img_path = '%s/webcam/%s.jpg' % (data_directory, timestamp)

        frame = cv.QueryFrame(cap)
        # BGR is the default colorspace for opencv
        cv.CvtColor(frame,frame, cv.CV_BGR2RGB)
        img = Image.fromstring("RGB", cv.GetSize(frame), frame.tostring())

        if resize:
            if verbose: print('[i] Resizing...')
            img = img.resize(resize)

        if verbose: print('[i] Saving to path %s' % img_path)
        f = open(img_path, "wb")
        img.save(f, 'JPEG', quality=compression)
        f.close()

        if archive:
            if verbose: print('[i] Archiving...')
            archive.write(img_path, os.path.basename(img_path))
            os.remove(img_path)

        time.sleep(args.interval)

if __name__=="__main__":
    # get args
    parser = argparse.ArgumentParser(
        description='Photolog through your webcam (and screenshots)')
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
                              'a passkey will be queried. NOT IMPLEMENTED'))
    parser.add_argument('-np', '--no-password', dest='passwordp', default=False,
                        const=True, action='store_const',
                        help='Overrides -p, stores the images unencrypted')

    parser.add_argument('-c', '--compression', dest='compression',
                        default=70, type=int,
                        help=('Parameter for jpeg compression '
                              '(1-95, default 70)'))
    parser.add_argument('-a', '--archive', dest='archive',
                        default=False, const=True, action='store_const',
                        help="Archive the snapshots as they're taken, by "
                        "default in DATA_DIR/webcam_archive.zip (option --dir)")

    parser.add_argument('--dir', dest='dir', default=None,
                        help=('Directory in which to store the images: '
                              'default is ~/.selfspy/photolog/'))
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        default=False, const=True, action='store_const',
                        help='Daemonizes the process')
    parser.add_argument('-f', '--format', dest='format',
                        default='%Y_%m_%dT%H_%M_%S', type=str,
                        help=('Override the file name formatting of the '
                              'generated image files. Note that if you do '
                              'not include a time unit granular enough for '
                              'your interval, your files will be overwritten.'))
    parser.add_argument('-v', '--verbose', dest='verbose',
                        default=False, const=True, action='store_const',
                        help='Display debug and informational messages')
    args = parser.parse_args()

    ########################################
    # argument computation
    cap = cv.CaptureFromCAM(0)
    verbose = args.verbose

    home = os.getenv("HOME")
    if args.dir is None:
        if verbose: print('[i] Using default directory')
        directory = "%s/.selfspy/photolog/" % home
    else:
        directory = args.dir
    webcam_dir = directory + 'webcam/'
    # add screenshot dir here
    if not os.path.exists(webcam_dir):
        if verbose: print('[i] Creating necessary directory')
        os.makedirs(webcam_dir)

    resize = tuple([int(s) for s in args.size.split("x")])[0:2]
    compression = max(1, min(args.compression, 95))

    # do an initial computation
    frame = cv.QueryFrame(cap)
    if cv.GetSize(frame) == resize:
        if verbose: print('[i] No resize necessary')
        resize = None

    if args.daemonize:
        if verbose: print('[i] Daemonizing...')
        with daemon.DaemonContext():
            main_loop(args.format, directory, compression, resize, args.archive,
                      verbose)
    main_loop(args.format, directory, compression, resize, args.archive,
              verbose)
