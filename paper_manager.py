from os import listdir, mkdir
from os.path import join, isfile, exists, dirname
import fitz

import question
# Paper Manager assumes the Paper Type is constant and will operate on that type
directory = dirname(__file__)
paper_path = join(directory, "downloads\\papers\\")


def run_for_papers():
    pdfs = [f for f in listdir(paper_path) if isfile(join(paper_path, f))]
    for pdf in pdfs:
        print(f"------ Starting {pdf} ------")
        new_save = question_folder_name(pdf)
        if exists(join(paper_path, new_save)):
            print(f"!!!! {pdf} dir already exists; skipping !!!!")
            continue
        make_question_dir(new_save)
        question.save_dir = f"questions\\{new_save}"
        question.doc = fitz.open(join(paper_path, pdf))
        question.load_questions()
        question.test = False
        for i in range(1, get_number_of_questions(pdf)+1):
            question.refined_ss(i)
        question.doc.close()


def make_question_dir(full_path: str):
    parts: list[str] = full_path.split("\\")
    for till in range(1, len(parts) + 1):
        potential: str = "\\".join(parts[:till])
        if not exists(join(directory, join("questions\\", potential))):
            mkdir(join(directory, join("questions\\", potential)))


# example
# In -> 0606_m22_qp_22
# Out -> 0606/March - 2022/Paper 2/Variant 2
def question_folder_name(pdf_name: str) -> str:
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
