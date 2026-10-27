from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)

from reportlab.lib.enums import (
    TA_RIGHT,
    TA_CENTER,
)

from reportlab.lib.units import mm


# =========================================================
# PREMIUM CERTIHIRE INVOICE
# =========================================================

def generate_invoice_pdf(payment):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    # =====================================================
    # COLORS
    # =====================================================

    BLUE = colors.HexColor("#2563EB")
    DARK = colors.HexColor("#0F172A")
    TEXT = colors.HexColor("#334155")
    MUTED = colors.HexColor("#64748B")

    LIGHT = colors.HexColor("#F8FAFC")
    BORDER = colors.HexColor("#E2E8F0")

    GREEN = colors.HexColor("#16A34A")
    GREEN_BG = colors.HexColor("#DCFCE7")

    BLUE_BG = colors.HexColor("#EFF6FF")


    # =====================================================
    # STYLES
    # =====================================================

    brand_style = ParagraphStyle(
        "BrandStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=28,
        textColor=BLUE,
    )


    tagline_style = ParagraphStyle(
        "TaglineStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=MUTED,
    )


    invoice_style = ParagraphStyle(
        "InvoiceStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=28,
        alignment=TA_RIGHT,
        textColor=DARK,
    )


    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=MUTED,
    )


    normal_style = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=TEXT,
    )


    bold_style = ParagraphStyle(
        "BoldStyle",
        parent=normal_style,
        fontName="Helvetica-Bold",
        textColor=DARK,
    )


    section_style = ParagraphStyle(
        "SectionStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=DARK,
    )


    amount_style = ParagraphStyle(
        "AmountStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        alignment=TA_RIGHT,
        textColor=BLUE,
    )


    paid_style = ParagraphStyle(
        "PaidStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=GREEN,
    )


    signature_style = ParagraphStyle(
        "SignatureStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        alignment=TA_RIGHT,
        textColor=MUTED,
    )


    footer_style = ParagraphStyle(
        "FooterStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=MUTED,
    )


    # =====================================================
    # PAYMENT INFORMATION
    # =====================================================

    invoice_number = (
        f"INV-{payment.id:06d}"
    )


    if payment.order:

        order_id = (
            f"#{payment.order.id}"
        )

    else:

        order_id = "Pending"


    buyer_name = (
        payment.buyer.username
    )


    buyer_email = (
        payment.buyer.email
    )


    seller_name = (
        payment.gig.seller.username
    )


    gig_title = (
        payment.gig.title
    )


    payment_date = (
        payment.created_at.strftime(
            "%d %b %Y"
        )
    )


    payment_time = (
        payment.created_at.strftime(
            "%I:%M %p"
        )
    )


    cashfree_order_id = (
        payment.cashfree_order_id
    )


    # Safely format amount

    try:

        amount_value = float(
            payment.amount
        )

        amount_text = (
            f"₹ {amount_value:,.2f}"
        )

    except (TypeError, ValueError):

        amount_text = (
            f"₹ {payment.amount}"
        )


    elements = []


    # =====================================================
    # HEADER
    # =====================================================

    header_table = Table(

        [

            [

                Paragraph(
                    "CERTIHIRE",
                    brand_style
                ),

                Paragraph(
                    "INVOICE",
                    invoice_style
                ),

            ],

            [

                Paragraph(
                    "Trusted Freelance Marketplace",
                    tagline_style
                ),

                Paragraph(
                    f"Invoice No: "
                    f"<b>{invoice_number}</b>",
                    small_style
                ),

            ],

        ],

        colWidths=[
            105 * mm,
            65 * mm,
        ]

    )


    header_table.setStyle(

        TableStyle([

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                0,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                0,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),

        ])

    )


    elements.append(
        header_table
    )


    elements.append(
        Spacer(
            1,
            5 * mm
        )
    )


    elements.append(

        HRFlowable(

            width="100%",

            thickness=1.2,

            color=BLUE,

        )

    )


    elements.append(
        Spacer(
            1,
            6 * mm
        )
    )


    # =====================================================
    # PAYMENT STATUS
    # =====================================================

    status_table = Table(

        [

            [

                Paragraph(
                    "<b>PAYMENT STATUS</b>",
                    small_style
                ),

                Paragraph(
                    "✓  PAID",
                    paid_style
                ),

                Paragraph(
                    "<b>PAYMENT DATE</b>",
                    small_style
                ),

                Paragraph(
                    payment_date,
                    bold_style
                ),

            ]

        ],

        colWidths=[
            35 * mm,
            35 * mm,
            35 * mm,
            65 * mm,
        ]

    )


    status_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                LIGHT,
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                BORDER,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8,
            ),

        ])

    )


    elements.append(
        status_table
    )


    elements.append(
        Spacer(
            1,
            7 * mm
        )
    )


    # =====================================================
    # BUYER / SELLER
    # =====================================================

    buyer_block = f"""
    <b>BILL TO</b><br/><br/>

    <font size="11">
        <b>{buyer_name}</b>
    </font>

    <br/>

    {buyer_email}

    <br/>

    Buyer / Customer
    """


    seller_block = f"""
    <b>SERVICE PROVIDER</b><br/><br/>

    <font size="11">
        <b>{seller_name}</b>
    </font>

    <br/>

    CertiHire Seller

    <br/>

    Freelance Service Provider
    """


    party_table = Table(

        [

            [

                Paragraph(
                    buyer_block,
                    normal_style
                ),

                Paragraph(
                    seller_block,
                    normal_style
                ),

            ]

        ],

        colWidths=[
            85 * mm,
            85 * mm,
        ]

    )


    party_table.setStyle(

        TableStyle([

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                BORDER,
            ),

            (
                "INNERGRID",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER,
            ),

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                colors.white,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

        ])

    )


    elements.append(
        party_table
    )


    elements.append(
        Spacer(
            1,
            7 * mm
        )
    )


    # =====================================================
    # SERVICE DETAILS
    # =====================================================

    service_table = Table(

        [

            [

                Paragraph(
                    "<b>SERVICE DESCRIPTION</b>",
                    normal_style
                ),

                Paragraph(
                    "<b>QTY</b>",
                    normal_style
                ),

                Paragraph(
                    "<b>AMOUNT</b>",
                    normal_style
                ),

            ],

            [

                Paragraph(

                    f"""
                    <b>{gig_title}</b>

                    <br/>

                    <font size="8">
                    Freelance service purchased
                    through CertiHire
                    </font>
                    """,

                    normal_style

                ),

                Paragraph(
                    "1",
                    normal_style
                ),

                Paragraph(
                    amount_text,
                    bold_style
                ),

            ],

        ],

        colWidths=[
            110 * mm,
            20 * mm,
            40 * mm,
        ]

    )


    service_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                DARK,
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                BORDER,
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "ALIGN",
                (1, 0),
                (-1, -1),
                "RIGHT",
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),

        ])

    )


    elements.append(
        service_table
    )


    elements.append(
        Spacer(
            1,
            6 * mm
        )
    )


    # =====================================================
    # ORDER SUMMARY
    # =====================================================

    summary_table = Table(

        [

            [

                Paragraph(

                    f"""
                    <b>Order ID</b>

                    <br/>

                    {order_id}

                    <br/><br/>

                    <b>Payment Method</b>

                    <br/>

                    Cashfree Secure Payment
                    """,

                    normal_style

                ),

                Paragraph(

                    f"""
                    <font size="9">
                    TOTAL AMOUNT PAID
                    </font>

                    <br/>

                    {amount_text}
                    """,

                    amount_style

                ),

            ]

        ],

        colWidths=[
            95 * mm,
            75 * mm,
        ]

    )


    summary_table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, -1),
                BLUE_BG,
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.8,
                colors.HexColor(
                    "#BFDBFE"
                ),
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),

            (
                "ALIGN",
                (1, 0),
                (1, 0),
                "RIGHT",
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                14,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                14,
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

        ])

    )


    elements.append(
        summary_table
    )


    elements.append(
        Spacer(
            1,
            7 * mm
        )
    )


    # =====================================================
    # PAYMENT INFORMATION
    # =====================================================

    payment_info = Table(

        [

            [

                Paragraph(
                    "PAYMENT INFORMATION",
                    section_style
                )

            ],

            [

                Paragraph(

                    f"""
                    <b>Cashfree Order ID:</b>
                    {cashfree_order_id}

                    <br/>

                    <b>Payment Date:</b>
                    {payment_date}

                    <br/>

                    <b>Payment Time:</b>
                    {payment_time}

                    <br/>

                    <b>Status:</b>

                    <font color="#16A34A">
                        Successful
                    </font>
                    """,

                    normal_style

                )

            ],

        ],

        colWidths=[
            170 * mm
        ]

    )


    payment_info.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                LIGHT,
            ),

            (
                "BOX",
                (0, 0),
                (-1, -1),
                0.6,
                BORDER,
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                10,
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                12,
            ),

        ])

    )


    elements.append(
        payment_info
    )


    elements.append(
        Spacer(
            1,
            9 * mm
        )
    )


    # =====================================================
    # THANK YOU + SIGNATURE
    # =====================================================

    thank_you = Paragraph(

        """
        <b>Thank you for choosing CertiHire.</b>

        <br/>

        We appreciate your business and hope you
        have a great experience with our marketplace.
        """,

        normal_style

    )


    signature_block = Paragraph(

        """
        Authorized by

        <br/>

        <font size="12">
            <b>Lithish Kumar</b>
        </font>

        <br/>

        Founder / Administrator

        <br/>

        CertiHire
        """,

        signature_style

    )


    final_table = Table(

        [

            [

                thank_you,

                signature_block,

            ]

        ],

        colWidths=[
            95 * mm,
            75 * mm,
        ]

    )


    final_table.setStyle(

        TableStyle([

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP",
            ),

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                0,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                0,
            ),

        ])

    )


    elements.append(
        final_table
    )


    elements.append(
        Spacer(
            1,
            8 * mm
        )
    )


    # =====================================================
    # FOOTER
    # =====================================================

    elements.append(

        HRFlowable(

            width="100%",

            thickness=0.7,

            color=BORDER,

        )

    )


    elements.append(
        Spacer(
            1,
            3 * mm
        )
    )


    elements.append(

        Paragraph(

            """
            <b>CertiHire</b> • Trusted Freelance Marketplace

            <br/>

            This is a computer-generated invoice and
            does not require a physical signature.

            <br/>

            © CertiHire. All rights reserved.
            """,

            footer_style

        )

    )


    # =====================================================
    # BUILD PDF
    # =====================================================

    doc.build(
        elements
    )

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# SEND PAYMENT SUCCESS EMAIL
# =========================================================

