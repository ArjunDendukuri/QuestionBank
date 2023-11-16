import fitz
from PIL import Image
import io
from time import localtime

import subjects

ss_shift = (-10, -20)  # a shift to give space around the question making the question more readable
blank_page_check = ((250, 60), (350, 90))

doc: fitz.Document
save_dir: str
paper_type: subjects.PaperType = subjects.ADDMATH
test: bool = False


class PaperPage:
    def __init__(self, num: int, page: fitz.Page, question_pos: dict[int, list[float]]):
        self.num = num
        self.question_pos_dict = question_pos
        self.pg = page

    def question_pos(self, question: int) -> list[float]:
        if question in self.question_pos_dict.keys():
            return self.question_pos_dict[question]
        return [-1.0, -1.0]

    def quick_ss(self, point: fitz.Rect, identifier: str = str(localtime().tm_sec.numerator)):
        self.pg.set_cropbox(point)
        self.pg.get_pixmap().save(f"{save_dir}\\quickss_{identifier}.png")

    def reset(self):
        self.pg.set_cropbox(self.pg.mediabox)

    def is_blank_page(self) -> bool:
        self.pg.set_cropbox(fitz.Rect(blank_page_check[0], blank_page_check[1]).normalize())
        tpg = self.pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)
        return "BLANK PAGE" in tpg.extractText()

    def is_last(self) -> bool:
        return self.num == doc.page_count - 1

    def page_starts_with_q(self) -> bool:
        """Checks if the questions are in the range of being at the question (x: 48-50, y:60-70)"""
        pg_qs = list(self.question_pos_dict.keys())
        if len(pg_qs) == 0:
            return False
        pos_of = self.question_pos(pg_qs[0])
        return paper_type.new_page_question_range[0][0] <= pos_of[0] <= paper_type.new_page_question_range[0][1] and \
            paper_type.new_page_question_range[1][0] <= pos_of[1] <= paper_type.new_page_question_range[1][1]


question_index: dict[int, PaperPage] = {}


def img_name(qs: int) -> str:
    if test:
        return f"question_{qs}"
    parts: list[str] = save_dir.split("\\")
    if len(parts) == 5:
        return f"[{parts[1]}] {parts[2][:3]} '{parts[2].split(' ')[1][2:]} Paper {parts[3][6]}{parts[4][9]} Q{qs}"
    return f"[{parts[1]}] {parts[2][:3]} '{parts[2].split(' ')[1][2:]} Paper {parts[3][6]} Q{qs}"


def load_questions():
    for pgnum, pg in enumerate(doc):
        qList = {}
        qs = get_questions(pg, stripped=True)
        for q in qs:
            qList[int(q)] = pos_of_question(pg, int(q), qs)
        question_index[pgnum] = PaperPage(pgnum, pg, qList)
        if test:
            print(f"Inited pg {pgnum}\nQuestions: {qs}")


def refined_ss(question: int) -> None:
    """Takes a screenshot of the question asked for. Prints fail message if it failed"""
    pg: fitz.Page

    for pgd in question_index.values():
        question_pos = pgd.question_pos(question)
        if question_pos[0] == -1:
            continue
        if test:
            print(f"Question {question} top left: {question_pos}")
        question_pos[0] += ss_shift[0]
        question_pos[1] += ss_shift[1]
        top_left: fitz.Point = fitz.Point(question_pos)

        next_q_pos = pgd.question_pos(question + 1)
        bottom_right: fitz.Point
        if next_q_pos[0] == -1:
            if not pgd.is_last() and should_continue_to_next_page(question_index[pgd.num + 1]):
                handle_second_pg(top_left, pgd, question)
                return
            else:
                bottom_right = pgd.pg.mediabox.bottom_right
        else:
            bottom_right = fitz.Point(pgd.pg.mediabox.x1, next_q_pos[1])

        try:
            pgd.pg.set_cropbox(fitz.Rect(top_left, bottom_right).normalize())
        except ValueError:
            why = '\\'  # this exists for some reason
            print(f"Failed??? Setting the cropbox for question {question} in pdf {'_'.join(save_dir.split(why)[1:])}" +
                  f"Rect: {fitz.Rect(top_left, bottom_right).normalize()}")
            break
        pgd.pg.get_pixmap().save(f"{save_dir}/{img_name(question)}.png", output="png")
        if test:
            print(f"Finished {question}")
        pgd.reset()
        return
    print(f"Question {question} failed :(")


def get_questions(pg: fitz.Page, stripped: bool = False) -> list[str]:
    """This function returns all the question numbers in a page"""
    pg.set_cropbox(paper_type.question_crop_box)
    tpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)  # textpage conversion
    text = tpg.extractText(sort=True)  # bcuz of the cropbox all of this should be te numbers
    if stripped:
        return [
            line.split(" ")[0].strip() for line in text.split('\n') if len(line) > 0 and line[0].isdigit()
        ]
    return [
        line.split(" ")[0] for line in text.split('\n') if len(line) > 0 and line[0].isdigit()
    ]


def pos_of_question(pg: fitz.Page, question: int, qs: list[str]) -> list[float]:
    """Returns position of question in a page. Returns [-1,-1] if question wasn't found"""
    if pg is None:
        return [-1, -1]
    if not str(question) in qs:
        return [-1, -1]
    pg.set_cropbox(paper_type.question_crop_box)
    txtpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)
    area = txtpg.search(str(question), quads=False)
    return [area[0].x0, area[0].y0]


def should_continue_to_next_page(page: PaperPage) -> bool:
    """Checks if the pg number starts with a new question or continues with the question from the last page"""
    return not page.page_starts_with_q() and not page.is_blank_page() and not page.is_last()


def handle_second_pg(top_left: fitz.Point, pgd: PaperPage, qnum: int):
    images_to_merge = []
    pg = pgd.pg
    if pg is None:
        return
    pg.set_cropbox(fitz.Rect(top_left, pg.mediabox.bottom_right).normalize())
    # images_to_merge.append(Image.open(io.BytesIO(pg.get_pixmap().pil_tobytes(format="PNG"))))

    do_pg = pgd
    while should_continue_to_next_page(do_pg):
        images_to_merge.append(photo_till_q(do_pg, qnum, top_left.x))
        do_pg = question_index[do_pg.num + 1]

    height = sum([img.height for img in images_to_merge])
    if test:
        print(f"Question {qnum} height: {height}")
    merged = Image.new('RGB', (images_to_merge[0].width, height))

    for i, img in enumerate(images_to_merge):
        merged.paste(img, (0, sum([img.height for img in images_to_merge[:i]])))
    if test:
        print(f"Finished {qnum}")
    merged.save(f"{save_dir}/{img_name(qnum)}.png")


def photo_till_q(pgd: PaperPage, qnum: int, top_left: float) -> Image:
    q_pos = pgd.question_pos(qnum + 1)
    bottom_right: fitz.Point
    pg = pgd.pg
    if q_pos[0] == -1:
        bottom_right = pg.mediabox.bottom_right
    else:
        bottom_right = fitz.Point(pg.mediabox.x1, q_pos[1])
    pg.set_cropbox(fitz.Rect(fitz.Point(top_left, 0), bottom_right).normalize())
    return Image.open(io.BytesIO(pg.get_pixmap().pil_tobytes(format="PNG")))
