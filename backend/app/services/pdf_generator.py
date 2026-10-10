import io
import os
import base64
from datetime import datetime
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from typing import Dict, Any, List

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw custom running headers/footers.
    """
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Colors
        garnet = colors.HexColor("#7D2E3B")
        gray_text = colors.HexColor("#6B6565")
        light_border = colors.HexColor("#EADCDC")

        # Top Header (on pages after cover / first page)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(garnet)
        self.drawString(36, 762, "LumiFace AI — Scientific Personal Beauty Diagnostics Report")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(gray_text)
        self.drawRightString(576, 762, "Confidential Diagnostic Report")

        self.setStrokeColor(light_border)
        self.setLineWidth(0.5)
        self.line(36, 754, 576, 754)

        # Bottom Footer
        self.line(36, 45, 576, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(gray_text)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 32, "LumiFace Beauty-Tech Engine v2.4 • Non-Invasive Geometric Analysis")
        self.drawRightString(576, 32, page_text)

        self.restoreState()


class PDFReportGenerator:
    """
    Generates high-quality, luxury Korean beauty-inspired PDF diagnostic reports.
    """
    def generate(self, analysis_data: Dict[str, Any], face_image_base64: str = None) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=54,
            bottomMargin=54
        )

        story = []
        styles = getSampleStyleSheet()

        # Custom Palette
        garnet = colors.HexColor("#7D2E3B")
        rose_pink = colors.HexColor("#C86D7C")
        bg_blush = colors.HexColor("#FDF2F4")
        bg_ivory = colors.HexColor("#FAF7F2")
        bg_lavender = colors.HexColor("#F5EFFB")
        border_pink = colors.HexColor("#F5DDE1")
        border_light = colors.HexColor("#EADCDC")
        text_dark = colors.HexColor("#1F1F1F")
        text_muted = colors.HexColor("#555555")

        # Typography Styles
        title_style = ParagraphStyle(
            'LumiTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=garnet,
            spaceAfter=2
        )

        subtitle_style = ParagraphStyle(
            'LumiSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=text_muted,
            spaceAfter=8
        )

        section_heading = ParagraphStyle(
            'LumiSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=garnet,
            spaceBefore=8,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'LumiBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=text_dark
        )

        body_bold = ParagraphStyle(
            'LumiBodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        caption_style = ParagraphStyle(
            'LumiCaption',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            leading=10,
            textColor=text_muted
        )

        badge_style = ParagraphStyle(
            'LumiBadge',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            leading=10,
            textColor=garnet
        )

        analysis_id = analysis_data.get("analysis_id", "N/A")
        created_at_raw = analysis_data.get("created_at", "")
        try:
            date_str = datetime.fromisoformat(created_at_raw.replace("Z", "")).strftime("%B %d, %Y at %I:%M %p")
        except Exception:
            date_str = datetime.utcnow().strftime("%B %d, %Y")

        face_shape = analysis_data.get("face_shape", {})
        skin_tone = analysis_data.get("skin_tone", {})
        ratios = face_shape.get("ratios", {})
        measurements = face_shape.get("measurements", {})
        color_palette = analysis_data.get("color_palette", {})
        lighting = analysis_data.get("lighting", {})

        user_name = analysis_data.get("user_full_name") or analysis_data.get("full_name") or "Valued Client"

        # --- HEADER BANNER ---
        header_table = Table([
            [
                Paragraph("<b>Your Personal Beauty Blueprint</b>", title_style),
                Paragraph(f"<b>Prepared Exclusively For:</b> {user_name}<br/><b>Analysis ID:</b> {analysis_id[:18]}...<br/><b>Date:</b> {date_str}", ParagraphStyle('RightMeta', parent=caption_style, alignment=2))
            ]
        ], colWidths=[4.0*inch, 3.5*inch])
        header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(header_table)
        story.append(Paragraph("LumiFace AI • 3D Facial Geometry, ITA° Skin Spectrum & Personal Beauty Consultation", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=garnet, spaceAfter=8))

        # --- SECTION 1: FACIAL PORTRAIT & PROFILE SUMMARY ---
        face_img_flowable = None
        target_img_b64 = face_image_base64 or analysis_data.get("annotated_image_base64")
        if target_img_b64 and "," in target_img_b64:
            try:
                header, encoded = target_img_b64.split(",", 1)
                img_data = base64.b64decode(encoded)
                pil_img = PILImage.open(io.BytesIO(img_data))
                
                # Strict aspect ratio preservation to prevent stretching
                orig_w, orig_h = pil_img.size
                max_w_px, max_h_px = 1.8 * inch, 2.2 * inch
                aspect = orig_w / float(orig_h if orig_h > 0 else 1)
                
                if aspect > (max_w_px / max_h_px):
                    render_w = max_w_px
                    render_h = max_w_px / aspect
                else:
                    render_h = max_h_px
                    render_w = max_h_px * aspect
                    
                img_temp_io = io.BytesIO()
                pil_img.save(img_temp_io, format="PNG")
                img_temp_io.seek(0)
                face_img_flowable = Image(img_temp_io, width=render_w, height=render_h)
            except Exception:
                face_img_flowable = None

        profile_rows = [
            [Paragraph("<b>Diagnostic Metric</b>", body_bold), Paragraph("<b>Analyzed Output</b>", body_bold)],
            [Paragraph("<b>Estimated Face Shape</b>", body_style), Paragraph(f"<b>{face_shape.get('face_shape', 'N/A').upper()}</b>", badge_style)],
            [Paragraph("<b>Face Length / Cheek Ratio</b>", body_style), Paragraph(f"{ratios.get('face_aspect_ratio', 'N/A')}", body_style)],
            [Paragraph("<b>Jaw / Cheekbone Ratio</b>", body_style), Paragraph(f"{ratios.get('jaw_to_cheek_ratio', 'N/A')}", body_style)],
            [Paragraph("<b>Forehead / Cheek Ratio</b>", body_style), Paragraph(f"{ratios.get('forehead_to_cheek_ratio', 'N/A')}", body_style)],
            [Paragraph("<b>ITA° Skin Angle</b>", body_style), Paragraph(f"<b>{skin_tone.get('ita_angle', 0)}°</b> ({skin_tone.get('shade', 'N/A')})", body_style)],
            [Paragraph("<b>Skin Undertone</b>", body_style), Paragraph(f"<b>{skin_tone.get('undertone', 'N/A')}</b>", body_style)],
            [Paragraph("<b>Seasonal Palette</b>", body_style), Paragraph(f"<b>{skin_tone.get('seasonal_palette', 'N/A')}</b>", badge_style)],
            [Paragraph("<b>Uncertainty Assessment</b>", body_style), Paragraph(f"{face_shape.get('uncertainty_level', 'Low')} Uncertainty", body_style)]
        ]

        profile_table = Table(profile_rows, colWidths=[2.2*inch, 3.2*inch])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), bg_blush),
            ('TEXTCOLOR', (0,0), (-1,0), garnet),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('GRID', (0,0), (-1,-1), 0.5, border_pink),
        ]))

        if face_img_flowable:
            sec1_layout = Table([[face_img_flowable, profile_table]], colWidths=[1.9*inch, 5.6*inch])
            sec1_layout.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            story.append(sec1_layout)
        else:
            story.append(profile_table)

        story.append(Spacer(1, 6))

        # --- SECTION 2: GEOMETRIC MEASUREMENTS & REASONING ---
        story.append(Paragraph("1. Facial Geometry Measurements & Documented Reasoning", section_heading))
        
        geom_measurements_data = [
            [
                Paragraph(f"<b>Face Length:</b> {measurements.get('face_length_px', 'N/A')} px", body_style),
                Paragraph(f"<b>Cheekbone Width:</b> {measurements.get('cheekbone_width_px', 'N/A')} px", body_style),
                Paragraph(f"<b>Forehead Width:</b> {measurements.get('forehead_width_px', 'N/A')} px", body_style),
                Paragraph(f"<b>Jaw Width:</b> {measurements.get('jaw_width_px', 'N/A')} px", body_style),
            ]
        ]
        geom_table = Table(geom_measurements_data, colWidths=[1.875*inch, 1.875*inch, 1.875*inch, 1.875*inch])
        geom_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_ivory),
            ('GRID', (0,0), (-1,-1), 0.5, border_light),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(geom_table)
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>Overview:</b> {face_shape.get('description', '')}", body_style))
        story.append(Paragraph(f"<b>Geometric Reasoning:</b> <i>\"{face_shape.get('reasoning', '')}\"</i>", body_style))
        story.append(Paragraph(f"<b>Uncertainty Note & Limitations:</b> {face_shape.get('limitations', '')}", caption_style))

        story.append(Spacer(1, 8))

        # --- SECTION 3: PERSONAL COLOR PALETTE ---
        story.append(Paragraph(f"2. Personal Color Analysis — {skin_tone.get('seasonal_palette', 'Season')}", section_heading))
        story.append(Paragraph(f"<b>Skin Tone Spectrum:</b> ITA° {skin_tone.get('ita_angle', 0)}° • CIE L* {skin_tone.get('lab_values', {}).get('L', 0)} | a* {skin_tone.get('lab_values', {}).get('a', 0)} | b* {skin_tone.get('lab_values', {}).get('b', 0)} • Undertone Confidence: {skin_tone.get('undertone_confidence', 'Medium')}", body_style))
        
        best_colors = color_palette.get("best_colors", [])
        worst_colors = color_palette.get("worst_colors", [])

        best_str = ", ".join([f"{c.get('name')} ({c.get('hex')})" for c in best_colors]) if best_colors else "N/A"
        worst_str = ", ".join([f"{c.get('name')} ({c.get('hex')})" for c in worst_colors]) if worst_colors else "N/A"

        color_table_data = [
            [Paragraph("<b>Recommended Best Hues</b>", body_bold), Paragraph(best_str, body_style)],
            [Paragraph("<b>Colors To Avoid</b>", body_bold), Paragraph(worst_str, body_style)]
        ]
        c_table = Table(color_table_data, colWidths=[2.0*inch, 5.5*inch])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor("#E8F5E9")),
            ('BACKGROUND', (0,1), (0,1), colors.HexColor("#FFEBEE")),
            ('GRID', (0,0), (-1,-1), 0.5, border_light),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(c_table)

        story.append(Spacer(1, 8))

        # --- SECTION 4: K-BEAUTY MAKEUP RECOMMENDATIONS ---
        story.append(Paragraph("3. Curated K-Beauty Makeup Shades", section_heading))
        makeup_list = analysis_data.get("makeup_recommendations", [])
        makeup_rows = [
            [Paragraph("<b>Product & Brand</b>", body_bold), Paragraph("<b>Category</b>", body_bold), Paragraph("<b>Shade & HEX</b>", body_bold), Paragraph("<b>Match %</b>", body_bold), Paragraph("<b>Reason / Lab Delta E</b>", body_bold)]
        ]
        for m in makeup_list:
            delta_e_text = f" (Delta E: {m.get('delta_e')})" if m.get("delta_e") is not None else ""
            makeup_rows.append([
                Paragraph(f"<b>{m.get('name')}</b><br/>{m.get('brand')}", body_style),
                Paragraph(f"{m.get('category', '').title()}", body_style),
                Paragraph(f"{m.get('shade_name')}<br/><font color='{text_muted}'>{m.get('hex_code')}</font>", body_style),
                Paragraph(f"<b>{m.get('match_score')}%</b>", body_style),
                Paragraph(f"{m.get('reason')}{delta_e_text}", body_style)
            ])

        m_table = Table(makeup_rows, colWidths=[2.2*inch, 1.0*inch, 1.6*inch, 0.8*inch, 1.9*inch])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), bg_lavender),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5D9F2")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(m_table)

        story.append(Spacer(1, 8))

        # --- SECTION 5: EYEWEAR FRAME RECOMMENDATIONS ---
        story.append(Paragraph("4. Recommended Eyewear Frame Styles", section_heading))
        eyewear_list = analysis_data.get("eyewear_recommendations", [])
        eyewear_rows = [
            [Paragraph("<b>Frame Silhouette</b>", body_bold), Paragraph("<b>Category</b>", body_bold), Paragraph("<b>Recommended Season Colors</b>", body_bold), Paragraph("<b>Score %</b>", body_bold), Paragraph("<b>Geometric Reasoning</b>", body_bold)]
        ]
        for e in eyewear_list:
            colors_str = ", ".join(e.get("recommended_colors", []))
            eyewear_rows.append([
                Paragraph(f"<b>{e.get('frame_style')}</b><br/><font color='{garnet}'>{e.get('suitability')}</font>", body_style),
                Paragraph(f"{e.get('category', '').title()}", body_style),
                Paragraph(f"{colors_str}", body_style),
                Paragraph(f"<b>{e.get('match_score')}%</b>", body_style),
                Paragraph(f"{e.get('reasoning')}", body_style)
            ])

        e_table = Table(eyewear_rows, colWidths=[2.2*inch, 0.9*inch, 1.7*inch, 0.7*inch, 2.0*inch])
        e_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), bg_ivory),
            ('GRID', (0,0), (-1,-1), 0.5, border_light),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        story.append(e_table)

        story.append(Spacer(1, 8))

        # --- SECTION 6: YOUR PERSONAL BEAUTY SUMMARY & PRIVACY NOTE ---
        story.append(Paragraph("5. Your Personal Beauty Summary & Practical Consultation Guide", section_heading))
        summary_text = (
            f"Based on your 3D facial geometry analysis ({face_shape.get('face_shape', 'N/A').upper()}) and {skin_tone.get('seasonal_palette', 'N/A')} color spectrum, "
            f"your optimal beauty strategy balances structured facial framing with muted, harmonious undertone shades. "
            f"Use recommended lipstick MLBB tints ({skin_tone.get('undertone', 'N/A')} undertone) to highlight natural lip contours. "
            f"For eyewear framing, choose styles that provide geometric contrast to your detected jaw-to-cheek proportion ({ratios.get('jaw_to_cheek_ratio', 'N/A')})."
        )
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Privacy & Assessment Disclaimer:</b> This report is generated using non-invasive 2D image landmark projection and CIE L*a*b* optical algorithms. Results represent estimated personal beauty consultations and cosmetic suggestions rather than medical, dermatological, or scientifically binding diagnoses.", caption_style))

        # Build PDF using NumberedCanvas
        doc.build(story, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

pdf_report_generator = PDFReportGenerator()
