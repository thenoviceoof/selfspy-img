#!/usr/bin/env python
################################################################################
# selfspy_img.py
# photologs through your webcam

import argparse
import daemon
import os
import sys
import time
import getpass

import math

import Image # PIL
import zipfile
from encrypt.EncryptedFile import EncryptedFile


################################################################################
# utilities

def debug(msg):
    print("[i] " + msg)

def error(msg):
    print("[ERROR] " + msg)
    sys.exit(1)


################################################################################
# main

def get_webcam_img(cv, cap):
    '''
    cv: because not imported into the top level
    cap: keep this guy around
    '''
    def shot():
        frame = cv.QueryFrame(cap)
        # BGR is the default colorspace for opencv
        cv.CvtColor(frame,frame, cv.CV_BGR2RGB)
        webcam_img = Image.fromstring("RGB", cv.GetSize(frame), frame.tostring())
        return webcam_img
    return shot

def get_gtk_screenshot(gtk):
    '''
    gtk: because not imported into the top level
    '''
    def screenshot():
        w = gtk.gdk.get_default_root_window()
        size = w.get_size()
        pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8,
                            size[0], size[1])
        pb = pb.get_from_drawable(w, w.get_colormap(), 0,0,0,0,
                                  size[0], size[1])
        # something has gone wrong, abort
        if pb is None:
            return None
        # handle non-4x rows
        pxs = pb.get_pixels()
        if len(pxs) != size[0]*size[1]*3:
            new = ''
            stride = int(math.ceil(len(pxs)/size[1])/4.)*4
            for i in range(size[1]):
                start = i*stride
                new += pxs[start:start+3*size[0]]
            pxs = new
        screen_img = Image.fromstring("RGB", (size[0], size[1]),
                                      pxs)
        return screen_img
    return screenshot

def get_save(path, getter, file_type='JPEG', resize=False,
             compression=None, archive=None, password=None):
    '''
    path: save to
    getter: function to retrieve image with
    file_type: PIL save as
    resize: False, no resizing, otherwise (w,h)
    compression: compression factor
    archive: whether or not to archive the image after saving
    password: passphrase with which to save the image
    '''
    if verbose: debug('Retrieving file...')
    img = getter()
    if img is None:
        if verbose: debug('No Image handed back, aborting...')
        return

    if resize:
        if verbose: debug('Resizing...')
        img = img.resize(resize)

    if verbose: debug('Opening file...')
    f = open(path, "wb")

    if password:
        if verbose: debug('Encrypting image...')
        f = EncryptedFile(f, passphrase=password, mode='wb',
                          encryption_algo=EncryptedFile.ALGO_BLOWFISH)
    img.save(f, file_type, quality=compression)
    f.close()

    if archive:
        if verbose: debug('Archiving...')
        archive = zipfile.ZipFile(archive, 'a', zipfile.ZIP_DEFLATED)
        archive.write(path, os.path.basename(path))
        archive.close()
        os.remove(path)


def main_loop(filename_format, data_directory, compression, webcam_resize,
              screen_resize, archive, password, verbose, interval):

    # do an initial computation
    if webcam_resize:
        import cv
        cap = cv.CaptureFromCAM(0)

        frame = cv.QueryFrame(cap)
        if cv.GetSize(frame) == webcam_resize:
            if verbose: debug('No resize necessary')
            webcam_resize = False

    if screen_resize:
        import gtk.gdk
        if screen_resize == 1.0:
            screen_resize = False
        else:
            img = get_gtk_screenshot(gtk)()
            screen_resize = [int(s*screen_resize) for s in img.size]

    # make sure the zipfile is still there
    if archive:
        archive = '%s/images_archive.zip' % data_directory

    while True:
        timestamp = time.strftime(filename_format)
        if verbose: debug('Taking shot at %s' % timestamp)

        if webcam_resize is not None:
            webcam_img_path = '%s/webcam/%s.jpg' % (data_directory, timestamp)
            if password:
                webcam_img_path += '.gpg'
            get_save(webcam_img_path, get_webcam_img(cv, cap), 'JPEG',
                     webcam_resize, compression, archive, password)

        if screen_resize is not None:
            screen_img_path = '%s/screenshot/%s.png' % (data_directory, timestamp)
            if password:
                screen_img_path += '.gpg'
            get_save(screen_img_path, get_gtk_screenshot(gtk), 'PNG',
                     screen_resize, 9, archive, password)

        if verbose: debug('Done, sleeping...')
        time.sleep(args.interval)


