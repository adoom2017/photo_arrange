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

IMAGE_EXT_NAMES = ('.jpg','.png','.jpeg')
VIDEO_EXT_NAMES = ('.mp4','.mov','.avi')

def get_image_original_time(filename):
    """
    用于图片创建时间获取，如果图片本来就是按照时间命名的
    :param filename: 待获取文件名
    :return: 输出格式YYYYMMDD_hhmmss
    """
    # 优先从exif中获取图片创建信息
    with open(filename, 'rb') as f:
        tags = exifread.process_file(f, details=False)
        if 'EXIF DateTimeOriginal' in tags:
            time = str(tags['EXIF DateTimeOriginal'])
            return time.replace(":", "").replace(" ", "_")

    # 如果exif中不存在图片时间信息，那么判断文件名是否是按照时间命名的，部分相机是这么个格式
    match_rex = re.match(r"(\d*)_(\d*)_(\d*)_(\d*)_(\d*)_IMG_(\d\d)", os.path.basename(filename))
    if match_rex != None:
        return match_rex.group(1)+match_rex.group(2)+match_rex.group(3)+"_"\
            +match_rex.group(4)+match_rex.group(5)+match_rex.group(6)
        
    return None

def get_video_original_time(filename):
    """
    用于视频创建时间获取
    :param filename: 待获取文件名
    :return: 输出格式YYYYMMDD_hhmmss
    """

    date_key = 'Creation date'
    time_pos = 8
    parser_file = parser.createParser(filename) #解析文件
    if not parser_file:
        logging.error("Unable to parse file %s." % filename)
        return False
    try:
        metadata_decode = metadata.extractMetadata(parser_file)  # 获取文件的metadata
    except ValueError:
        logging.error("Metadata extraction error, file: %s." % filename)
        metadata_decode = None
        return False

    if not metadata_decode:
        logging.error("Unable to extract metadata, file: %s." % filename)
        return False

    matedata_list = metadata_decode.exportPlaintext(line_prefix="") # 将文件的metadata转换为list,且将前缀设置为空

    for i in range(1, len(matedata_list) + 1):
        # 如果字符串在列表中,则提取数字部分,即为文件创建时间
        if date_key in matedata_list[i-1]:
            fileTime = re.sub(r"\D",'',matedata_list[i-1])    #使用正则表达式将列表中的非数字元素剔除
            a=list(fileTime)                           #将文件创建时间字符串转为列表list
            a.insert(time_pos,'_')                 #将列表插入下划线分割date与time
            fileFinalTime = "".join(a)                 #重新将列表转为字符串

            return fileFinalTime

def copyFile(src_file_name, dst_file_name):
    """
    复制文件，整理名称
    :param src_file_name: 原文件名
    :param dst_root_fold: 目标文件名
    :return: 
    """

    i = 1
    name, suffix = os.path.splitext(dst_file_name)
    while os.path.exists(dst_file_name):
        if filecmp.cmp(src_file_name, dst_file_name):
            logging.info("%s already exist." % src_file_name)
            return
        else:
            dst_file_name = name + "_" + str(i) + suffix
            i = i + 1

    print("Collect File %s to %s." % (src_file_name, dst_file_name))

    if not os.path.exists(os.path.dirname(dst_file_name)):
        os.makedirs(os.path.dirname(dst_file_name))
    if MOVE_FILE:
        shutil.move(src_file_name, dst_file_name)
    else:
        shutil.copy2(src_file_name, dst_file_name)

def classify(src_file_name, dst_root_fold):
    """
    分类文件
    :param src_file_name: 原文件名
    :param dst_root_fold: 输出目录
    :return: 输出格式YYYYMMDD_hhmmss
    """

    name, suffix = os.path.splitext(src_file_name)

    if suffix.lower() in IMAGE_EXT_NAMES:
        time = get_image_original_time(src_file_name)
    elif suffix.lower() in VIDEO_EXT_NAMES:
        time = get_video_original_time(src_file_name)
    else:
        logging.info("File: %s is not collected." % src_file_name)
        return

    if time != None:
        name, suffix = os.path.splitext(src_file_name)
        dst_file_name = dst_root_fold +'\\'+ time[0:4] + "-" + time[4:6] + '\\' + time + suffix
    else:
        dst_file_name = dst_root_fold + "\\unclassify" + "\\" + os.path.basename(src_file_name)

    copyFile(src_file_name, dst_file_name)

def mainLoop(in_path, out_path):
    logging.info("Process %s." % in_path)
    for root, dirs, files in os.walk(in_path, True):
        for filename in files:
            absolute_file = os.path.join(root, filename)
            classify(absolute_file, out_path)
    
def main(argv):
    global MOVE_FILE

    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
     
    logging.basicConfig(filename='collect.log', level=logging.INFO, format=fmt)
    
    output_dir = ""
    input_dir = ""
    config_dir = ""

    try:
        opts, args = getopt.getopt(argv, "hmi:c:o:", ["help", "move", "ifile=", "config=", "ofile="])
    except getopt.GetoptError:
        print(sys.argv[0] + " -c <pathfile> or -i <inputpath> -o <outputpath>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print(sys.argv[0] + " -c <pathfile> -o <outputpath>")
            sys.exit()
        elif opt in ("-o", "--ofile"):
            output_dir = arg
        elif opt in ("-i", "--ifile"):
            input_dir = arg
        elif opt in ("-c", "--config"):
            config_dir = arg
        elif opt in ("-m", "--move"):
            MOVE_FILE = True
    
    try:
        if len(input_dir) != 0:    
            mainLoop(input_dir, output_dir)
        elif len(config_dir) != 0:
            with open(config_dir, "r") as configFile:
                line = configFile.readline()
                while line:
                    if line.lstrip().startswith("#"):
                        line = configFile.readline()
                        continue
                    mainLoop(str.strip(line), output_dir)
                    line = configFile.readline()
        else:
            print(sys.argv[0] + " -c <pathfile> or -i <inputpath> -o <outputpath>")
            sys.exit(2)
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    main(sys.argv[1:])
