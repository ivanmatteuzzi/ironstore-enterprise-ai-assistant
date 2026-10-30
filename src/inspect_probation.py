from pathlib import Path
from pypdf import PdfReader
import re

PROJECT_DIR = Path(__file__).resolve().parents[1]

HR_DIR = (
    PROJECT_DIR
    / "documents"
    / "internal_docs_by_area"
    / "HR_policies"
)

TERMS = [
    "probation",
    "probationary",
    "trial period",
    "introductory period",
    "initial employment period",
]

pdf_files = list(HR_DIR.rglob("*.pdf"))

print(f"PDF files scanned: {len(pdf_files)}")

matches_found = 0

for pdf_path in pdf_files:
    reader = PdfReader(str(pdf_path))

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        for term in TERMS:
            pattern = re.escape(term)
            matches = list(re.finditer(pattern, text, re.IGNORECASE))

            for match in matches:
                matches_found += 1

                start = max(0, match.start() - 180)
                end = min(len(text), match.end() + 180)

                snippet = text[start:end].replace("\n", " ")

                print("\n" + "=" * 70)
                print(f"FILE: {pdf_path.name}")
                print(f"PAGE: {page_number}")
                print(f"TERM: {term}")
                print(f"CONTEXT: {snippet}")

if matches_found == 0:
    print("\nNo probation-related terms found in HR documents.")
else:
    print(f"\nTotal matches found: {matches_found}")