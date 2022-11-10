import os
import s3fs
import fitz
import itertools
from contextlib import contextmanager

from .schemas import PdfElement, TextBlock, Line, Span, TocItem, PdfInfo


def open_file(filename, mode="r"):
    """
    Return a file object, open with open(data/<filename>, <mode>) or fs.open(projet-outil-ae/test/filename, <mode>)
    for s3, depending if environment variable $AWS_S3_ENDPOINT is set
    Args:
        filename (str): file to open
        mode (str): open mode
    Returns:
        File object
    """
    if False:  # "AWS_S3_ENDPOINT" in os.environ:
        # Create filesystem object
        S3_ENDPOINT_URL = "https://" + os.environ["AWS_S3_ENDPOINT"]
        fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": S3_ENDPOINT_URL})
        return fs.open(f"projet-outil-ae/test/{filename}", mode=mode)
    else:
        return open(f"data/{filename}", mode=mode)


@contextmanager
def open_pdf(pdf: str) -> fitz.Document:
    with open_file(pdf, "rb") as pdf_file:
        with fitz.open(pdf_file) as doc:
            yield doc


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def get_text_blocks(doc: fitz.Document, title: PdfElement, next_title: PdfElement):
    """
    Return an iterator with a tuple (x0, y0, x1, y1, text) for each the text block

    Args:
        pdf (str or fitz.Document): PDF document
        text_blocks (bool, default=True): add text blocks
    """
    for page_no in range(title.page, next_title.get("page", doc.page_count - 1) + 1):
        page = doc.load_page(page_no)
        for x0, y0, x1, y1, text, block_no, block_type in sorted(
            page.get_text("blocks"), key=lambda x: x[1]
        ):
            if block_type != 0 or (page_no == title["page"] and y1 < title["to"].y):
                continue
            if (
                next_title
                and page_no == next_title["page"]
                and y1 >= next_title["to"].y
            ):
                return
            yield x0, y0, x1, y1, text


def get_toc_item(item_id: int, item: tuple[int, str, int, dict]) -> PdfElement:
    """
    Return a TocItem, built from a PyMuPdf toc item

    Args:
        item_id (int): index in toc
        item (tuple): toc item
    """
    return TocItem(
        id=item_id,
        level=item[0],
        title=item[1],
        page=item[2] - 1,
        x=item[3]["to"].x if "to" in item[3] else 0.0,
        y=item[3]["to"].y if "to" in item[3] else 0.0,
    )


def get_pdf_info(pdf_id: int, pdf: str) -> PdfInfo:
    """
    Return a PdfInfo object, with information about the PDF document.
    """
    with open_pdf(pdf) as doc:
        return PdfInfo(
            id=pdf_id,
            name=pdf,
            n_pages=doc.page_count,
            toc=[
                get_toc_item(item_id, item)
                for item_id, item in enumerate(doc.get_toc(simple=False))
            ],
        )


# def get_toc(pdf: str, add_text_blocks=False) -> list[PdfElement]:
#     """
#     Return a list with the table of contents of the PDF document.

#     Args:
#         pdf (str): PDF document
#     """
#     with open_pdf(pdf) as doc:
#         toc = [

#             pdf_element_from_toc(i, item)
#             for i, item in enumerate(doc.get_toc(simple=False))
#         ]
#         page_count = doc.page_count

#     all_titles = []
#     for ititle, (title, next_title) in enumerate(
#         pairwise(toc + [{}])
#     ):  # add empty title for last one
#         if add_text_blocks:
#             text_blocks = list(get_text_blocks(doc, title, next_title))
#             toc[ititle].text_blocks = text_blocks
#             toc[ititle].text = "\n".join(i[-1] for i in toc[ititle].text_blocks)
#         all_titles = [j for i, j in enumerate(all_titles) if i < title.level - 1] + [
#             title.title
#         ]
#         toc[ititle].last_page = next_title.page if next_title else page_count
#         toc[ititle].all_titles = all_titles
#     return toc


def get_text_block(block: dict) -> TextBlock:
    "Convert text block dictionary from PyMuPdf to TextBlock object"
    return TextBlock(
        bbox=block["bbox"],
        lines=[
            Line(bbox=line["bbox"], spans=[Span(**span) for span in line["spans"]])
            for line in block["lines"]
        ],
    )


def get_page_content(page: fitz.Page) -> list[TextBlock]:
    "Return a list of text blocks from pdf page"
    return [
        get_text_block(block)
        for block in page.get_text("dict")["blocks"]
        if block["type"] == 0
    ]


def get_text_from_block(block: TextBlock) -> str:
    "Return the text from a text block, joining lines and spans"
    return "".join(span.text for line in block.lines for span in line.spans)


def get_pdf_element(pdf_info: PdfInfo, element_id: int, details: bool = False):
    """"""
    toc_item = pdf_info.toc[element_id]
    next_item = (
        pdf_info.toc[element_id + 1] if element_id < len(pdf_info.toc) - 1 else None
    )

    def filter_text_block(block, page_no, toc_item, next_item):
        y1 = block.bbox[3]
        if page_no == toc_item.page and y1 < toc_item.y:
            return False
        if next_item and page_no == next_item.page and y1 >= next_item.y:
            return False
        return True

    with open_pdf(pdf_info.name) as doc:
        text_blocks = []
        for page_no in range(toc_item.page, next_item.page + 1 if next_item else pdf_info.n_pages):
            page = doc.load_page(page_no)
            text_blocks.extend(
                [
                    block
                    for block in get_page_content(page)
                    if filter_text_block(block, page_no, toc_item, next_item)
                ]
            )
        text = "\n".join(get_text_from_block(block) for block in text_blocks)
        return PdfElement(blocks=text_blocks if details else [], text=text, **toc_item.__dict__)


# def get_pdf_elements(pdf_info: PdfInfo, details: bool = False) -> list[PdfElement]:
#     elements = []
#     with open_pdf(pdf_info.name) as doc:
#         for page_no in range(pdf_info.n_pages):
#             page = doc.load_page(page_no)
#             text_blocks = get_page_content(page)
#             text = "\n".join(get_text_from_block(block) for block in text_blocks)
#             elements.append()
    
#     return PdfElement(text=get_text_from_block(block))