# -*- coding: utf-8 -*-

import filecmp
import getopt
import logging
import os
import shutil
import sys
import traceback

import subprocess
import json

VIDEO_FOLD = "video"
PHOTO_FOLD = "photo"
MOVE_FILE = False

PhotoExtNames = ('.jpg','.png','.jpeg')
VedioExtNames = ('.mp4','.mov','.avi')

TimeFlag = u'CreateDate'

def popen(cmd):
    try:
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        popen.wait()
        lines = popen.stdout.readlines()
        output = ""
        for line in lines:
            output += line.decode('utf-8').strip()
        return output
    except BaseException as e:
        logging.exception(e)
        return None

def get_metadata(filename):
    cmd = "exiftool -j " + filename
    result = popen(cmd)
    if result == None:
        return None
    else:
        return json.loads(result)[0]

def getOrignalDate(filename):
    meta = get_metadata(filename)
    if meta == None:
        logging.error("Can not found create date in meta for %s." % filename)
        return None

    if TimeFlag in meta:
        cameraDate = meta[TimeFlag]
    else:
        logging.error("Can not found create date in meta for %s." % filename)
        return None

    return cameraDate

def mainLoop(path):
    logging.info("Process %s." % path)
    for root, dirs, files in os.walk(path, True):
        for filename in files:
            absolute_file = os.path.join(root, filename)
            name, suffix = os.path.splitext(absolute_file)
            if suffix.lower() in PhotoExtNames:
                classifyAll(absolute_file, PHOTO_FOLD)
            elif suffix.lower() in VedioExtNames:
                classifyAll(absolute_file, VIDEO_FOLD)
            else:
                logging.info("File: %s is not collected." % absolute_file)

def copyFile(srcFileName, dstFileName):
    i = 1
    while os.path.exists(dstFileName):
        if filecmp.cmp(srcFileName, dstFileName):
            logging.info("%s already exist." % srcFileName)
            return
        else:
            name, suffix = os.path.splitext(dstFileName)
            dstFileName = name + "_" + str(i) + suffix
            i = i + 1

    print("Collect File %s to %s." % (srcFileName, dstFileName))
    if not os.path.exists(os.path.dirname(dstFileName)):
        os.makedirs(os.path.dirname(dstFileName))
    if MOVE_FILE:
        shutil.move(srcFileName, dstFileName)
    else:
        shutil.copy2(srcFileName, dstFileName)

def classifyAll(srcFileName, dstRootFold):
    time = getOrignalDate(srcFileName)
    if time != None:
        name, suffix = os.path.splitext(srcFileName)
        dstFileName = dstRootFold +'\\'+ time.replace(":", "-")[:7] + '\\'+ time.replace(":", "").replace(" ", "_") + suffix
    else:
        dstFileName = dstRootFold + "\\unclassify" + "\\" + os.path.basename(srcFileName)

    copyFile(srcFileName, dstFileName)
    
def main(argv):
    global VIDEO_FOLD
    global PHOTO_FOLD
    global MOVE_FILE

    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
     
    logging.basicConfig(filename='collect.log', level=logging.INFO, format=fmt)
    
    output_dir = "collect"
    config_dir = "PathProcess.txt"

    try:
        opts, args = getopt.getopt(argv, "hmc:o:", ["help", "move", "config=", "ofile="])
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
        elif opt in ("-m", "--move"):
            MOVE_FILE = True

    if output_dir != "":
        VIDEO_FOLD = output_dir + "\\" + VIDEO_FOLD
        PHOTO_FOLD = output_dir + "\\" + PHOTO_FOLD

    try:
        with open(config_dir, "r") as configFile:
            line = configFile.readline()
            while line:
                mainLoop(str.strip(line))
                line = configFile.readline()
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    main(sys.argv[1:])
