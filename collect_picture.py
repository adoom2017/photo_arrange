import filecmp
import getopt
import logging
import os
import shutil
import sys
import time

import exifread
import ffmpeg

VIDEO_FOLD = "video"
UNCLASSIFY_FOLD = "unclassify"
CLASSIFY_FOLD = "photo"

class ReadFailException(Exception):
    pass

def getOrignalDate(filename):
    try:
        fd = open(filename, 'rb')
    except:
        logging.error("Cannot open: %s." % filename)
        raise ReadFailException
    data = exifread.process_file(fd)
    if data:
        try:
            t = data['EXIF DateTimeOriginal']
            return str(t)
        except:
            logging.error("No exif: %s." % filename)
            pass

    return Null

def mainLoop(path):
    logging.info("Process %s." % path)
    for root, dirs, files in os.walk(path, True):
        for filename in files:
            absolute_file = os.path.join(root, filename)
            name, suffix = os.path.splitext(absolute_file)
            if suffix.lower() in ('.jpg', '.png'):
                classifyPictures(absolute_file)
            elif suffix.lower() in ('.mov', '.mp4'):
                classifyVideo(absolute_file)
            else:
                logging.info("%s is not collected." % absolute_file)

def copyFile(filename, dstFileName):
    i = 1
    while os.path.exists(dstFileName):
        if filecmp.cmp(filename, dstFileName):
            logging.info("%s already exist." % filename)
            return
        else:
            name, suffix = os.path.splitext(dstFileName)
            dstFileName = name + "_" + str(i) + suffix
            i = i + 1

    logging.info("Collect File %s to %s." % (filename, dstFileName))
    if not os.path.exists(os.path.dirname(dstFileName)):
        os.makedirs(os.path.dirname(dstFileName))

    shutil.copy2(filename, dstFileName)

def classifyPictures(filename):
        time=""
        try:
            time = getOrignalDate(filename)
        except Exception:
            logging.info("Can not get time for %s." % filename)
            dstFileName = UNCLASSIFY_FOLD + "\\" + os.path.basename(filename)
            copyFile(filename, dstFileName)
            return

        name, suffix = os.path.splitext(filename)
        dstFileName = CLASSIFY_FOLD +'\\'+ time.replace(":", "-")[:7] + '\\'+ time.replace(":", "").replace(" ", "_") + suffix

        copyFile(filename, dstFileName)

def classifyVideo(filename):
    dstFileName = VIDEO_FOLD + "\\" + os.path.basename(filename)
    copyFile(filename, dstFileName)
    
def main(argv):
    global VIDEO_FOLD
    global UNCLASSIFY_FOLD
    global CLASSIFY_FOLD

    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
     
    logging.basicConfig(filename='collect.log',level=logging.INFO, format=fmt)
    
    output_dir = ""
    config_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hc:o:", ["ofile=", "config="])
    except getopt.GetoptError:
        print(sys.argv[0] + " -c <pathfile> -o <outputpath>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(sys.argv[0] + " -c <pathfile> -o <outputpath>")
            sys.exit()
        elif opt in ("-o", "--ofile"):
            output_dir = arg
        elif opt in ("-c", "--config"):
            config_dir = arg

    if output_dir != "":
        VIDEO_FOLD = output_dir + "\\" + VIDEO_FOLD
        UNCLASSIFY_FOLD = output_dir + "\\" + UNCLASSIFY_FOLD
        CLASSIFY_FOLD = output_dir + "\\" + CLASSIFY_FOLD
    
    if config_dir != "":
        pass
    else:
        config_dir = "PathProcess.txt"

    try:
        with open(config_dir, "r") as configFile:
            line = configFile.readline()
            while line:
                mainLoop(str.strip(line))
                line = configFile.readline()
    except:
        print("%s File is not found." % config_dir)

if __name__ == '__main__':
    main(sys.argv[1:])
