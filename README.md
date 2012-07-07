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
 - per-file or per bulk thing (see next)
   - blowfish? (also what vanilla selfspy uses)
   - AES?
 - rotation/bulk compression (.tar.gz or .zip)
   - see: zipfile, tarfile, shutil.make_archive (all in standard lib)
 - get screenshots
   - see: stackoverflow.com/questions/69645/take-a-screenshot-via-a-python-script-linux
   - save this as a png
 - do store on sufficient diff (-t --threshold option)
   - see: cvabsdiff
 - ensure interop
 - testing?
 - requirements.txt file - test in a virtualenv
