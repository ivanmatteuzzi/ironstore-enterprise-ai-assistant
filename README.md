# IronStore Enterprise AI Assistant

An AI-powered enterprise assistant designed to help employees retrieve reliable information from internal company policies and product catalogues.

The project uses Retrieval-Augmented Generation (RAG) to ground AI-generated answers in an indexed collection of company documents, providing references to the original PDF files and page numbers.

## 1. Project Overview

IronStore Enterprise AI Assistant provides a single conversational interface for accessing two categories of internal information:

- **Internal documentation:** HR policies, employee handbook, remote work policies, expense procedures and other company documents.
- **Product catalogues:** Product descriptions, SKUs, specifications, features and availability information.

The assistant looks through its internal knowledge base to find the right information and then uses a special language model to create answers that make sense in the conversation.

The application does not perform external web searches.

## 2. Architecture

The application follows a Retrieval-Augmented Generation architecture.

**Document ingestion**
- PDF text extraction using PyPDF.
- Page-level document processing.
- Text cleaning and metadata enrichment.
- Text splitting into chunks.

**Vector database**
- OpenAI embeddings.
- Chroma vector database.
- Local persistence of indexed document chunks.

**Retrieval**
- Multi-Query Retrieval generates alternative search queries.
- When looking for answers, the original question and any alternative versions are searched separately.
- Reciprocal Rank Fusion (RRF) combines and ranks the retrieved results.
- Duplicate passages are removed.
- To generate an answer, the system takes the top eight most relevant passages and uses them to create a response.

**Answer generation**
- OpenAI language model.
- Context-grounded response generation.
- Streaming responses through Chainlit.
- Source references linking answers to document names and PDF pages.
- Instructions to disclose insufficient or missing information rather than inventing facts.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| PDF extraction | PyPDF |
| Text splitting | LangChain Text Splitters |
| Embeddings and LLM | OpenAI API |
| Vector database | Chroma |
| Retrieval orchestration | LangChain |
| User interface | Chainlit |
| Environment configuration | Python dotenv |

## 4. Project Structure

```text
ironstore-enterprise-ai-assistant/
│
├── app.py
├── chainlit.md
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── documents/             # Local PDF documents, not committed
│   ├── internal_docs_by_area/
│   └── product_catalog/
│
├── src/
│   ├── assistant.py
│   ├── audit.py
│   ├── config.py
│   ├── ingestion.py
│   ├── vector_store.py
│   └── __init__.py
│
├── storage/               # Local Chroma database, not committed
│
└── tests/
└── evaluate_retrieval.py
```

You can find more tools to help with diagnosis in the `src/` directory.

## 5. Installation

### Requirements

- Python 3.13
- An OpenAI API key
- You can get to the IronStore PDF documents that you're allowed to see.

### Clone the repository

```bash
git clone https://github.com/ivanmatteuzzi/ironstore-enterprise-ai-assistant.git
cd ironstore-enterprise-ai-assistant
```

### Create a virtual environment

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure environment variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Don't ever add your `.env` file to your project or share your API credentials with anyone.

## 6. Document Ingestion and Vector Database

We don't keep PDF documents in our Git repository on purpose.

Put the right documents in the correct folders inside the `documents/` section.

Run the ingestion process:

```bash
python -m src.ingestion
```

Build the local vector database:

```bash
python -m src.vector_store
```

The Chroma database that we end up with is kept on your computer in a folder called `storage/`.

The database must be built before starting the application.

## 7. Running the Application

Start Chainlit:

```bash
chainlit run app.py --port 8000
```

Open the application in your browser:

```text
http://localhost:8000
```

The assistant supports natural-language questions about internal company policies and product catalogues.

## 8. Retrieval Evaluation

The project starts with a set of tests to see how well it can find what it's looking for - there are 15 different scenarios to check it out.

- 5 HR policy questions.
- 5 product catalogue questions.
- 5 questions involving insufficient or incomplete information.

Run the evaluation:

```bash
python tests/evaluate_retrieval.py
```

### Initial evaluation results

| Metric | Result |
|---|---:|
| Test cases | 15 |
| Successful cases | 15 |
| Case hit rate | 100% |
| Expected sources found | 16/16 |
| Expected source recall | 100% |

These results are based on a test set that was created manually. They check if the right source documents are found, but they don't check if all the answers given are factually correct.

## 9. Source Attribution and Reliability

The assistant gives labels to the documents it finds, so you can tell where the information is coming from.

Answers can refer to these labels, while the interface displays the corresponding PDF filename and page number.

The app also helps narrow down the list of sources to only those that are actually used in the answer it comes up with.

The system is instructed to:
- Use the retrieved document context.
- Avoid inventing company policies or product specifications.
- Identify missing or insufficient information.
- Avoid unsupported claims.
- Respond in the language used by the employee.

Just because a fact has a citation, it doesn't mean the information is actually backed up by the source. In other words, having a citation doesn't automatically guarantee that what's being said is true or supported by the passage it's referencing.

## 10. Security and Data Handling

- To keep your account information safe, we store your API credentials in a file on your computer called `.env`.
- PDF documents are excluded from version control.
- We don't include the local Chroma database in our version control system.
- Audit reports and generated translation files are excluded from version control.
- The only things we plan to share publicly are the project's source code and the documents that go with it.

When you send a document to be processed, it gets sent to OpenAI to help generate answers. Make sure to only use documents that you're allowed to share and follow your organization's rules for handling sensitive information.

## 11. Current Scope and Limitations

This project is a basic version of an educational tool and a working model that shows how something can be done, even if it's not perfect yet.

It does not currently implement:
- Production-grade user authentication and authorization.
- Department-specific document access controls.
- A production deployment environment.
- A completely automatic review of the meaning of given responses.
- An independent semantic verification of every citation.

Further development could introduce hybrid search, reranking, more extensive evaluation and enterprise access controls.

---

**Project:** IronStore Enterprise AI Assistant
**Repository:** https://github.com/ivanmatteuzzi/ironstore-enterprise-ai-assistant
**Purpose:** Educational AI Engineering project.