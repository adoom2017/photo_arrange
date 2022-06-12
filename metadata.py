#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import os
import time
import exifread

from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core import config as HachoirConfig

from sys import argv, stderr, exit

HachoirConfig.quiet = True

class Metadata:
    def __init__(self, path):
        self.path = path

    def getCreateTime(self):
        parser = createParser(self.path)
        ftime = None
        if parser:
            with parser:
                try:
                    metadata = extractMetadata(parser)
                except Exception as err:
                    logging.error("File %s metadata extraction error: %s." % (self.path, err))
                    metadata = None

            if metadata != None:
                mime_type = metadata.getValues("mime_type")[0]
                if "video" in mime_type:
                    create_times = metadata.getValues("creation_date")
                elif "image" in mime_type:
                    create_times = metadata.getValues("date_time_original")
                else:
                    create_times = None
            else:
                create_times = None

            if len(create_times) > 0:
                ftime = create_times[0].strftime("%Y%m%d_%H%M%S")
        else:
            # try to use another method
            fbyte = open(self.path, 'rb')
            tags = exifread.process_file(fbyte, stop_tag='DateTimeOriginal')

            timeArray = time.strptime(str(tags['EXIF DateTimeOriginal']), "%Y:%m:%d %H:%M:%S")
            ftime = time.strftime("%Y%m%d_%H%M%S", timeArray)

        if not ftime:
            # use last modify time instead of exif create time
            filemt = time.localtime(os.stat(self.path).st_mtime)
            ftime = time.strftime("%Y%m%d_%H%M%S",filemt)

        return ftime
