from pathlib import Path
import re

from pypdf import PdfReader
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = PROJECT_ROOT / "documents"

# Legacy documents excluded from the active knowledge base
EXCLUDED_FILES = {
    "IronStore_Old_Product_Catalog_2021.pdf"
}


# --------------------------------------------------
# STEP 1 + 2: LOAD AND EXTRACT
# --------------------------------------------------

def clean_text(text: str) -> str:
    """Apply basic text normalization without losing content."""

    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing spaces from individual lines
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def load_pdf_pages(pdf_path: Path) -> list[Document]:
    """Extract text from a PDF, preserving page-level metadata."""

    documents = []

    relative_path = pdf_path.relative_to(DOCUMENTS_DIR)
    path_parts = relative_path.parts

    source_area = path_parts[0]

    # Internal documents have an additional department folder.
    if source_area == "internal_docs_by_area":
        department = (
            path_parts[1] if len(path_parts) > 2 else "General"
        )
        document_type = "internal_document"

    else:
        department = "Product Catalog"
        document_type = "product_catalog"

    try:
        reader = PdfReader(str(pdf_path), strict=False)

        if reader.is_encrypted:
            decrypted = reader.decrypt("")

            if not decrypted:
                raise ValueError("PDF requires a password.")

        for page_number, page in enumerate(reader.pages, start=1):

            raw_text = page.extract_text() or ""
            page_text = clean_text(raw_text)

            # Skip completely empty pages
            if not page_text:
                continue

            document = Document(
                page_content=page_text,
                metadata={
                    "source": relative_path.as_posix(),
                    "filename": pdf_path.name,
                    "document_id": pdf_path.stem,
                    "source_area": source_area,
                    "department": department,
                    "document_type": document_type,
                    "page": page_number,
                }
            )

            documents.append(document)

    except Exception as exc:
        print(f"ERROR reading {pdf_path.name}: {exc}")

    return documents


def load_documents() -> list[Document]:
    """Load all eligible PDF documents from the documents directory."""

    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(
            f"Documents directory not found: {DOCUMENTS_DIR}"
        )

    pdf_files = sorted(DOCUMENTS_DIR.rglob("*.pdf"))

    all_documents = []

    excluded_count = 0
    failed_count = 0

    print(f"Found {len(pdf_files)} PDF files.")

    for pdf_path in pdf_files:

        if pdf_path.name in EXCLUDED_FILES:
            excluded_count += 1
            print(f"SKIPPED (legacy): {pdf_path.name}")
            continue

        page_documents = load_pdf_pages(pdf_path)

        if not page_documents:
            failed_count += 1
            print(f"WARNING: No readable pages in {pdf_path.name}")
            continue

        all_documents.extend(page_documents)

        print(
            f"Loaded: {pdf_path.name} "
            f"({len(page_documents)} pages)"
        )

    print("\n" + "=" * 45)
    print("DOCUMENT LOADING SUMMARY")
    print("=" * 45)

    print(f"PDF files found: {len(pdf_files)}")
    print(f"Legacy documents excluded: {excluded_count}")
    print(f"PDF files without readable pages: {failed_count}")
    print(f"Extracted page documents: {len(all_documents)}")

    return all_documents

# --------------------------------------------------
# STEP 4: CHUNK
# --------------------------------------------------

def split_documents(documents: list[Document]) -> list[Document]:
    """Split page-level documents into smaller chunks."""

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=800,
        chunk_overlap=300,
        add_start_index=True,
    )

    chunks = text_splitter.split_documents(documents)

    print("\n" + "=" * 45)
    print("CHUNKING SUMMARY")
    print("=" * 45)

    print(f"Input pages: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")

    if chunks:
        print("\nFIRST CHUNK:")
        print("Metadata:", chunks[0].metadata)
        print("Text preview:")
        print(chunks[0].page_content[:400])

    return chunks

# --------------------------------------------------
# TEST EXECUTION
# --------------------------------------------------

def main():

    documents = load_documents()

    if not documents:
        print("No documents were extracted.")
        return

    chunks = split_documents(documents)

    print("\nINGESTION PREPARATION COMPLETED")
    print(f"Final chunks: {len(chunks)}")


if __name__ == "__main__":
    main()