
from fpdf import FPDF
data = [['Manufacturer', 'Product']]

def createpdf(obj):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('pep', '', r"Montserrat/Montserrat-SemiBold.ttf", uni=True)
    pdf.add_font('reg', '', r"Montserrat/Montserrat-Regular.ttf", uni=True)
    pdf.add_font('zhop', '', r"Montserrat/Montserrat-Light.ttf", uni=True)
    pdf.set_font("pep", size=28)
    pdf.image("Logo.png", x=12, y=15, w=70)
    pdf.cell(200, 65, txt="My Cart", ln=1, align="L")
    pdf.set_font("reg", size=24)
    col_width = pdf.w / 2.5
    row_height = pdf.font_size
    c = 0
    for row in data:
        if c != 0:
            pdf.set_font("zhop", size=20)
        for item in row:
            pdf.cell(col_width, row_height*1,
                     txt=item, border=1)
        pdf.ln(row_height*1)
        c+=1
    pdf.image("p.png", x=3, y=250, w=200)
    pdf.output("demo.pdf")
