"""Turn a Markdown file into a branded A4 PDF.

Usage: python skills/doc-creator/build_pdf.py <input.md> <output.pdf> [--title "Doc title"]
"""

import argparse
import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_FILE = Path(__file__).with_name("brand.md")
DEFAULTS = {
    "company_name": "",
    "primary_color": "#111111",
    "accent_color": "#888888",
    "text_color": "#222222",
    "logo": "",
    "font_regular": "",
    "font_bold": "",
    "font_heading": "",
    "footer": "",
}


def load_brand():
    brand = dict(DEFAULTS)
    if BRAND_FILE.exists():
        for key, value in re.findall(r"^\s*-\s*(\w+):\s*(.*?)\s*$", BRAND_FILE.read_text(), re.M):
            if value and not value.startswith("<"):
                brand[key] = value.strip("`")
    return brand


def register_fonts(brand):
    regular, bold = "Helvetica", "Helvetica-Bold"
    if brand["font_regular"] and Path(brand["font_regular"]).exists():
        pdfmetrics.registerFont(TTFont("Brand", brand["font_regular"]))
        regular = bold = "Brand"
    if brand["font_bold"] and Path(brand["font_bold"]).exists():
        pdfmetrics.registerFont(TTFont("Brand-Bold", brand["font_bold"]))
        bold = "Brand-Bold"
    if regular == "Brand":
        pdfmetrics.registerFontFamily("Brand", normal=regular, bold=bold, italic=regular, boldItalic=bold)
    heading = bold
    if brand["font_heading"] and Path(brand["font_heading"]).exists():
        pdfmetrics.registerFont(TTFont("Brand-Heading", brand["font_heading"]))
        heading = "Brand-Heading"
    return regular, bold, heading


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*", r"<i>\1</i>", text)
    return re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)


def parse(md, styles, brand):
    story, para, items, rows = [], [], [], []
    list_kind = None

    def flush():
        nonlocal list_kind
        if para:
            story.append(Paragraph(inline(" ".join(para)), styles["body"]))
            para.clear()
        if items:
            story.append(ListFlowable(
                [ListItem(Paragraph(inline(i), styles["body"])) for i in items],
                bulletType="1" if list_kind == "ol" else "bullet", bulletFormat="%s." if list_kind == "ol" else None, leftIndent=12,
                bulletFontName=styles["body"].fontName, bulletFontSize=9,
            ))
            items.clear()
            list_kind = None
        if rows:
            cols = max(len(r) for r in rows)
            cells = [[Paragraph(f"<b>{inline(c)}</b>" if n == 0 else inline(c), styles["body"])
                      for c in r + [""] * (cols - len(r))] for n, r in enumerate(rows)]
            weights = [min(60, max(12, *(len(r[i]) for r in rows if i < len(r)))) for i in range(cols)]
            widths = [(A4[0] - 40 * mm) * w / sum(weights) for w in weights]
            table = Table(cells, colWidths=widths, hAlign="LEFT", repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), HexColor(brand["primary_color"]).clone(alpha=0.12)),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, HexColor(brand["accent_color"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.extend([table, Spacer(1, 4 * mm)])
            rows.clear()

    for line in md.splitlines():
        stripped = line.strip()
        heading = re.match(r"^(#{1,3})\s+(.*)", stripped)
        bullet = re.match(r"^[-*]\s+(.*)", stripped)
        number = re.match(r"^\d+\.\s+(.*)", stripped)
        if heading:
            flush()
            story.append(Paragraph(inline(heading.group(2)), styles[f"h{len(heading.group(1))}"]))
        elif stripped.startswith("|"):
            if para or items:
                flush()
            if not re.fullmatch(r"\|[\s:|-]+\|", stripped):
                rows.append([c.strip() for c in stripped.strip("|").split("|")])
        elif bullet or number:
            if para or rows:
                flush()
            list_kind = "ol" if number else "ul"
            items.append((bullet or number).group(1))
        elif re.fullmatch(r"-{3,}|\*{3,}", stripped):
            flush()
            story.append(HRFlowable(width="100%", color=HexColor(brand["accent_color"]), spaceBefore=6, spaceAfter=6))
        elif not stripped:
            flush()
        else:
            para.append(stripped)
    flush()
    return story


def page_canvas(brand, title, regular, heading):
    class BrandedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pages = []

        def showPage(self):
            self._pages.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            for page in self._pages:
                self.__dict__.update(page)
                self._decorate(len(self._pages))
                super().showPage()
            super().save()

        def _decorate(self, total):
            width, height = A4
            top = height - 18 * mm
            name_x = 20 * mm
            if brand["logo"] and Path(brand["logo"]).exists():
                self.drawImage(brand["logo"], 20 * mm, top - 4 * mm, width=10 * mm, height=10 * mm,
                               preserveAspectRatio=True, mask="auto")
                name_x += 12 * mm
            self.setFont(heading, 14)
            self.setFillColor(HexColor(brand["primary_color"]))
            self.drawString(name_x, top, brand["company_name"])
            self.setFont(regular, 9)
            self.setFillColor(HexColor(brand["text_color"]))
            self.drawRightString(width - 20 * mm, top, title)
            self.setStrokeColor(HexColor(brand["accent_color"]))
            self.line(20 * mm, top - 11 * mm, width - 20 * mm, top - 11 * mm)
            self.line(20 * mm, 18 * mm, width - 20 * mm, 18 * mm)
            self.setFont(regular, 7.5)
            self.drawString(20 * mm, 13 * mm, brand["footer"])
            self.drawRightString(width - 20 * mm, 13 * mm, f"{self._pageNumber} / {total}")

    return BrandedCanvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    brand = load_brand()
    regular, bold, heading = register_fonts(brand)
    text, primary = HexColor(brand["text_color"]), HexColor(brand["primary_color"])
    styles = {
        "body": ParagraphStyle("body", fontName=regular, fontSize=10, leading=14, textColor=text, spaceAfter=6),
        "h1": ParagraphStyle("h1", fontName=heading, fontSize=20, leading=24, textColor=primary, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontName=heading, fontSize=14, leading=18, textColor=primary, spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("h3", fontName=bold, fontSize=11, leading=14, textColor=text, spaceBefore=6, spaceAfter=4),
    }

    md = Path(args.input).read_text()
    title = args.title or next((l[2:] for l in md.splitlines() if l.startswith("# ")), "")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(args.output, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=35 * mm, bottomMargin=25 * mm, title=title)
    doc.build(parse(md, styles, brand), canvasmaker=page_canvas(brand, title, regular, heading))
    print(f"PDF written: {args.output}")


if __name__ == "__main__":
    sys.exit(main())
