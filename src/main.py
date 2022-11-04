from fastapi import FastAPI, status, UploadFile, HTTPException, Response
from pydantic import BaseModel


app = FastAPI()


@app.post("/pdf")
def upload_pdf(file: UploadFile):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {"filename": file.filename}


class PdfInfo(BaseModel):
    id: str
    name: str
    description: str | None = None
    n_pages: int


class PdfElementDetails(BaseModel):
    pass


@app.get("/pdf/{id}")
async def get_pdf_from_id(pdf_id: int):
    """Return pdf file"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    # Get image from the database
    pdf = ...
    headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}
    return Response(pdf, headers=headers, media_type='application/pdf')


@app.get("/pdf", response_model=list[PdfInfo])
def list_pdfs():
    """Return the list of pdf files available"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return []


class PdfElement(BaseModel):
    """Partie élementaire d'un pdf pour la recherche: contenu entre deux niveaux de titres"""
    id: str
    title: str
    all_titles: list[str]
    text: str
    # TODO: add low-level details ?


@app.get("/pdf_element/{pdf_id}", response_model=PdfElement)
def get_pdf_element(pdf_id: str, item_id: str):
    """Partie élementaire d'un pdf pour la recherche: contenu entre deux niveaux de titres"""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {}


@app.get("/pdf_element/details/{pdf_id}", response_model=PdfElementDetails)
def get_pdf_element_details(pdf_id: str, item_id: str):
    """Return details about pdf element: paragraphs, lines, word and the associated position, font, ..."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {}