################################################################################
# pre-loop

if __name__=="__main__":
    # get args
    parser = argparse.ArgumentParser(
        description='Photolog through your webcam (and screenshots)')

    parser.add_argument('-i', '--interval', dest='interval',
                        default=10, type=int,
                        help=('Time interval in seconds between snapshots'))
    parser.add_argument('-ws', '--webcam-size', dest='webcam_size',
                        default='320x240',
                        help=('Size of the stored image in <wxh> format '
                              '(ex. 640x480)'))
    parser.add_argument('-ss', '--screeshot-size', dest='screenshot_size',
                        default=1.0, type=float,
                        help=('Size of the stored image in percentage'))

    # encryption stuff
    parser.add_argument('-p', '--password', dest='password',
                        default=None, type=str,
                        help=('Passkey with which to encrypt the images, ' 
                              'after optional compression with -c. If '
                              'neither -p nor -n are specified, then '
                              'a passkey will be queried.'))
    parser.add_argument('-np', '--no-password', dest='passwordp', default=True,
                        const=False, action='store_const',
                        help='Overrides -p, stores the snapshots unencrypted')

    # sources
    parser.add_argument('-nw', '--no-webcam', dest='webcam', default=True,
                        const=False, action='store_const',
                        help="Don't query the webcam for snapshots")
    parser.add_argument('-ns', '--no-screenshot', dest='screen', default=True,
                        const=False, action='store_const',
                        help="Don't query GTK for snapshots")

    # compression settings
    parser.add_argument('-c', '--compression', dest='compression',
                        default=70, type=int,
                        help=('Parameter for jpeg compression '
                              '(1-95, default 70)'))
    parser.add_argument('-a', '--archive', dest='archive',
                        default=False, const=True, action='store_const',
                        help="Archive the snapshots as they're taken, by "
                        'default in DATA_DIR/webcam_archive.zip (option --dir)')

    # various overall settings
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
    verbose = args.verbose
    webcamp = args.webcam
    screenp = args.screen

    if webcamp:
        if verbose: debug('Using webcam source')
    if screenp:
        if verbose: debug('Using GTK screenshot source')
    if not webcamp and not screenp:
        print("ERROR: You need to have at least one source")
        sys.exit(1)

    # directories
    home = os.getenv("HOME")
    if args.dir is None:
        if verbose: debug('Using default directory')
        directory = "%s/.selfspy/photolog/" % home
    else:
        directory = args.dir
    if webcamp:
        webcam_dir = directory + 'webcam/'
        if not os.path.exists(webcam_dir):
            if verbose: debug('Creating necessary directory')
            os.makedirs(webcam_dir)
    if screenp:
        screen_dir = directory + 'screenshot/'
        if not os.path.exists(screen_dir):
            if verbose: debug('Creating necessary directory')
            os.makedirs(screen_dir)

    # precomute some stuff
    compression = max(1, min(args.compression, 95))
    webcam_resize = None
    screen_resize = None
    if webcamp:
        webcam_resize = tuple([int(s) for s in args.webcam_size.split("x")])[0:2]
        if verbose: debug('Resizing webcam output to %dx%d' % webcam_resize)
    if screenp:
        screen_resize = args.screenshot_size
        if verbose: debug('Resizing screenshots to %f' % screen_resize)

    # password
    if not args.passwordp:
        password = None
    else:
        if args.password:
            password = args.password
        else:
            password = getpass.getpass()

    # let's get this party started
    if args.daemonize:
        if verbose: debug('Daemonizing...')
        with daemon.DaemonContext():
            main_loop(args.format, directory, compression,
                      webcam_resize, screen_resize, args.archive,
                      password, verbose, args.interval)
    main_loop(args.format, directory, compression, webcam_resize, screen_resize,
              args.archive, password, verbose, args.interval)
