from fastapi import FastAPI, status, UploadFile, HTTPException
from fastapi.responses import FileResponse  # StreamingResponse
from pathlib import Path
from .schemas import PdfElement, PdfInfo
from .utils import get_pdf_info, get_pdf_element


description = """
Liseuse et recherche intelligente pour les autorités environnementales

API pour récupérer un fichier pdf et son contenu
"""


app = FastAPI(title="LIRIAe API", description=description)


# pdf_list = [{"id": 1, "name": "test.pdf", "n_pages": 241}]
pdf_list = [get_pdf_info(pdf_id=1, pdf="test.pdf")]


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
    headers = {"Content-Disposition": 'attachment; filename="out.pdf"'}
    return FileResponse(
        Path("data") / pdf_info["name"], headers=headers, media_type="application/pdf"
    )
    # def iterfile():
    #     with open_file(pdf_info["name"], 'rb') as pdf_file:
    #         yield from pdf_file

    # return StreamingResponse(iterfile(), headers=headers, media_type='application/pdf')


@app.get("/pdf/info/{pdf_id}", response_model=PdfInfo)
async def get_PDF_info(pdf_id: int):
    """Return pdf file info"""
    return pdf_list[pdf_id - 1]


@app.get("/pdf", response_model=list[PdfInfo])
def list_pdfs():
    """Return the list of pdf files available"""
    return pdf_list


@app.get("/pdf_element/{item_id}", response_model=PdfElement)
async def get_PDF_element(pdf_id: int, item_id: int, details: bool = False):
    """Return an element from a pdf"""
    return get_pdf_element(await get_PDF_info(pdf_id), item_id, details)
