import streamlit as st
import fitz
import pytesseract
from PIL import Image
import io

st.set_page_config(page_title="PDF OCR", layout="wide")

st.title("📄 PDF OCR")
st.write("Upload a PDF and extract **page-wise OCR text**. No files are stored on disk.")

uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])


def pdf_to_images(pdf_bytes):
    images = []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_index in range(len(doc)):

        page = doc.load_page(page_index)

        pix = page.get_pixmap(matrix=fitz.Matrix(3,3))

        img_bytes = pix.tobytes("png")

        image = Image.open(io.BytesIO(img_bytes))

        images.append(image)

    return images


def run_ocr(images):

    results = []

    for i, image in enumerate(images):

        text = pytesseract.image_to_string(
            image,
            lang="hin+eng"
        )

        results.append({
            "page": i + 1,
            "text": text
        })

    return results


if uploaded_pdf:

    pdf_bytes = uploaded_pdf.read()

    if st.button("Run OCR"):

        with st.spinner("Extracting pages..."):

            images = pdf_to_images(pdf_bytes)

        st.success(f"{len(images)} pages extracted")

        with st.spinner("Running OCR..."):

            results = run_ocr(images)

        st.success("OCR completed")

        for page_data in results:

            st.subheader(f"Page {page_data['page']}")

            st.text_area(
                "OCR Text",
                page_data["text"],
                height=200
            )