def send_payment_success_email(
    request,
    payment,
    order,
    invoice_pdf
):

    invoice_number = (
        f"INV-{payment.id:06d}"
    )


    invoice_url = request.build_absolute_uri(

        f"/payments/invoice/"
        f"{payment.id}/download/"

    )


    # =====================================================
    # HTML EMAIL
    # =====================================================

    html_content = render_to_string(

        "emails/payment_success.html",

        {

            "buyer":
                payment.buyer,

            "order":
                order,

            "payment":
                payment,

            "invoice_number":
                invoice_number,

            "amount":
                payment.amount,

            "invoice_url":
                invoice_url,

        }

    )


    # =====================================================
    # PLAIN TEXT FALLBACK
    # =====================================================

    text_content = f"""

CertiHire
Trusted Freelance Marketplace

PAYMENT SUCCESSFUL
------------------

Hi {payment.buyer.username},

Your payment has been successfully
processed and your order has been confirmed.

Invoice Number:
{invoice_number}

Order ID:
#{order.id}

Service:
{payment.gig.title}

Amount Paid:
₹{payment.amount}

Payment Status:
Successful

Your professional invoice is attached
to this email as a PDF.

You can also download your invoice
from your CertiHire Payment History.

Regards,

Lithish Kumar
Founder / Administrator
CertiHire

This is an automated email.
Please do not reply directly to this message.

"""


    # =====================================================
    # CREATE EMAIL
    # =====================================================

    email = EmailMultiAlternatives(

        subject=(

            "Payment Successful | "

            f"CertiHire Invoice "
            f"{invoice_number}"

        ),

        body=text_content,

        from_email=
            settings.DEFAULT_FROM_EMAIL,

        to=[

            payment.buyer.email

        ],

    )


    # =====================================================
    # HTML VERSION
    # =====================================================

    email.attach_alternative(

        html_content,

        "text/html"

    )


    # =====================================================
    # ATTACH SAME INVOICE PDF
    # =====================================================

    email.attach(

        f"CertiHire_"
        f"{invoice_number}.pdf",

        invoice_pdf,

        "application/pdf"

    )


    # =====================================================
    # SEND EMAIL
    # =====================================================

    email.send(
        fail_silently=False
    )