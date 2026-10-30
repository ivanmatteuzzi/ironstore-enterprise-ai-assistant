# How to Run IronStore Enterprise AI Assistant

## 1. Open the project

Open PowerShell in the root directory of the cloned repository.

## 2. Create and activate the virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Configure OpenAI

Create the local environment file:

```powershell
Copy-Item .env.example .env
```

Add your OpenAI API key to `.env`.

## 5. Prepare the knowledge base

The company PDF documents and Chroma database are not included in this public repository.

The authorized PDF documents must be placed in the expected `documents/` directories and the local vector database must be built before running the application.

See the main README for the ingestion and vector database setup instructions.

## 6. Start the application

From the project root, run:

```powershell
.\.venv\Scripts\chainlit.exe run app.py --port 8001
```

## 7. Open the interface

Open your browser and navigate to:

http://localhost:8001

You can now interact with IronStore through the Chainlit chat interface.

Keep the PowerShell terminal open while using the application.