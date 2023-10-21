from fitz import Rect


class PaperType:
    
    def __init__(self, code_n_paper: str, question_crop_box: Rect,
                 new_page_question_range: tuple[tuple[float, float], tuple[float, float]]):  # who the frog made type casting this stupid??
        self.code_n_paper = code_n_paper
        self.question_crop_box = question_crop_box
        self.new_page_question_range = new_page_question_range

    def __repr__(self):
        return f"IGCSE {self.code_n_paper}"
        

ADDMATH: PaperType = PaperType(
    "0606",
    Rect((45, 0), (65, 741.89)),
    ((10, 54), (60, 90))  # todo fix
)

SCIENCE_THEORY = PaperType(
    "0654/4",
    Rect((45, 0), (65, 741.89)),
    ((49, 65), (60, 70))  # todo fix
)
SCIENCE_MCQ: PaperType = PaperType( 
    "0654/2",
    Rect((10, 0), (78, 741.89)),
    ((38, 40), (60, 90))
)
