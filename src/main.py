from fastapi import FastAPI, status, UploadFile, HTTPException
from fastapi.responses import FileResponse  # StreamingResponse
from pathlib import Path
import fitz
from .schemas import PdfElement, PdfInfo, Block
from .utils import open_file

description = """
Liseuse et recherche intelligente pour les autorités environnementales

API pour récupérer un fichier pdf et son contenu
"""


app = FastAPI(title="LIRIAe API",
              description=description)


pdf_list = [
    {
        "id": 1,
        "name": "test.pdf",
        "n_pages": 241
    }
]


@app.post("/pdf", response_model=PdfInfo)
def upload_pdf(file: UploadFile):
    # TODO: add info as argument
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {"filename": file.filename}


@app.get("/pdf/{pdf_id}")
async def get_pdf(pdf_id: int):
    """Return pdf file"""
    # raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    # Get image from the database
    pdf_info = await get_pdf_info(pdf_id)
    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return FileResponse(Path("data") / pdf_info["name"], headers=headers, media_type='application/pdf')
    # def iterfile():
    #     with open_file(pdf_info["name"], 'rb') as pdf_file:
    #         yield from pdf_file

    # return StreamingResponse(iterfile(), headers=headers, media_type='application/pdf')


@app.get("/pdf/info/{pdf_id}", response_model=PdfInfo)
async def get_pdf_info(pdf_id: int):
    """Return pdf file info"""
    return pdf_list[pdf_id - 1]


@app.get("/pdf", response_model=list[PdfInfo])
def list_pdfs():
    """Return the list of pdf files available"""
    return pdf_list


@app.get("/pdf_elements", response_model=list[PdfElement])
def get_pdf_elements(pdf_id: str):
    """Return all elements from a pdf"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@app.get("/pdf_elements/{item_id}", response_model=PdfElement)
def get_pdf_element(pdf_id: str, item_id: str):
    """Return an element from a pdf"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {}


# @app.get("/pdf_elements/details/{item_id}", response_model=PdfElementDetails)
# def get_pdf_element_details(pdf_id: str, item_id: str):
#     """Return details about pdf element: paragraphs, lines, word and the associated position, font, ..."""
#     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
#     return {}

@app.get("/page_structure", response_model=list[Block])
def get_page_structure(pdf_id: str, page_number: int):
    pdf_info = get_pdf_info(pdf_id)
    with open_file(pdf_info["name"]) as pdf_file:
        with fitz.open(pdf_file) as doc:
            page = doc.load_page(page_number)
            return page.get_text("dict")["blocks"]
