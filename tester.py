from PIL import Image
from os import listdir
from os.path import join, isfile
from time import time

import io
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


def crop_white_areas(image: Image, pg: fitz.Page):
    # Open the image

    # Convert the image to RGBA mode (allows transparency)
    image = image.convert("RGBA")

    # Get the image data as a list of (R, G, B, A) tuples
    image_data = list(image.getdata())

    # Define the color to consider as white (white: (255, 255, 255, 255))
    white_color = (255, 255, 255, 255)

    # Find the coordinates of the top-left corner of the first white area
    white_area_coords = []
    for y in range(image.height):
        for x in range(image.width):
            if image_data[y * image.width + x] == white_color:
                white_area_coords.append((x, y))

    # Start at x,y = 0,

    if not white_area_coords:
        print("No white areas found in the image.")
        return

    # Assuming there's only one white area, you can use the first found
    x, y = white_area_coords[0]

    # Crop the image to the specified dimensions (e.g., 700x500)
    cropped_image = image.crop((x, y, x + test_crop_dim[0], y + test_crop_dim[1]))

    # Save the cropped image



def run_white_test(pgnum: int = -1):
    prepare_questions()
    for pnum, pg in enumerate(question.doc):
        if pnum != pgnum and pgnum != -1:
            continue
        pg.set_cropbox(pg.mediabox)

        mg: Image = Image.open(io.BytesIO(pg.get_pixmap().pil_tobytes(format="PNG")))
        crop_white_areas(mg, pnum)


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
