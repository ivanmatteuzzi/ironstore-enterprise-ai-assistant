from pathlib import Path
import csv

from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_CSV = PROJECT_ROOT / "reports" / "document_audit.csv"


def main():

    with AUDIT_CSV.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        rows = list(csv.DictReader(file))

    problematic_docs = [
        row for row in rows
        if row["status"] == "partial_text"
    ]

    for row in problematic_docs:

        pdf_path = PROJECT_ROOT / row["relative_path"]
        reader = PdfReader(str(pdf_path), strict=False)

        page_numbers = [
            int(number)
            for number in row["empty_page_numbers"].split(",")
            if number.strip()
        ]

        print(f"\nDOCUMENT: {row['filename']}")

        for page_number in page_numbers:

            page = reader.pages[page_number - 1]

            text = (page.extract_text() or "").strip()

            try:
                image_count = len(page.images)
            except Exception:
                image_count = "check failed"

            previous_chars = 0
            next_chars = 0

            if page_number > 1:
                previous_chars = len(
                    (reader.pages[page_number - 2].extract_text() or "").strip()
                )

            if page_number < len(reader.pages):
                next_chars = len(
                    (reader.pages[page_number].extract_text() or "").strip()
                )

            print(
                f" Page {page_number}: "
                f"text_chars={len(text)}, "
                f"images={image_count}, "
                f"previous_page_chars={previous_chars}, "
                f"next_page_chars={next_chars}"
            )


if __name__ == "__main__":
    main()