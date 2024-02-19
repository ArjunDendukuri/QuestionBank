import requests
import fitz
import os

HEAD = "https://pastpapers.co/cie/IGCSE/"
YEAR = (19, 19)  # start year, end year

save_dir = "downloads\\papers"
msave_dir = "downloads\\ms"


def run_download():
    current = to_run.first()
    while current is not None:
        if not current.download():
            if to_run.next_paper(current) is None:
                break
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

    def joint_name(self):
        joint = f"20{self.year}-"
        match self.season:
            case "s":
                joint += "May-June"
            case "m":
                joint += "March"
            case "w":
                joint += "Oct-Nov"
        return joint

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
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': f'{self.link()}'
            }

            response = requests.get(self.link(), headers=headers, stream=True)
            print(response.content[:128])

            if response.status_code == 200:
                with open(f'{save_dir}\\{self.file_name()}', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=128):
                        file.write(chunk)
                return True

            elif response.status_code in [401, 403]:
                print(f"Unauthorized access to {self.link()}")
                return False

            else:
                print(f"Failed to download {self.file_name()}\nStatus Code: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error {e}")

        return False

    def link(self) -> str:
        return f"{HEAD}{self.name}-{self.code}/{self.series.joint_name()}/{self.file_name()}"

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
        return f"{HEAD}{self.paper.name}-{self.paper.code}/{self.paper.series.joint_name()}/{self.file_name()}"

    def __repr__(self):
        return self.file_name()

    def download(self) -> bool:
        """Downloads the file. Returns boolean on whether it succeeded"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Referer': f'{self.link()}'
            }

            response = requests.get(self.link(), headers=headers, stream=True)


            if response.status_code == 200:
                with open(f'{msave_dir}\\{self.file_name()}', 'wb') as file:
                    for chunk in response.iter_content(chunk_size=128):
                        file.write(chunk)
                return True

            elif response.status_code in [401, 403, 404]:
                print(f"Unauthorized access to {self.link()}")
                return False

            else:
                print(f"Failed to download {self.file_name()}\nStatus Code: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error {e}")

        return False


class SubjectData:
    def __init__(self, papers: list[int], variants: int, seasons: list[str], code: str, name: str,
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

# https://pastpapers.co/cie/IGCSE/Mathematics-Additional-0606/2022-May-June/0606_s22_ms_12.pdf
ADDMATH = SubjectData([1, 2], 2, ['m', 's', 'w'], "0606", "Mathematics-Additional", [0, 1])
ADDMATHT = SubjectData([1, 2], 2, ['s'], "0606", "Mathematics-Additional", [0, 1])
SCIENCE = SubjectData([2, 4, 6], 2, ['m', 's', 'w'], "0654", "Sciences - Co-ordinated (Double)", [0])

to_run: SubjectData = ADDMATHT
