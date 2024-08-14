from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from PyPDF2 import PdfReader, PdfWriter
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_pdf():
    # Get the text and formatting from the form input
    text_to_add1 = request.form.get('text_to_add1', '')
    font1 = request.form.get('font1', 'Arial')
    font_size1 = int(request.form.get('font_size1', '12'))
    x1 = int(request.form.get('x1', '10'))
    y1 = int(request.form.get('y1', '10'))

    text_to_add2 = request.form.get('text_to_add2', '')
    font2 = request.form.get('font2', 'Arial')
    font_size2 = int(request.form.get('font_size2', '12'))
    x2 = int(request.form.get('x2', '10'))
    y2 = int(request.form.get('y2', '30'))

    # Get the uploaded template PDF
    template_pdf = request.files.get('template_pdf')
    if template_pdf and template_pdf.filename.endswith('.pdf'):
        template_pdf_path = 'uploaded_template.pdf'
        template_pdf.save(template_pdf_path)
    else:
        return "Invalid file type. Please upload a PDF file.", 400

    with open(template_pdf_path, 'rb') as f:
        reader = PdfReader(f)

        # Create a PdfWriter object to hold the final PDF
        writer = PdfWriter()

        # Create a new PDF with FPDF to overlay the text
        overlay_buffer = io.BytesIO()
        pdf = FPDF()
        pdf.add_page()

        # Add the first text with its font, size, and coordinates
        pdf.set_font(font1, size=font_size1)
        pdf.set_xy(x1, y1)
        pdf.cell(200, 10, txt=text_to_add1, ln=1, align='C')

        # Add the second text with its font, size, and coordinates
        pdf.set_font(font2, size=font_size2)
        pdf.set_xy(x2, y2)
        pdf.cell(200, 10, txt=text_to_add2, ln=2, align='C')

        pdf_output = pdf.output(dest='S')  # Output PDF to a string
        overlay_buffer.write(pdf_output.encode('latin1'))  # Write PDF bytes to buffer
        overlay_buffer.seek(0)

        # Read the overlay PDF
        overlay_reader = PdfReader(overlay_buffer)

        # Add the overlay to each page of the template
        for page_num in range(len(reader.pages)):
            template_page = reader.pages[page_num]
            overlay_page = overlay_reader.pages[0]  # Assuming the overlay is a single-page PDF
            template_page.merge_page(overlay_page)
            writer.add_page(template_page)

        # Write the final PDF to a new buffer
        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

    # Send the merged PDF as an attachment
    return send_file(
        output_buffer,
        as_attachment=True,
        download_name='generated.pdf',
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(debug=True)
