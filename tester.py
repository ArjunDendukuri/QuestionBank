from PIL import Image
from os import listdir
from os.path import join, isfile

import fitz
import question
import answer
import paper_manager

save_dir = ["test\\questions\\out", "test\\ms\\out"]
read_dir = ["test\\questions\\in", "test\\ms\\in"]
pdf: str
is_answer: bool = False  # False -> Questions dir, True -> Ms dir

rdir = lambda dtype: read_dir[int(is_answer)] if dtype == 'read' else save_dir[int(is_answer)]

test_crop_dim = (700, 500)

'''
Take img at every point and use pytessrsct to extract text
Once a large textless space is found mark the bottom and top
make ss from last bottom the current top
set bottom to last bottom
repeat
'''


def prepare_answers():
    global pdf
    global is_answer
    is_answer = True

    pdf = [f for f in listdir(rdir('read')) if isfile(join(rdir('read'), f))][0]
    paper_manager.ms_path = rdir('read')
    print("------ Starting Test ------")
    answer.test = True
    answer.save_dir = rdir('save')
    answer.doc = fitz.open(join(rdir('read'), pdf))
    answer.load_answers()


def test_answer(qs: int):
    prepare_answers()
    answer.answer_ss(qs)
    answer.doc.close()


def test_full_ms():
    prepare_answers()
    for i in range(1, paper_manager.get_number_of_answers(pdf) + 1):
        answer.answer_ss(i)
    answer.doc.close()


def prepare_questions():
    global pdf
    pdf = [f for f in listdir(rdir('read')) if isfile(join(rdir('read'), f))][0]
    paper_manager.paper_path = rdir('read')
    print("------ Starting Test ------")
    question.test = True
    question.save_dir = rdir('save')
    question.doc = fitz.open(join(rdir('read'), pdf))
    question.load_questions()


def test_question(qs: int):
    prepare_questions()
    question.refined_ss(qs)
    question.doc.close()


def test_paper():
    prepare_questions()
    for i in range(1, paper_manager.get_number_of_questions(pdf) + 1):
        question.refined_ss(i)
    question.doc.close()
