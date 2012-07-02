#!/usr/bin/env python
################################################################################
# selfspy_webcam.py
# photologs through your webcam

import os
import cv
import time

cv.StartWindowThread()

cap = cv.CaptureFromCAM(0)

home = os.getenv("HOME")

for i in range(2):
    f = cv.QueryFrame(cap)
    timestamp = time.strftime("%FT%T.jpg").replace("-","_").replace(":","_")
    path = "%s/.selfspy/photolog/%s" % (home, timestamp)
    cv.SaveImage(path, f)
    time.sleep(2)
