# -*- coding: utf-8 -*-

import filecmp
import getopt
import logging
import os
import shutil
import sys
import traceback
import exifread
import re
import json

import hachoir
from hachoir import core
from hachoir import metadata
from hachoir import parser
from hachoir import stream
from hachoir import subfile

MOVE_FILE = False

ImageExtNames = ('.jpg','.png','.jpeg')
VideoExtNames = ('.mp4','.mov','.avi')

def get_image_original_time(filename):
    """
    用于图片创建时间获取
    :param filename: 待获取文件名
    :return: 输出格式YYYYMMDD_hhmmss
    """
    matchRex = re.match(r"(\d*)_(\d*)_(\d*)_(\d*)_(\d*)_IMG_(\d\d)", os.path.basename(filename))
    if matchRex != None:
        return matchRex.group(1)+matchRex.group(2)+matchRex.group(3)+"_"\
            +matchRex.group(4)+matchRex.group(5)+matchRex.group(6)

    with open(filename, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        if 'EXIF DateTimeOriginal' in tags:
            time = str(tags['EXIF DateTimeOriginal'])
            return time.replace(":", "").replace(" ", "_")
        
    return None

def get_video_original_time(filename):
    """
    用于视频创建时间获取
    :param filename: 待获取文件名
    :return: 输出格式YYYYMMDD_hhmmss
    """

    myChar = 'Creation date'
    timePosition = 8
    parserFile = parser.createParser(filename) #解析文件
    if not parserFile:
        print("Unable to parse file - {}\n".format(filename))
        return False
    try:
        metadataDecode = metadata.extractMetadata(parserFile)  # 获取文件的metadata
    except ValueError:
        print('Metadata extraction error.')
        metadataDecode = None
        return False

    if not metadataDecode:
        print("Unable to extract metadata.")
        return False

    myList = metadataDecode.exportPlaintext(line_prefix="") # 将文件的metadata转换为list,且将前缀设置为空

    for i in range(1, len(myList) + 1):
        # 如果字符串在列表中,则提取数字部分,即为文件创建时间
        if myChar in myList[i-1]:
            fileTime = re.sub(r"\D",'',myList[i-1])    #使用正则表达式将列表中的非数字元素剔除
            a=list(fileTime)                           #将文件创建时间字符串转为列表list
            a.insert(timePosition,'_')                 #将列表插入下划线分割date与time
            fileFinalTime = "".join(a)                 #重新将列表转为字符串

            print("The {0} is: {1}".format(myChar,fileFinalTime))
            return fileFinalTime

def copyFile(srcFileName, dstFileName):
    """
    复制文件，整理名称
    :param srcFileName: 原文件名
    :param dstRootFold: 目标文件名
    :return: 
    """

    i = 1
    name, suffix = os.path.splitext(dstFileName)
    while os.path.exists(dstFileName):
        if filecmp.cmp(srcFileName, dstFileName):
            logging.info("%s already exist." % srcFileName)
            return
        else:
            dstFileName = name + "_" + str(i) + suffix
            i = i + 1

    print("Collect File %s to %s." % (srcFileName, dstFileName))

    if not os.path.exists(os.path.dirname(dstFileName)):
        os.makedirs(os.path.dirname(dstFileName))
    if MOVE_FILE:
        shutil.move(srcFileName, dstFileName)
    else:
        shutil.copy2(srcFileName, dstFileName)

def classify(srcFileName, dstRootFold):
    """
    分类文件
    :param srcFileName: 原文件名
    :param dstRootFold: 输出目录
    :return: 输出格式YYYYMMDD_hhmmss
    """

    name, suffix = os.path.splitext(srcFileName)

    if suffix.lower() in ImageExtNames:
        time = get_image_original_time(srcFileName)
    elif suffix.lower() in VideoExtNames:
        time = get_video_original_time(srcFileName)
    else:
        logging.info("File: %s is not collected." % srcFileName)
        return

    if time != None:
        name, suffix = os.path.splitext(srcFileName)
        dstFileName = dstRootFold +'\\'+ time[0:4] + "-" + time[4:6] + '\\' + time + suffix
    else:
        dstFileName = dstRootFold + "\\unclassify" + "\\" + os.path.basename(srcFileName)

    copyFile(srcFileName, dstFileName)

def mainLoop(inPath, outPath):
    logging.info("Process %s." % inPath)
    for root, dirs, files in os.walk(inPath, True):
        for filename in files:
            absolute_file = os.path.join(root, filename)
            classify(absolute_file, outPath)
    
def main(argv):
    global MOVE_FILE

    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
     
    logging.basicConfig(filename='collect.log', level=logging.INFO, format=fmt)
    
    output_dir = ""
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

    try:
        with open(config_dir, "r") as configFile:
            line = configFile.readline()
            while line:
                if line.lstrip().startswith("#"):
                    line = configFile.readline()
                    continue
                mainLoop(str.strip(line), output_dir)
                line = configFile.readline()
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    main(sys.argv[1:])
