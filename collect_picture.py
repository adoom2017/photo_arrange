import filecmp
import getopt
import logging
import os
import shutil
import sys
import time

import exifread
import ffmpeg

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

def mainLoop(path, dst):
    for root, dirs, files in os.walk(path, True):
        for filename in files:
            absolute_file = os.path.join(root, filename)
            f, e = os.path.splitext(absolute_file)
            if e.lower() in ('.jpg', '.png'):
                classifyPictures(absolute_file, dst, e)
            elif e.lower() in ('.mov', '.mp4'):
                classifyVideo(absolute_file, dst)
            else:
                logging.info("%s is not collected." % absolute_file)

def classifyPictures(filename, dst, suffix):
        time=""
        try:
            time = getOrignalDate(filename)
        except Exception:
            logging.info("Can not get time for %s." % filename)
            return

        fold = dst +'\\'+ time.replace(":", "-")[:7]
        dstFileName = fold + '\\'+ time.replace(":", "").replace(" ", "_") + suffix

        i = 1
        while os.path.exists(dstFileName):
            if filecmp.cmp(filename, dstFileName):
                logging.info("%s already exist." % filename)
                return
            else:
                dstFileName = fold + '\\'+ time.replace(":", "").replace(" ", "_") + "_" + str(i) + suffix
                i = i + 1

        logging.info("Collect File %s to %s." % (filename, dstFileName))
        if not os.path.exists(fold):
            os.mkdir(fold)

        shutil.copy2(filename, dstFileName)

def classifyVideo(filename, dst):
    fold = dst + "\\" + "video"
    dstFileName = fold + "\\" + os.path.basename(filename)
    if os.path.exists(dstFileName):
        logging.info("%s already exist." % filename)
        return
    
    if not os.path.exists(fold):
        os.mkdir(fold)

    shutil.copy2(filename, dstFileName)
            
    
def main(argv):
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
     
    logging.basicConfig(filename='collect.log',level=logging.INFO, format=fmt)
    
    input_dir = ""
    output_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print(sys.argv[0] + " -i <inputfile> -o <outputfile>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(sys.argv[0] + " -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_dir = arg
        elif opt in ("-o", "--ofile"):
            output_dir = arg
    
    mainLoop(input_dir, output_dir)

if __name__ == '__main__':
    main(sys.argv[1:])
