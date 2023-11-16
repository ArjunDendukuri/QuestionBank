import os.path

import fitz
from time import localtime
from PIL import Image
from io import BytesIO
import re

doc: fitz.Document
DEFAULT_BOTTOM_POINT: fitz.Point = fitz.Point(560, 800)  # might vary from ms, probably should check it
save_dir = "test\\ms\\out"
ss_shift = (-10, -10)
test: bool = False

question_column_cropbox: fitz.Rect = fitz.Rect(50, 90, 100, 800)


class MsPage:
    def __init__(self, num: int, pg: fitz.Page, answer_pos: dict[int, fitz.Point]):
        self.num = num
        self.pg = pg
        self.answer_pos = answer_pos

    def has_question(self, q: int) -> bool:
        return q in self.answer_pos

    def next_page(self):
        if self.is_last():
            return None
        return answer_index[self.num + 1]

    def answer_posi(self, question: int) -> fitz.Point:
        if question in self.answer_pos.keys():
            return self.answer_pos[question]
        return fitz.Point(-1, -1)

    def quick_ss(self, point: fitz.Rect, identifier: str = str(localtime().tm_sec.numerator)):
        self.pg.set_cropbox(point)
        self.pg.get_pixmap().save(f"{save_dir}\\quickss_{identifier}.png")

    def is_last(self):
        return self.num == doc.page_count - 1

    def reset(self):
        self.pg.set_cropbox(self.pg.mediabox)

    def page_starts_with_a(self):
        pass  # todo


answer_index: dict[int, MsPage] = dict()


def img_name(qs: int) -> str:
    if test:
        return f"answer_{qs}"
    parts: list[str] = save_dir.split("\\")
    if len(parts) == 5:
        return f"[{parts[1]}] {parts[2][:3]} '{parts[2].split(' ')[1][2:]} Paper {parts[3][6]}{parts[4][7]} A{qs}"
    return f"[{parts[1]}] {parts[2][:3]} '{parts[2].split(' ')[1][2:]} Paper {parts[3][6]} A{qs}"


def obtain_crop_box(pg: fitz.Page) -> fitz.Rect:
    """Gives you the crop box for the current page"""
    y_constants = [160, 90, 750]  # 0 -> Start Constant, 90 -> Top Constant, 750 -> Bottom constant
    y = y_constants[0]
    left_x = 0
    right_x = 0
    current_x = 1
    pxmp: fitz.Pixmap = pg.get_pixmap()
    finale: fitz.Rect = pg.mediabox

    while right_x == 0 and current_x < pg.mediabox.x1:
        clr = pxmp.pixel(current_x, y)
        if clr != (255, 255, 255):

            if current_x in range(left_x+3, left_x+6):  # resets in case of a seperating line or letter
                y = y - 10 if max(y_constants[1], y-10) == y - 10 else 300
                current_x = left_x + 1
                continue
            if left_x == 0:
                left_x = current_x
            else:
                right_x = current_x
                finale = fitz.Rect(left_x, y - 7.5, right_x + 5, y + 7.5).normalize()
                pg.set_cropbox(finale)
                text = [q.strip() for q in pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT).extractText(sort=True).split('\n')
                        if q.strip() and q[0].isdigit()]
                if len(text) != 0 or pxmp.pixel(current_x+3, y) != (255, 255, 255):
                    y += 20
                    current_x = left_x + 3
                    right_x = 0
                    continue
        current_x += 1

    finale.y0 = y_constants[1]
    finale.x0 -= 5
    finale.y1 = y_constants[2]
    return finale if right_x != 0 else pg.mediabox


def get_answer_nums(pg: fitz.Page) -> list[str]:
    pg.set_cropbox(question_column_cropbox)
    tpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)  # textpage conversion
    text = tpg.extractText(sort=True)  # bcuz of the cropbox all of this should be te numbers
    ans_f = []
    for line in text.split('\n'):
        match = re.match(r'^\d{1,2}', line)
        if not match or int(match.group()) < 1:
            continue
        num = match.group()

        ans_f.append(num)

    return ans_f


