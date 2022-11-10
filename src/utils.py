import os
import s3fs
import fitz
import itertools
from contextlib import contextmanager

from .schemas import PdfElement


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
    if "AWS_S3_ENDPOINT" in os.environ:
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


def pdf_element_from_toc(item_id: int, item: tuple) -> PdfElement:
    "Return a PdfElement, built from a toc entry"
    return PdfElement(
        id=item_id,
        level=item[0],
        title=item[1],
        page=item[2] - 1,
        x=item[3]["to"].x if "to" in item[3] else 0.0,
        y=item[3]["to"].y if "to" in item[3] else 0.0,
    )


def get_toc(pdf: str, add_text_blocks=False) -> list[PdfElement]:
    """
    Return a list with the table of contents of the PDF document.

    Args:
        pdf (str): PDF document
    """
    with open_pdf(pdf) as doc:
        toc = [
            pdf_element_from_toc(i, item)
            for i, item in enumerate(doc.get_toc(simple=False))
        ]
        page_count = doc.page_count

    all_titles = []
    for ititle, (title, next_title) in enumerate(
        pairwise(toc + [{}])
    ):  # add empty title for last one
        if add_text_blocks:
            text_blocks = list(get_text_blocks(doc, title, next_title))
            toc[ititle].text_blocks = text_blocks
            toc[ititle].text = "\n".join(i[-1] for i in toc[ititle].text_blocks)
        all_titles = [j for i, j in enumerate(all_titles) if i < title.level - 1] + [
            title.title
        ]
        toc[ititle].last_page = next_title.page if next_title else page_count
        toc[ititle].all_titles = all_titles
    return toc
