from pydantic import BaseModel


class _Position(BaseModel):
    x: float = 0.0
    y: float = 0.0


class Bbox(BaseModel):
    bbox: tuple[float, float, float, float] = (0, 0, 1, 1)


class _TocItemBase(BaseModel):
    "Base for table of content items"
    id: int
    title: str


class TocItem(_TocItemBase, _Position):
    parent_id: int = -1
    level: int  # 1-based
    page: int  # 0-based as used when loading the page


class TocTreeItem(_TocItemBase):
    children: list = []


class PdfInfo(BaseModel):
    """Basic information about a pdf file"""

    id: int
    name: str
    description: str | None = None
    n_pages: int
    n_toc_items: int
    toc: list[TocItem]


class Span(Bbox):
    color: int
    font: str
    size: float
    flags: int
    text: str


class Line(Bbox):
    spans: list[Span]


class TextBlock(Bbox):
    lines: list[Line]


class PdfElement(TocItem):
    """Partie élementaire d'un pdf pour la recherche: contenu entre deux niveaux de titres"""

    all_titles: list[str] = []
    text: str = ""
    blocks: list[TextBlock]
