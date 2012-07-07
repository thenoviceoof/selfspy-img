selfspy-webcam
================================================================================

Photolog yourself for fun and profit!

Usage
--------------------------------------------------------------------------------

`./selfspy-webcam.py`


Options
--------------------------------------------------------------------------------

run `./selfspy-webcam.py --help` to find some help


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