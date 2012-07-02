#!/usr/bin/env python
################################################################################
# selfspy_webcam.py
# photologs through your webcam

import cv
import time

cv.StartWindowThread()

cv.NamedWindow("capture")

cap = cv.CaptureFromCAM(0)

for i in range(100):
    f = cv.QueryFrame(cap)
    cv.ShowImage("capture", f)
    time.sleep(0.5)
