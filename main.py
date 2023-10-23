import download
from os import path, mkdir
import paper_manager
import tester

dirs_to_make = [
    "downloads", "downloads\\ms", "downloads\\papers",
    "test", "test\\ms", "test\\ms\\in", "test\\ms\\out", "test\\questions", "test\\questions\\in",
    "test\\questions\\out", "questions"
]


def make_base_dirs():
    for dir2mk in dirs_to_make:
        if not path.exists(dir2mk):
            mkdir(dir2mk)


if __name__ == '__main__':
    make_base_dirs()
    tester.run_white_test()
    # tester.test_paper()
    # download.run_download()
    # print("Downloads Finished!!")
    # paper_manager.run_for_papers()
    print("Done")
