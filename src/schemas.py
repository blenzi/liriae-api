from pydantic import BaseModel


class PdfInfo(BaseModel):
    """Basic information about a pdf file"""
    id: int
    name: str
    description: str | None = None
    n_pages: int


class _Position(BaseModel):
    x: float = 0.
    y: float = 0.


class Bbox(BaseModel):
    bbox: tuple[float] = (0, 0, 1, 1)


class PdfElement(_Position):
    """Partie élementaire d'un pdf pour la recherche: contenu entre deux niveaux de titres"""
    id: int
    title: str
    level: int  # 1-based
    page: int  # 0-based as used when loading the page
    last_page: int = -1
    all_titles: list[str] = []
    text: str = ""


class Span(Bbox):
    color: int
    font: str
    size: float
    flags: str
    text: str


class Line(Bbox):
    spans: list[Span]


class Block(Bbox):
    lines: list[Line]


class PdfElementDetails(BaseModel):
    pass
