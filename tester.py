import fitz
from os import listdir
from os.path import join, isfile

import question
import paper_manager

save_dir = ["test\\questions\\out", "test\\answers\\out"]
read_dir = ["test\\questions\\in", "test\\answers\\in"]
pdf: str
answer: bool = False  # False -> Questions dir, True -> Ms dir 

rdir = lambda dtype: read_dir[int(answer)] if dtype == 'r' else save_dir[int(answer)]


def prepare():
    global pdf
    pdf = [f for f in listdir(rdir('r')) if isfile(join(rdir('r'), f))][0]
    paper_manager.paper_path = rdir('r')
    print("------ Starting Test ------")
    question.save_dir = rdir('s')
    question.doc = fitz.open(join(rdir('r'), pdf))
    question.load_questions()
    question.test = True
    print(f"Document Bottom Right: {question.doc[0].mediabox.bottom_right}")


def test_question(qs: int):
    prepare()
    question.refined_ss(qs)
    question.doc.close()


def test_paper():
    prepare()
    for i in range(1, paper_manager.get_number_of_questions(pdf) + 1):
        question.refined_ss(i)
    question.doc.close()
