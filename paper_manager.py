from os import listdir, mkdir
from os.path import join, isfile, exists, dirname
import fitz
import re

import question
import answer

# Paper Manager assumes the Paper Type is constant and will operate on that type
directory = dirname(__file__)
paper_path = "downloads\\papers\\"
ms_path = "downloads\\ms\\"


def run_for_answers():
    ms_list = [f for f in listdir(ms_path) if isfile(join(ms_path, f))]
    for ms in ms_list:
        print(f"------ Starting {ms} ------")
        new_save = folder_name(ms)
        if exists(join(ms_path, new_save)):
            print(f"!!!! {ms} dir already exists; skipping !!!!")
            continue
        make_dir(new_save, False)
        answer.save_dir = f"saves\\{new_save}\\answers"
        answer.doc = fitz.open(join(ms_path, ms))
        answer.test = False
        answer.load_answers()
        for i in range(1, get_number_of_answers(pdf) + 1):
            try:
                question.refined_ss(i)
            except:
                print(f"{pdf}/ans{i} didn't work for some reason; skipping doc")
                break
        answer.doc.close()


def run_for_papers():
    pdfs = [f for f in listdir(paper_path) if isfile(join(paper_path, f))]
    for pdf in pdfs:
        print(f"------ Starting {pdf} ------")
        new_save = folder_name(pdf)
        if exists(join(paper_path, new_save)):
            print(f"!!!! {pdf} dir already exists; skipping !!!!")
            continue
        make_dir(new_save, True)
        question.save_dir = f"saves\\{new_save}\\questions"
        question.doc = fitz.open(join(paper_path, pdf))
        question.load_questions()
        question.test = False
        for i in range(1, get_number_of_questions(pdf) + 1):
            try:
                question.refined_ss(i)
            except:
                print(f"{pdf}/q{i} didn't work for some reason; skipping doc")
                break
        question.doc.close()


def make_dir(full_path: str, is_q: bool):
    parts: list[str] = full_path.split("\\")
    last = "questions" if is_q else "answers"
    parts.append(last)
    for till in range(1, len(parts) + 1):
        potential: str = "\\".join(parts[:till])
        if not exists(f"saves\\{potential}"):
            mkdir(f"saves\\{potential}")


# example
# In -> 0606_m22_qp_22
# Out -> 0606/March - 2022/Paper 2/Variant 2
def folder_name(pdf_name: str) -> str:
    pdf_name = pdf_name[:len(pdf_name) - 4]
    parts: list[str] = pdf_name.split("_")
    final: str = f"{parts[0]}\\"
    match parts[1][0]:
        case "m":
            final += "March"
        case "s":
            final += "June"
        case "w":
            final += "November"
        case _:
            final += "Unknown Series"
    final += f" 20{parts[1][1]}{parts[1][2]}\\"
    final += f"Paper {parts[3][0]}"
    if len(parts[3]) == 2:
        final += f"\\Variant {parts[3][1]}"
    return final


def get_number_of_questions(doc_file) -> int:
    doc: fitz.Document = fitz.open(join(paper_path, doc_file))
    questions = 0
    for pg in doc:
        pg.set_cropbox(question.paper_type.question_crop_box)
        tpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)  # textpage conversion
        text = tpg.extractText(sort=True)  # bcuz of the cropbox all of this should be te numbers
        questions += len([
            line for line in text.split('\n') if len(line) > 0 and line[0].isdigit()
        ])

    doc.close()
    return questions


def get_number_of_answers(ms) -> int:
    doc: fitz.Document = fitz.open(join(ms_path, ms))
    finished = []
    for num, pg in enumerate(doc):
        pg.set_cropbox(answer.obtain_crop_box(pg))
        tpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)  # textpage conversion
        text = tpg.extractText(sort=True)  # bcuz of the cropbox all of this should be te numbers
        ans_f = []

        for line in text.split('\n'):
            match = re.match(r'^\d{1,2}', line)
            if not match or int(match.group()) < 1:
                continue
            num = match.group()

            if num not in ans_f and num not in finished:
                ans_f.append(num)

        finished = list(set(finished + ans_f))
        if answer.test:
            print(f"number of answers in {pg}: {len(ans_f)}")

    return len(finished)
