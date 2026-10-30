from pathlib import Path
from collections import Counter
import csv
import hashlib

from pypdf import PdfReader


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
REPORTS_DIR = PROJECT_ROOT / "reports"

CSV_REPORT = REPORTS_DIR / "document_audit.csv"
TXT_REPORT = REPORTS_DIR / "document_audit_summary.txt"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def calculate_sha256(file_path: Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    digest = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def get_pdf_metadata(metadata, key: str) -> str:
    """Safely extract PDF metadata."""
    if not metadata:
        return ""

    value = metadata.get(key)
    return str(value) if value is not None else ""


# --------------------------------------------------
# PDF AUDIT
# --------------------------------------------------

def audit_pdf(file_path: Path, known_hashes: dict) -> dict:

    relative_path = file_path.relative_to(PROJECT_ROOT)
    relative_document_path = file_path.relative_to(DOCUMENTS_DIR)

    source_folder = (
        relative_document_path.parts[0]
        if len(relative_document_path.parts) > 1
        else "root"
    )

    row = {
        "filename": file_path.name,
        "relative_path": relative_path.as_posix(),
        "source_folder": source_folder,
        "size_mb": round(file_path.stat().st_size / (1024 * 1024), 4),
        "sha256": "",
        "duplicate_of": "",
        "pages": 0,
        "pages_with_text": 0,
        "empty_pages": 0,
        "empty_page_numbers": "",
        "extracted_chars": 0,
        "extracted_words": 0,
        "pdf_title": "",
        "pdf_author": "",
        "pdf_creation_date": "",
        "pdf_modified_date": "",
        "status": "",
        "error_message": "",
    }

    try:
        # Check exact duplicates
        file_hash = calculate_sha256(file_path)
        row["sha256"] = file_hash

        if file_hash in known_hashes:
            row["duplicate_of"] = known_hashes[file_hash]
        else:
            known_hashes[file_hash] = relative_path.as_posix()

        # Read PDF
        reader = PdfReader(str(file_path), strict=False)

        if reader.is_encrypted:
            decrypted = reader.decrypt("")
            if not decrypted:
                raise ValueError("PDF is encrypted and requires a password.")

        row["pages"] = len(reader.pages)

        # Extract PDF metadata
        metadata = reader.metadata

        row["pdf_title"] = get_pdf_metadata(metadata, "/Title")
        row["pdf_author"] = get_pdf_metadata(metadata, "/Author")
        row["pdf_creation_date"] = get_pdf_metadata(metadata, "/CreationDate")
        row["pdf_modified_date"] = get_pdf_metadata(metadata, "/ModDate")

        page_errors = []

                # Extract text page by page
        empty_page_numbers = []

        for page_number, page in enumerate(reader.pages, start=1):

            try:
                text = page.extract_text() or ""
                text = text.strip()

                if text:
                    row["pages_with_text"] += 1
                    row["extracted_chars"] += len(text)
                    row["extracted_words"] += len(text.split())

                else:
                    row["empty_pages"] += 1
                    empty_page_numbers.append(page_number)

            except Exception as exc:
                row["empty_pages"] += 1
                empty_page_numbers.append(page_number)
                page_errors.append(
                    f"Page {page_number}: {str(exc)}"
                )

        # Save empty page numbers
        row["empty_page_numbers"] = ", ".join(
            map(str, empty_page_numbers)
        )

        # Assign status
        if page_errors:
            row["status"] = "partial_error"
            row["error_message"] = " | ".join(page_errors[:3])

        elif row["extracted_chars"] == 0:
            row["status"] = "no_text"

        elif row["empty_pages"] > 0:
            row["status"] = "partial_text"

        else:
            row["status"] = "ok"

    except Exception as exc:
        row["status"] = "error"
        row["error_message"] = str(exc)

    return row


# --------------------------------------------------
# MAIN AUDIT
# --------------------------------------------------

def main():

    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {DOCUMENTS_DIR}"
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(
        DOCUMENTS_DIR.rglob("*.pdf")
    )

    if not pdf_files:
        print("No PDF files found.")
        return

    print(f"Found {len(pdf_files)} PDF documents.")
    print("Starting document audit...\n")

    results = []
    known_hashes = {}

    for index, pdf_file in enumerate(pdf_files, start=1):

        result = audit_pdf(pdf_file, known_hashes)
        results.append(result)

        print(
            f"[{index}/{len(pdf_files)}] "
            f"{result['filename']} -> {result['status']}"
        )

    # --------------------------------------------------
    # EXPORT CSV
    # --------------------------------------------------

    fieldnames = list(results[0].keys())

    with CSV_REPORT.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)

    # --------------------------------------------------
    # GENERATE SUMMARY
    # --------------------------------------------------

    status_counts = Counter(
        row["status"] for row in results
    )

    folder_counts = Counter(
        row["source_folder"] for row in results
    )

    total_pages = sum(row["pages"] for row in results)
    total_chars = sum(row["extracted_chars"] for row in results)
    total_words = sum(row["extracted_words"] for row in results)

    duplicate_count = sum(
        1 for row in results if row["duplicate_of"]
    )

    summary = [
        "IRONSTORE DOCUMENT AUDIT",
        "=" * 40,
        "",
        f"Total PDF documents: {len(results)}",
        f"Total pages: {total_pages}",
        f"Total extracted characters: {total_chars}",
        f"Total extracted words: {total_words}",
        f"Exact duplicates: {duplicate_count}",
        "",
        "DOCUMENT STATUS",
        "-" * 40,
    ]

    for status, count in sorted(status_counts.items()):
        summary.append(f"{status}: {count}")

    summary.extend([
        "",
        "DOCUMENTS BY FOLDER",
        "-" * 40,
    ])

    for folder, count in sorted(folder_counts.items()):
        summary.append(f"{folder}: {count}")

    summary.extend([
        "",
        "DOCUMENTS REQUIRING REVIEW",
        "-" * 40,
    ])

    for row in results:

        if row["status"] != "ok" or row["duplicate_of"]:

            summary.append(
                f"{row['filename']} | "
                f"Status: {row['status']} | "
                f"Duplicate of: {row['duplicate_of']} | "
                f"Error: {row['error_message']}"
            )

    summary.extend([
        "",
        "REPORT FILES",
        "-" * 40,
        str(CSV_REPORT),
        str(TXT_REPORT),
    ])

    TXT_REPORT.write_text(
        "\n".join(summary),
        encoding="utf-8"
    )

    print("\n" + "=" * 40)
    print("AUDIT COMPLETED")
    print("=" * 40)
    print(f"CSV report: {CSV_REPORT}")
    print(f"Summary: {TXT_REPORT}")


if __name__ == "__main__":
    main()
