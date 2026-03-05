import streamlit as st
import fitz
import pytesseract
from PIL import Image
import io
import zipfile

st.set_page_config(page_title="PDF OCR", layout="wide")

st.title("📄 PDF OCR")
st.write("Upload a PDF and extract **page-wise OCR text**.")

uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])


# Convert PDF → Images (in memory)
def pdf_to_images(pdf_bytes):

    images = []

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    for page_index in range(len(doc)):

        page = doc.load_page(page_index)

        pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))

        img_bytes = pix.tobytes("png")

        image = Image.open(io.BytesIO(img_bytes))

        images.append(image)

    return images


# Run OCR with preview + progress
def run_ocr(images):

    results = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    preview_col, info_col = st.columns([1,4])
    page_preview = preview_col.empty()

    total_pages = len(images)

    for i, image in enumerate(images):

        status_text.text(f"OCR Processing Page {i+1}/{total_pages}")

        page_preview.image(
            image,
            caption=f"Page {i+1}",
            width=120   # tiny preview
        )

        text = pytesseract.image_to_string(
            image,
            lang="hin+eng"
        )

        results.append({
            "page": i + 1,
            "text": text
        })

        progress_bar.progress((i + 1) / total_pages)

    status_text.success("OCR Completed ✅")

    return results


# Create ZIP file in memory
def create_zip(results):

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:

        for page in results:

            filename = f"pg{page['page']}.txt"

            zip_file.writestr(
                filename,
                page["text"]
            )

    zip_buffer.seek(0)

    return zip_buffer


# Main app logic
if uploaded_pdf:

    pdf_bytes = uploaded_pdf.read()

    if st.button("Run OCR"):

        with st.spinner("Extracting pages..."):
            images = pdf_to_images(pdf_bytes)

        st.success(f"{len(images)} pages extracted")

        results = run_ocr(images)

        zip_file = create_zip(results)

        st.download_button(
            label="📥 Download OCR as ZIP",
            data=zip_file,
            file_name="ocr_pages.zip",
            mime="application/zip"
        )