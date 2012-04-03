#!/usr/bin/python
"""Downloads all missing SAME Radio Shows in MP3 format using wget to the
current directory.
"""

import os
import subprocess

SHOW_NUMBER_LOW = 1
SHOW_NUMBER_HIGH = 999
URL_PATTERN = "http://www.sameradioshow.com/shows/%(filename)s"
WGET_PATH = '/usr/bin/wget'

for x in range(SHOW_NUMBER_LOW, SHOW_NUMBER_HIGH + 1):
    show_number_padded = str(x).zfill(3)
    filename = 'sameradioshow%s.mp3' % show_number_padded

    if os.path.exists(filename):
        # File already exists, skip
        print '%s has already been downloaded, skipping...' % filename
        continue

    url = URL_PATTERN % { 'filename': filename }

    # Execute wget
    proc = subprocess.call([WGET_PATH, url])

print 'Done!'
