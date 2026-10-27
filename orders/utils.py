from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth


def generate_certificate_pdf(order):

    buffer = BytesIO()

    # =========================================================
    # LANDSCAPE A4
    # =========================================================

    width, height = landscape(A4)

    pdf = canvas.Canvas(
        buffer,
        pagesize=(width, height)
    )

    # =========================================================
    # COLORS
    # =========================================================

    navy = colors.HexColor("#111827")
    blue = colors.HexColor("#2563EB")
    purple = colors.HexColor("#7C3AED")
    gold = colors.HexColor("#C9A227")
    light_gold = colors.HexColor("#E8D58A")
    grey = colors.HexColor("#64748B")

    # =========================================================
    # BACKGROUND
    # =========================================================

    pdf.setFillColor(colors.white)

    pdf.rect(
        0,
        0,
        width,
        height,
        fill=1,
        stroke=0
    )

    # =========================================================
    # OUTER GOLD BORDER
    # =========================================================

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(4)

    pdf.rect(
        18,
        18,
        width - 36,
        height - 36,
        fill=0,
        stroke=1
    )

    # =========================================================
    # INNER BORDER
    # =========================================================

    pdf.setStrokeColor(light_gold)
    pdf.setLineWidth(1.2)

    pdf.rect(
        28,
        28,
        width - 56,
        height - 56,
        fill=0,
        stroke=1
    )

    # =========================================================
    # DECORATIVE CORNERS
    # =========================================================

    corner_size = 18

    corners = [
        (28, 28),
        (width - 28, 28),
        (28, height - 28),
        (width - 28, height - 28),
    ]

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(1)

    for x, y in corners:

        pdf.circle(
            x,
            y,
            4,
            stroke=1,
            fill=0
        )

        if x < width / 2:

            pdf.line(
                x,
                y,
                x + corner_size,
                y
            )

        else:

            pdf.line(
                x,
                y,
                x - corner_size,
                y
            )

        if y < height / 2:

            pdf.line(
                x,
                y,
                x,
                y + corner_size
            )

        else:

            pdf.line(
                x,
                y,
                x,
                y - corner_size
            )

    # =========================================================
    # CERTIHIRE BRAND
    # =========================================================

    pdf.setFillColor(blue)

    pdf.setFont(
        "Helvetica-Bold",
        15
    )

    pdf.drawCentredString(
        width / 2,
        height - 65,
        "CERTIHIRE"
    )

    # =========================================================
    # SMALL VERIFIED TEXT
    # =========================================================

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawCentredString(
        width / 2,
        height - 83,
        "Verified Freelance Marketplace"
    )

    # =========================================================
    # MAIN TITLE
    # =========================================================

    pdf.setFillColor(navy)

    pdf.setFont(
        "Times-Bold",
        38
    )

    pdf.drawCentredString(
        width / 2,
        height - 135,
        "CERTIFICATE"
    )

    # =========================================================
    # OF COMPLETION
    # =========================================================

    pdf.setFont(
        "Times-Roman",
        23
    )

    pdf.drawCentredString(
        width / 2,
        height - 165,
        "OF COMPLETION"
    )

    # =========================================================
    # GOLD DIVIDER
    # =========================================================

    pdf.setStrokeColor(gold)
    pdf.setLineWidth(2)

    pdf.line(
        width / 2 - 55,
        height - 185,
        width / 2 + 55,
        height - 185
    )

    # =========================================================
    # AWARDED TEXT
    # =========================================================

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        width / 2,
        height - 220,
        "This certificate is proudly awarded to"
    )

    # =========================================================
    # USER NAME
    # =========================================================

    buyer_name = order.seller.username

    pdf.setFillColor(navy)

    pdf.setFont(
        "Times-BoldItalic",
        30
    )

    pdf.drawCentredString(
        width / 2,
        height - 260,
        buyer_name
    )

    # =========================================================
    # NAME UNDERLINE
    # =========================================================

    name_width = stringWidth(
        buyer_name,
        "Times-BoldItalic",
        30
    )

    pdf.setStrokeColor(light_gold)
    pdf.setLineWidth(1)

    pdf.line(
        width / 2 - name_width / 2,
        height - 270,
        width / 2 + name_width / 2,
        height - 270
    )

    # =========================================================
    # COMPLETION MESSAGE
    # =========================================================

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        11
    )

    pdf.drawCentredString(
        width / 2,
        height - 300,
        "for successfully completing their first freelance"
    )

    pdf.drawCentredString(
        width / 2,
        height - 317,
        "project on CertiHire."
    )

    # =========================================================
    # GIG / PROJECT NAME
    # =========================================================

    gig_title = order.gig.title

    # Keep very long titles from overflowing

    if len(gig_title) > 70:

        gig_title = gig_title[:67] + "..."

    pdf.setFillColor(blue)

    pdf.setFont(
        "Helvetica-Bold",
        14
    )

    pdf.drawCentredString(
        width / 2,
        height - 350,
        f'"{gig_title}"'
    )

    # =========================================================
    # GOLD SEAL
    # =========================================================

    seal_x = width / 2
    seal_y = 78

    pdf.setFillColor(gold)
    pdf.setStrokeColor(gold)

    pdf.circle(
        seal_x,
        seal_y,
        31,
        fill=1,
        stroke=1
    )

    pdf.setFillColor(colors.white)

    pdf.setFont(
        "Helvetica-Bold",
        9
    )

    pdf.drawCentredString(
        seal_x,
        seal_y + 5,
        "CERTIHIRE"
    )

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.drawCentredString(
        seal_x,
        seal_y - 7,
        "VERIFIED"
    )

    # =========================================================
    # LEFT DATE SECTION
    # =========================================================

    date_x = 145

    pdf.setFillColor(navy)

    pdf.setFont(
        "Helvetica",
        11
    )

    completion_date = order.created_at.strftime(
        "%d %B %Y"
    )

    pdf.drawCentredString(
        date_x,
        92,
        completion_date
    )

    pdf.setStrokeColor(gold)

    pdf.line(
        date_x - 75,
        82,
        date_x + 75,
        82
    )

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        date_x,
        68,
        "DATE OF COMPLETION"
    )

    # =========================================================
    # RIGHT SIGNATURE
    # =========================================================

    signature_x = width - 145

    pdf.setFillColor(navy)

    pdf.setFont(
        "Times-Italic",
        18
    )

    pdf.drawCentredString(
        signature_x,
        92,
        "Lithish Kumar"
    )

    pdf.setStrokeColor(gold)

    pdf.line(
        signature_x - 80,
        82,
        signature_x + 80,
        82
    )

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        9
    )

    pdf.drawCentredString(
        signature_x,
        68,
        "FOUNDER / ADMINISTRATOR"
    )

    # =========================================================
    # FOOTER
    # =========================================================

    pdf.setFillColor(grey)

    pdf.setFont(
        "Helvetica",
        7
    )

    pdf.drawCentredString(
        width / 2,
        40,
        "This certificate recognizes the successful completion of a freelance project on CertiHire."
    )

    # =========================================================
    # FINISH
    # =========================================================

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()