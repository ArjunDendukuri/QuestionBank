import urllib.request
from urllib.error import HTTPError

import fitz

HEAD = "https://papers.gceguide.com/Cambridge%20IGCSE/"
YEAR = (22, 22)  # start year, end year

save_dir = "downloads\\papers"


def run_download():
    current = to_run.first()
    if current.download():
        touchups = fitz.open(f"{save_dir}\\{current.file_name()}")
        touchups.delete_page(0)
        touchups.saveIncr()
        touchups.close()
    while to_run.next_paper(current) is not None:
        if current.download():
            touchups = fitz.open(f"{save_dir}\\{current.file_name()}")
            touchups.delete_page(0)
            touchups.saveIncr()
            touchups.close()


class Series:
    def __init__(self, year: int, season: str):
        self.year = year
        self.season = season

    def __repr__(self):
        return f"{self.season}{self.year}"


class PaperData:
    def __init__(self, code: str, series: Series, paper: int, name: str, variant: int):
        self.code = code
        self.series = series
        self.paper = paper
        self.name = name
        self.variant = variant

    def download(self) -> bool:
        """Downloads the file. Returns boolean on whether it succeeded"""
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/6.0')]
        urllib.request.install_opener(opener)
        try:
            urllib.request.urlretrieve(self.link(), f"{save_dir}\\{self.file_name()}")
        except HTTPError:
            print(f"Failed to download {self.file_name()}\nLink: {self.link()}")
            return False
        return True

    def link(self) -> str:
        return f"{HEAD}{'%20'.join(self.name.split(' '))}%20({self.code})/20{self.series.year}/{self.file_name()}"

    def file_name(self) -> str:
        return f"{self.code}_{self.series}_qp_{self.paper}{'' if self.variant == 0 else self.variant}.pdf"

    def __repr__(self):
        return self.file_name()


class SubjectData:
    def __init__(self, papers: list[int], variants: int, seasons: tuple[str, str, str], code: str, name: str):
        self.papers = papers
        self.variants = variants
        self.seasons = seasons
        self.code = code
        self.name = name

    def first(self) -> PaperData:
        return PaperData(self.code, Series(YEAR[0], self.seasons[0]), self.papers[0], self.name, int(self.variants != 0))

    def next_paper(self, paper: PaperData) -> PaperData | None:
        if paper.variant < self.variants:
            paper.variant += 1
            return paper
        if paper.paper != self.papers[-1]:
            paper.paper = self.papers[self.papers.index(paper.paper) + 1]
            paper.variant = int(self.variants != 0)
            return paper
        if paper.series.season != self.seasons[-1]:
            paper.series.season = self.seasons[self.seasons.index(paper.series.season) + 1]
            paper.paper = self.papers[0]
            paper.variant = int(self.variants != 0)
            return paper
        if paper.series.year != YEAR[1]:
            paper.series.year += 1
            paper.series.season = self.seasons[0]
            paper.paper = self.papers[0]
            paper.variant = int(self.variants != 0)
            return paper

        return None


ADDMATH = SubjectData([1, 2], 2, ('m', 's', 'w'), "0606", "Mathematics - Additional")
SCIENCE = SubjectData([2, 4, 6], 2, ('m', 's', 'w'), "0654", "Sciences - Co-ordinated (Double)")

to_run: SubjectData = ADDMATH
