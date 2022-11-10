from fastapi import FastAPI, status, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from .schemas import PdfElement, PdfInfo, TocTreeItem
from .utils import get_pdf_info, get_pdf_element, open_file


description = """
Liseuse et recherche intelligente pour les autorités environnementales

API pour récupérer un fichier pdf et son contenu
"""


app = FastAPI(title="LIRIAe PDF API", description=description)


pdf_list = [
    get_pdf_info(
        pdf_id=0,
        pdf="projet-outil-ae/test/19-021 - LODI_DAE_Volume 4_avec_annexes_indice 10 220301.pdf.pdf",
        # pdf="data/test.pdf"
    )
]


@app.post("/pdf", response_model=PdfInfo)
def upload_pdf(file: UploadFile):
    "Not implemented"
    # TODO: add info as argument
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    return {"filename": file.filename}


@app.get("/pdf/{pdf_id}")
async def get_pdf_by_id(pdf_id: int):
    """Return pdf file"""
    # raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
    # Get image from the database
    pdf_info = await get_pdf_info_by_id(pdf_id)
    headers = {"Content-Disposition": 'attachment; filename="out.pdf"'}
    # return FileResponse("data/test.pdf", headers=headers, media_type="application/pdf")

    def iterfile():
        with open_file(pdf_info.name, "rb") as pdf_file:
            yield from pdf_file

    return StreamingResponse(iterfile(), headers=headers, media_type="application/pdf")


@app.get("/pdf/info/{pdf_id}", response_model=PdfInfo)
async def get_pdf_info_by_id(pdf_id: int):
    """Return pdf file info"""
    try:
        return pdf_list[pdf_id]
    except IndexError:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/pdf/toc_tree/{pdf_id}", response_model=list[TocTreeItem])
async def get_toc_tree(pdf_id: int):
    "Return the table of content in tree format"
    toc = (await get_pdf_info_by_id(pdf_id)).toc
    root = TocTreeItem(id=-1, title="")
    for item in toc:
        last = root
        for _ in range(item.level - 1):
            last = last.children[-1]
        last.children.append(TocTreeItem(id=item.id, title=item.title))
    return root.children


@app.get("/pdf", response_model=list[PdfInfo])
def list_pdfs():
    """Return the list of pdf files available"""
    return pdf_list


@app.get("/pdf_element/{item_id}", response_model=PdfElement)
async def get_PDF_element(pdf_id: int, item_id: int, details: bool = False):
    """Return an element from a pdf"""
    return get_pdf_element(await get_pdf_info_by_id(pdf_id), item_id, details)
