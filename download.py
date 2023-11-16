import urllib.request
from urllib.error import HTTPError, ContentTooShortError
import fitz

HEAD = "https://papers.gceguide.com/Cambridge%20IGCSE/"
YEAR = (19, 19)  # start year, end year

save_dir = "downloads\\papers"
msave_dir = "downloads\\ms"


def run_download():
    current = to_run.first()
    while current is not None:
        if not current.download():
            to_run.next_paper(current)
            continue

        touchups = fitz.open(f"{save_dir}\\{current.file_name()}")
        touchups.delete_pages(to_run.red_pages)
        touchups.saveIncr()
        touchups.close()

        ms = current.ms()
        if not ms.download():
            to_run.next_paper(current)
            continue

        touchups = fitz.open(f"{msave_dir}\\{ms.file_name()}")
        # this varies based on subject and year (probably paper too) :(
        touchups.delete_pages([0, 1])
        touchups.saveIncr()
        touchups.close()

        current = to_run.next_paper(current)


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

    def ms(self):
        return MarkSchemeData(self)

    def download(self) -> bool:
        """Downloads the file. Returns boolean on whether it succeeded"""
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/6.0')]
        urllib.request.install_opener(opener)
        try:
            while True:
                try:
                    urllib.request.urlretrieve(self.link(), f"{save_dir}\\{self.file_name()}")
                except ContentTooShortError:
                    continue
                break
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


# soooo joint markschemes are a thing in the early days of igcse so some ms straight up wont download but like
# all thoses syllabuses are outdated, that's why you'll probably not get some ms if you do something very old
class MarkSchemeData:
    def __init__(self, paper: PaperData):
        self.paper = paper

    def file_name(self) -> str:
        return f"{self.paper.code}_{self.paper.series}_ms_{self.paper.paper}" + \
               f"{'' if self.paper.variant == 0 else self.paper.variant}.pdf"

    def link(self) -> str:
        return f"{HEAD}{'%20'.join(self.paper.name.split(' '))}" + \
               f"%20({self.paper.code})/20{self.paper.series.year}/{self.file_name()}"

    def __repr__(self):
        return self.file_name()

    def download(self) -> bool:
        """Downloads the file. Returns boolean on whether it succeeded"""
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/6.0')]
        urllib.request.install_opener(opener)
        try:
            urllib.request.urlretrieve(self.link(), f"{msave_dir}\\{self.file_name()}")
        except HTTPError:
            print(f"Failed to download {self.file_name()}\nLink: {self.paper.link()}")
            return False
        return True


class SubjectData:
    def __init__(self, papers: list[int], variants: int, seasons: tuple[str, str, str], code: str, name: str,
                 red_pages: list[int]):
        self.papers = papers
        self.variants = variants
        self.seasons = seasons
        self.code = code
        self.name = name
        self.red_pages = red_pages

    def first(self) -> PaperData:
        return PaperData(self.code, Series(YEAR[0], self.seasons[0]), self.papers[0], self.name,
                         int(self.variants != 0))

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


ADDMATH = SubjectData([1, 2], 2, ('m', 's', 'w'), "0606", "Mathematics - Additional", [0, 1])
SCIENCE = SubjectData([2, 4, 6], 2, ('m', 's', 'w'), "0654", "Sciences - Co-ordinated (Double)", [0])

to_run: SubjectData = ADDMATH
