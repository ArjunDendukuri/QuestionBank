import download
from os import path, mkdir, listdir
import paper_manager
import tester
from time import time

import answer
import fitz

dirs_to_make = [
    "downloads", "downloads\\ms", "downloads\\papers",
    "test", "test\\ms", "test\\ms\\in", "test\\ms\\out", "test\\questions", "test\\questions\\in",
    "test\\questions\\out", "saves"
]


def make_base_dirs():
    for dir2mk in dirs_to_make:
        if not path.exists(dir2mk):
            mkdir(dir2mk)


if __name__ == '__main__':
    make_base_dirs()
    start = time()
    # download.run_download()
    # print("Finished Downloads")
    paper_manager.run_for_papers()
    print("Finished Papers")
    paper_manager.run_for_answers()

    print (f"Timey: {time()-start}") #1.7/s paper
    print("Done")
