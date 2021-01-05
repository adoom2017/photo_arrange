# -*- coding: utf-8 -*-

import filecmp
import getopt
import logging
import os
import shutil
import sys
import re
import json

from metadata import Metadata

class MediaArrange:
    def __init__(self, input, output, move = False):
        self.input = input
        self.output = output
        self.move = move

    def genAbsolutePath(self, in_file):
        name, suffix = os.path.splitext(in_file)
        self.suffix = suffix
        self.name = name
        create_time = Metadata(in_file).getCreateTime()

        if create_time != None:
            dst_file_name = self.output +'\\'+ create_time[0:4] + "-" + create_time[4:6] + '\\' + create_time + self.suffix
        else:
            dst_file_name = self.output + "\\unclassify" + "\\" + os.path.basename(in_file)

        return dst_file_name

    def copy(self, in_file, out_file):
        i = 1
        while os.path.exists(out_file):
            if filecmp.cmp(in_file, out_file):
                logging.info("%s already exist." % in_file)
                return
            else:
                out_file = self.name + "_" + str(i) + self.suffix
                i = i + 1

        logging.info("Collect File %s to %s." % (in_file, out_file))

        if not os.path.exists(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))

        if self.move:
            shutil.move(in_file, out_file)
        else:
            shutil.copy2(in_file, out_file)

    def arrange(self):
        logging.info("Begin Process %s." % self.input)
        for root, _, files in os.walk(self.input, True):
            for filename in files:
                in_file = os.path.join(root, filename)
                out_file = self.genAbsolutePath(in_file)
                self.copy(in_file, out_file)
        logging.info("End Process %s." % self.input)

def main(argv):
    fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(message)s'
    logging.basicConfig(filename='media-arrange.log', level=logging.INFO, format=fmt)
    
    output_dir = ""
    input_dir = ""
    config_dir = ""
    move_file = False

    try:
        opts, _ = getopt.getopt(argv, "hmi:c:o:", ["help", "move", "ifile=", "config=", "ofile="])
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
            move_file = True
    
    try:
        if len(input_dir) != 0:
            MediaArrange(input_dir, output_dir, move_file).arrange()
        elif len(config_dir) != 0:
            with open(config_dir, "r") as configFile:
                line = configFile.readline()
                while line:
                    if line.lstrip().startswith("#"):
                        line = configFile.readline()
                        continue
                    MediaArrange(input_dir, output_dir, move_file).arrange()
                    line = configFile.readline()
        else:
            print(sys.argv[0] + " -c <pathfile> or -i <inputpath> -o <outputpath>")
            sys.exit(2)
    except Exception as e:
        logging.exception(e)

if __name__ == '__main__':
    main(sys.argv[1:])
