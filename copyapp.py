import streamlit as st
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import utils
import tempfile
import io
import requests

def add_watermark(input_pdf, watermark_url, transparency, style):
    # Fetch the watermark image from URL
    response = requests.get(watermark_url)
    watermark_image = io.BytesIO(response.content)
    
    # Create a watermark PDF with the given image
    watermark_pdf = io.BytesIO()
    c = canvas.Canvas(watermark_pdf, pagesize=letter)
    c.setFillAlpha(transparency)  # Set transparency
    
    img = utils.ImageReader(watermark_image)
    img_width, img_height = img.getSize()
    aspect = img_height / float(img_width)
    width = 1.5 * inch  # Adjust width for your watermark
    height = aspect * width
    
    if style == 'mosaic':
        for y in range(0, int(letter[1]), int(height)):
            for x in range(0, int(letter[0]), int(width)):
                c.drawImage(watermark_image, x, y, width=width, height=height)
    elif style == 'centered':
        c.drawImage(watermark_image, (letter[0] - width) / 2, (letter[1] - height) / 2, width=width, height=height)
    
    c.save()
    watermark_pdf.seek(0)
    
    # Read the input PDF
    input_pdf = PdfReader(input_pdf)
    watermark_pdf = PdfReader(watermark_pdf)
    output_pdf = PdfWriter()
    
    # Add the watermark to each page
    for i in range(len(input_pdf.pages)):
        page = input_pdf.pages[i]
        page.merge_page(watermark_pdf.pages[0])
        output_pdf.add_page(page)
    
    # Write the watermarked PDF to a BytesIO object
    output_pdf_stream = io.BytesIO()
    output_pdf.write(output_pdf_stream)
    output_pdf_stream.seek(0)
    
    return output_pdf_stream

def main():
    st.title("PDF Merger and Watermarker")

    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type="pdf")
    watermark = st.selectbox(
        "Select Watermark", 
        [
            "https://thrassvent.de/wp-content/uploads/2024/07/COPY-LOGO-1.png",
            "https://thrassvent.de/wp-content/uploads/2024/07/COPY-LOGO-2.png",
            "https://thrassvent.de/wp-content/uploads/2024/07/COPY-LOGO-3.png",
            "https://thrassvent.de/wp-content/uploads/2024/07/COPY-LOGO-4.png"
        ]
    )
    style = st.selectbox("Watermark Style", ["mosaic", "centered"])
    transparency = st.slider("Transparency", 0.0, 1.0, 0.5)

    if st.button("Merge and Watermark PDFs"):
        if uploaded_files and watermark:
            merged_pdf = PdfWriter()
            for uploaded_file in uploaded_files:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    merged_pdf.add_page(page)

            temp_merged_pdf = tempfile.NamedTemporaryFile(delete=False)
            merged_pdf.write(temp_merged_pdf)
            temp_merged_pdf.close()

            watermarked_pdf_stream = add_watermark(temp_merged_pdf.name, watermark, transparency, style)
            
            st.download_button(
                label="Download Merged and Watermarked PDF",
                data=watermarked_pdf_stream,
                file_name="merged_watermarked.pdf",
                mime="application/pdf"
            )

if __name__ == "__main__":
    main()
