#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess

import click


# TODO delete originals
# TODO optimize


@click.command()
@click.option("--keep", is_flag=True, help="Keep original source image?")
@click.option(
    "--src",
    "-s",
    type=click.Path(exists=True),
    help="Source directory of images to process or path to single image",
    required=True,
)
def main(keep, src):

    if os.path.isdir(src):

        image_to_convert = []
        for filename in os.listdir(src):
            if filename.endswith(".heic") or filename.endswith(".HEIC"):
                absolute_filename = os.path.join(src, filename)
                image_to_convert.append(absolute_filename)

                pwd = os.getcwd()
                os.chdir(src)
                command = "magick convert " + filename + " " + os.path.splitext(filename)[0] + ".jpg"
                print(command)

                os.system(command)
                os.chdir(pwd)

        # remove?
        if not keep:
            for filename in image_to_convert:
                os.remove(filename)

if __name__ == "__main__":
    main(sys.argv[1:])