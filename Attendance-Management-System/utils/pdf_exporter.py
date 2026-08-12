import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from models.settings import CollegeSettings

def generate_pdf_report(title, subtitle, headers, data_rows, summary_stats=None):
    """
    Generates a professional PDF report with dynamic College Branding in header.
    Returns BytesIO object containing PDF bytes.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    settings = CollegeSettings.get_settings()
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E293B'),
        alignment=1 # Center
    )
    meta_style = ParagraphStyle(
        'CollegeMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B'),
        alignment=1 # Center
    )
    report_title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        alignment=0 # Left
    )
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=0
    )
    cell_header_style = ParagraphStyle(
        'CellHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=0
    )
    cell_body_style = ParagraphStyle(
        'CellBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155'),
        alignment=0
    )

    story = []

    # Dynamic Header Section
    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads', settings.college_logo)
    header_content = []
    
    header_content.append(Paragraph(f"<b>{settings.college_name.upper()}</b>", title_style))
    header_content.append(Paragraph(f"{settings.address} | Phone: {settings.contact_number} | Email: {settings.email_address}", meta_style))
    header_content.append(Paragraph(f"Academic Year: {settings.academic_year} | Principal: {settings.principal_name}", meta_style))

    if os.path.exists(logo_path) and settings.college_logo != 'default_logo.png':
        try:
            img = RLImage(logo_path, width=50, height=50)
            header_table = Table([[img, header_content]], colWidths=[60, 460])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (0,0), 'CENTER')
            ]))
            story.append(header_table)
        except Exception:
            story.extend(header_content)
    else:
        story.extend(header_content)

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=15))

    # Report Title & Subtitle
    story.append(Paragraph(title, report_title_style))
    if subtitle:
        story.append(Spacer(1, 4))
        story.append(Paragraph(subtitle, subtitle_style))
    story.append(Spacer(1, 12))

    # Summary Statistics Box (if provided)
    if summary_stats:
        stat_cells = []
        for k, v in summary_stats.items():
            stat_cells.append([
                Paragraph(f"<b>{k}:</b>", cell_body_style),
                Paragraph(str(v), cell_body_style)
            ])
        stat_table = Table(stat_cells, colWidths=[120, 380])
        stat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(stat_table)
        story.append(Spacer(1, 12))

    # Data Table
    table_data = []
    # Header row
    table_data.append([Paragraph(h, cell_header_style) for h in headers])

    # Body rows
    for row in data_rows:
        row_cells = []
        for cell in row:
            row_cells.append(Paragraph(str(cell), cell_body_style))
        table_data.append(row_cells)

    # Dynamic column widths
    available_width = 520
    col_count = len(headers)
    col_width = available_width / col_count if col_count > 0 else available_width

    report_table = Table(table_data, colWidths=[col_width] * col_count)
    report_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1F5F9')])
    ]))

    story.append(report_table)

    # Footer note
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'FooterNote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        textColor=colors.HexColor('#94A3B8'),
        alignment=2 # Right
    )
    story.append(Paragraph(f"Generated automatically by {settings.college_name} Attendance System", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
