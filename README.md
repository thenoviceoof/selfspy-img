selfspy-webcam
================================================================================

Photolog yourself for fun and profit!

Usage
--------------------------------------------------------------------------------

`./selfspy-webcam.py`


Options
--------------------------------------------------------------------------------

run `./selfspy-webcam.py --help` to find some help, like so:

    ./selfspy_webcam.py --help 
    usage: selfspy_webcam.py [-h] [-i INTERVAL] [-s SIZE] [-p PASSWORD] [-np]
                             [-c COMPRESSION] [-a] [--dir DIR] [-d] [-f FORMAT]

    Photolog through your webcam

    optional arguments:
      -h, --help            show this help message and exit
      -i INTERVAL, --interval INTERVAL
                            Time interval in seconds between snapshots
      -s SIZE, --size SIZE  Size of the stored image in <wxh> format (ex. 640x480)
      -p PASSWORD, --password PASSWORD
                            Passkey with which to encrypt the images, after
                            optional compression with -c. If neither -p nor -n are
                            specified, then a passkey will be queried.
      -np, --no-password    Overrides -p, stores the images unencrypted
      -c COMPRESSION, --compression COMPRESSION
                            Parameter for jpeg compression (1-95, default 70)
      -a, --archive         Archive the snapshots as they're taken, by default in
                            DATA_DIR/webcam_archive.zip (option --dir)
      --dir DIR             Directory in which to store the images: default is
                            ~/.selfspy/photolog/
      -d, --daemonize       Daemonizes the process
      -f FORMAT, --format FORMAT
                            Override the file name formatting of the generated
                            image files. Note that if you do not include a time
                            unit granular enough for your interval, your files
                            will be overwritten.


TODO
--------------------------------------------------------------------------------
 - encryption per-file or per bulk thing (see next)
   - blowfish? (also what vanilla selfspy uses)
   - AES?
 - get screenshots
   - see: stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
   - save this as a png
 - do store on sufficient diff (-t --threshold option)
   - see: cvabsdiff
 - add a lockfile
 - ensure interop (? encryption/zip/tar?)
 - testing?
 - requirements.txt file - test in a virtualenv
 - test with python 3.x