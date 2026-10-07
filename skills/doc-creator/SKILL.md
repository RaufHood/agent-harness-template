---
name: doc-creator
description: Create branded PDF documents — proposals, letters, invoices, reports, one-pagers. Use when the user wants a PDF, a professional document, an offer/proposal, an invoice or a letter in their branding.
---

# Document Creator

## Goal

A clean, branded A4 PDF in `output/`.

## Steps

1. Clarify what's missing: document type, recipient, key content. Ask max 3 questions.
2. Write the content as Markdown in `output/<name>.md`, using the structure below for the type.
3. Build the PDF (first run: create `.venv` if it doesn't exist):
   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r skills/doc-creator/requirements.txt
   .venv/bin/python skills/doc-creator/build_pdf.py output/<name>.md output/<name>.pdf
   ```
   On Windows use `.venv\Scripts\python`.
4. Tell the user the path. Offer one round of changes.

Branding (colors, logo, fonts, footer) and the writing voice come from `skills/doc-creator/brand.md`.
It ships with **Blinkwise** as the example brand; assets live in `skills/doc-creator/assets/`.

The script supports: `#`/`##`/`###` headings, paragraphs, `-` and `1.` lists, tables, `**bold**`, `*italic*`, `---`.

## Structures

**Proposal**
1. Title, client, date
2. Summary (max 5 lines): problem → approach → result
3. Goals (measurable) + what's *not* in scope
4. Approach: phases with deliverables and timeline (table)
5. Price: what's included, payment terms, validity
6. Next steps

**Letter** — date, recipient, subject (bold), salutation, body (max 3 short paragraphs), closing, name.

**Invoice** — invoice number + date, recipient, table (item, qty, unit price, total), subtotal, VAT, total, payment terms, bank details.

**Report / one-pager** — title, key takeaway in 1 sentence, 3-5 sections, next steps.

## Style

- Less text, more structure. Short headings, whitespace.
- Concrete over vague: "3 workshops in 2 weeks", not "support".
- Active voice: "We deliver…", "You get…".
- Deliverables a third party could check.

## Before you finish

- [ ] Can a busy reader get the point in 30 seconds?
- [ ] Numbers, dates and names correct?
- [ ] Nothing invented — mark unknowns as `[TODO]` and tell the user.