def pos_of_q(q: int, pg: fitz.Page, qs: list[str]) -> fitz.Point:
    if not str(q) in qs:
        return fitz.Point(-1, -1)
    pg.set_cropbox(question_column_cropbox)
    txtpg = pg.get_textpage(flags=fitz.TEXTFLAGS_TEXT)
    area: list[fitz.Rect] = txtpg.search(str(q), quads=False)
    return area[0].top_left


def load_answers():
    global question_column_cropbox
    question_column_cropbox = obtain_crop_box(doc[-2])


    for pgnum, page in enumerate(doc):
        qs = get_answer_nums(page)
        pos_list = {}
        for q in qs:
            if int(q) in pos_list.keys():
                continue
            pos_list[int(q)] = pos_of_q(int(q), page, qs)
        wrapper = MsPage(pgnum, page, pos_list)
        answer_index[pgnum] = wrapper


def answer_ss(question: int):
    ms_page: MsPage | None = None
    for pge in answer_index.values():
        if pge.has_question(question):
            ms_page = pge
            break
    if ms_page is None:
        print(f"Answer for question {question} failed :(; QuestionNotFound")
        return

    q_top_line: fitz.Point = ms_page.answer_posi(question)
    q_top_line += ss_shift
    bottom_line_y: float = ms_page.answer_posi(question + 1).y
    if bottom_line_y == -1:
        if should_continue_to_next_page(ms_page.next_page(), question):
            handle_multiple_pages(ms_page, question, q_top_line)
            return
        bottom_line_y = DEFAULT_BOTTOM_POINT.y

    try:
        ms_page.pg.set_cropbox(fitz.Rect(q_top_line, fitz.Point(DEFAULT_BOTTOM_POINT.x, bottom_line_y)).normalize())
    except ValueError:
        why = '\\'  # this exists for some reason
        print(f"Failed??? Setting the cropbox for question {question} in pdf {'_'.join(save_dir.split(why)[1:])}\n" +
              f"Rect: {fitz.Rect(q_top_line, fitz.Point(DEFAULT_BOTTOM_POINT.x, bottom_line_y)).normalize()}")
        return
    ms_page.pg.get_pixmap().save(f"{save_dir}\\{img_name(question)}.png")
    ms_page.reset()


def handle_multiple_pages(original: MsPage, question: int, top_left: fitz.Point):
    imgs_to_append = []
    # ss of the orginal question
    original.pg.set_cropbox(fitz.Rect(top_left, DEFAULT_BOTTOM_POINT).normalize())
    imgs_to_append.append(Image.open(BytesIO(original.pg.get_pixmap().pil_tobytes(format="PNG"))))

    do: MsPage = original.next_page()
    while should_continue_to_next_page(do, question):
        if do.num == original.num:
            continue
        imgs_to_append.append(photo_page(do, question, top_left.x))
        do = do.next_page()

    height = sum([img.height for img in imgs_to_append])
    if test:
        print(f"Question {question} height: {height}")

    merged = Image.new('RGB', (imgs_to_append[0].width, height))
    for i, img in enumerate(imgs_to_append):
        merged.paste(img, (0, sum([img.height for img in imgs_to_append[:i]])))

    if test:
        print(f"Finished {question}")
    merged.save(f"{save_dir}/{img_name(question)}.png")
    original.reset()


def photo_page(mpg: MsPage, q: int, top_left_x: float) -> Image:
    q_pos = mpg.answer_posi(q + 1)
    bottom_right: fitz.Point
    pg = mpg.pg
    if q_pos[0] == -1:
        bottom_right = DEFAULT_BOTTOM_POINT
    else:
        bottom_right = fitz.Point(pg.mediabox.x1, q_pos[1])
    pg.set_cropbox(fitz.Rect(fitz.Point(top_left_x, 0), bottom_right).normalize())
    return Image.open(BytesIO(pg.get_pixmap().pil_tobytes(format="PNG")))


def should_continue_to_next_page(pg: MsPage | None, ques: int) -> bool:
    return pg is not None and pg.has_question(ques)
