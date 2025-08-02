# coding utf-8
import sys

import pyguetzli


def jpg_compress(filename):
    input_jpeg = open(f"../big/{filename}.jpg", "rb").read()
    optimized_jpeg = pyguetzli.process_jpeg_bytes(input_jpeg)

    output = open(f"../big/{filename}_optimized.jpg", "wb")
    output.write(optimized_jpeg)
    output.close()


jpg_compress(sys.argv[1])
