from pydantic import BaseModel


class PdfInfo(BaseModel):
    """Basic information about a pdf file"""
    id: int
    name: str
    description: str | None = None
    n_pages: int


class PdfElement(BaseModel):
    """Partie élementaire d'un pdf pour la recherche: contenu entre deux niveaux de titres"""
    id: str
    title: str
    all_titles: list[str]
    first_page: int
    last_page: int
    text: str


class Bbox(BaseModel):
    bbox: tuple[float] = (0, 0, 1, 1)


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
