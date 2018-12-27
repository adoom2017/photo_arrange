import shutil
import os
import time
import exifread
import filecmp
import getopt
import sys
import logging
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

    return null

def classifyPictures(path, dst):
    for root, dirs, files in os.walk(path, True):
        dir = []
        for filename in files:
            filename = os.path.join(root, filename)
            f, e = os.path.splitext(filename)
            if e.lower() not in ('.jpg', '.png'):
                logging.info("%s is not collected." % filename)
                continue

            t=""
            try:
                t = getOrignalDate(filename)
            except Exception:
                logging.info("Can not get time for %s." % filename)
                continue

            fold = t.replace(":", "-")[:7]
            pwd = dst +'\\'+ fold
            dst_name = pwd + '\\'+ t.replace(":", "").replace(" ", "_") + e

            i = 1
            while os.path.exists(dst_name):
                if filecmp.cmp(filename, dst_name):
                    logging.info("%s already exist." % filename)
                    break
                else:
                    dst_name = pwd + '\\'+ t.replace(":", "").replace(" ", "_") + "_" + str(i) + e
                i = i + 1

            logging.info("Collect File %s to %s." % (filename, dst_name))
            if not os.path.exists(pwd):
               os.mkdir(pwd)

            shutil.copy2(filename, dst_name)
            #os.remove(filename)

def classifyVideo(path, dst):
    for root, dirs, files in os.walk(path, True):
        dir = []
        for filename in files:
            filename = os.path.join(root, filename)
            f, e = os.path.splitext(filename)
            if e.lower() not in ('.mov', '.mp4'):
                logging.info("%s is not collected." % filename)
                continue

            pwd = dst + "\\" + "video"
            if not os.path.exists(pwd):
               os.mkdir(pwd)

            shutil.copy2(filename, pwd)
            
    
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
    
    classifyPictures(input_dir, output_dir)
    classifyVideo(input_dir, output_dir)

if __name__ == '__main__':
    main(sys.argv[1:])
