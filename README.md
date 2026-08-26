# 🎓 Web Engineering RAG System

A Retrieval-Augmented Generation (RAG) system for answering questions about the **M.Sc. Web Engineering programme at Technische Universität Chemnitz**.

The system processes the official study regulation and module descriptions, converts them into structured and searchable knowledge, retrieves the most relevant information using semantic similarity, and generates answers using a local Large Language Model.

The application is provided through a lightweight **Gradio** web interface and is designed to be deployable as a **Hugging Face Space**.

---

## 📌 Project Overview

University study regulations contain information distributed across different sections and documents.

For example:

- Admission requirements
- Programme duration
- Study structure
- Compulsory and elective modules
- Module categories
- Credit points
- Part-time study regulations
- Module contents
- Examination requirements
- Master's thesis requirements

A conventional keyword search is often insufficient because users may ask questions using terminology that differs from the wording used in the official documents.

This project therefore uses **Retrieval-Augmented Generation (RAG)**.

Instead of asking an LLM to answer using its general knowledge, the system first retrieves relevant information from the processed university documents and then provides that information to the LLM as context.

The goal is to produce answers that are:

- Grounded in the provided documents
- Traceable to retrieved sources
- Less prone to hallucination
- Useful for natural-language questions
- Easy to deploy and use

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │     Official PDFs        │
                    │                         │
                    │  Study Regulation       │
                    │  Module Descriptions    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     PDF Extraction      │
                    │                         │
                    │      PyMuPDF            │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Zone Detection      │
                    │                         │
                    │  Front Matter           │
                    │  TOC                    │
                    │  Main Regulation        │
                    │  Module Descriptions    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Cleaning          │
                    │                         │
                    │  Remove unwanted PDF    │
                    │  artifacts and blocks   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌─────────────────────┐   ┌────────────────────────┐
        │ Main Regulation     │   │ Module Descriptions    │
        │ Parser              │   │ Parser                 │
        └──────────┬──────────┘   └────────────┬───────────┘
                   │                           │
                   ▼                           ▼
        ┌─────────────────────┐   ┌────────────────────────┐
        │ Normalization       │   │ Normalization          │
        │ + Validation        │   │ + Validation           │
        └──────────┬──────────┘   └────────────┬───────────┘
                   │                           │
                   └────────────┬──────────────┘
                                ▼
                     ┌─────────────────────┐
                     │      Chunking       │
                     │                     │
                     │ Regulation Chunks  │
                     │ Module Chunks      │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    BGE-M3           │
                     │    Embeddings       │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │       FAISS         │
                     │                     │
                     │ Vector Index        │
                     │ + Metadata          │
                     └──────────┬──────────┘
                                │
                       User Question
                                │
                                ▼
                     ┌─────────────────────┐
                     │  Query Embedding    │
                     │      BGE-M3         │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   FAISS Retrieval   │
                     │                     │
                     │      Top-K          │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   Prompt Builder    │
                     │                     │
                     │ Question + Context │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │    Local Qwen LLM   │
                     │                     │
                     │    Generation       │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │      Answer         │
                     │                     │
                     │ + Source References │
                     └──────────┬──────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │      Gradio UI      │
                     │                     │
                     │  Hugging Face Space │
                     └─────────────────────┘
````

---

# 🔄 RAG Pipeline

The application follows the standard Retrieval-Augmented Generation workflow:

```text
User Question
      │
      ▼
BGE-M3 Query Embedding
      │
      ▼
FAISS Similarity Search
      │
      ▼
Top-K Relevant Chunks
      │
      ▼
Prompt Construction
      │
      ▼
Qwen LLM
      │
      ▼
Grounded Answer
      │
      ▼
Retrieved Sources
```

The system currently retrieves:

```text
TOP_K = 5
```

chunks for each query.

---

# 1. 📄 PDF Extraction

The original documents are PDF files.

The project uses **PyMuPDF** to extract structured text from the PDF.

The extraction stage preserves page-level information so that retrieved content can later be associated with its original page.

The extracted data is persisted before further processing.

This creates a reproducible processing pipeline rather than repeatedly parsing the original PDF during development.

---

# 2. 🧭 Zone Detection

The documents contain different logical regions.

The pipeline identifies document zones such as:

* Front matter
* Table of contents
* Main regulation
* Module descriptions
* Study-plan related content

Zone detection prevents unrelated parts of the PDF from being treated as normal regulation content.

---

# 3. 🧹 Cleaning

PDF extraction does not always produce clean logical text.

The cleaning stage processes the extracted blocks and removes or handles unwanted PDF artifacts.

The result is a collection of cleaned blocks that can be passed to the document-specific parsers.

The current pipeline produces approximately:

```text
971 cleaned blocks
```

---

# 4. 📜 Main Regulation Parsing

The main study regulation is parsed into structured regulation paragraphs.

For example:

```text
§ 1  Geltungsbereich
§ 2  Studienbeginn und Regelstudienzeit
§ 3  Zugangsvoraussetzungen
§ 4  Lehr- und Lernformen
§ 5  Ziele des Studienganges
§ 6  Aufbau des Studiums
§ 7  Inhalte des Studiums
§ 8  Studienberatung
§ 9  ...
§ 10 Fern- und Teilzeitstudium
§ 11 Inkrafttreten ...
```

The parser converts unstructured PDF content into structured data.

---

# 5. 📚 Module Description Parsing

Module descriptions are processed separately because their structure differs from the main study regulation.

The pipeline identifies module descriptions and extracts information such as:

* Module number
* Module name
* Category
* Version
* Responsible professorship
* Contents
* Qualification goals
* Examination information
* Credit points

The current dataset contains:

```text
38 module descriptions
```

---

# 6. 🔧 Normalization

After parsing, the extracted structures are normalized into canonical JSON representations.

Normalization provides a stable format for downstream processing.

The normalized datasets are:

```text
normalized_main_regulation.json
normalized_module_descriptions.json
```

---

# 7. ✅ Validation

The project contains several validation stages.

## Main Regulation Validation

Checks the normalized regulation structure.

Current result:

```text
Errors:   0
Warnings: 0

Main regulation validation passed.
```

## Module Validation

The normalized module descriptions are validated for structural consistency.

Current result:

```text
All normalized modules passed validation.
```

## Cross-Document Validation

The regulation and module descriptions are also compared.

This checks relationships such as:

* Modules referenced by §6
* Module descriptions available in the dataset
* Curriculum/module consistency

Some warnings currently exist for module descriptions that are not referenced directly in §6.

These are treated as data-level warnings rather than parser failures.

---

# 8. ✂️ Chunking

The normalized documents are transformed into RAG chunks.

Two major chunk types are created:

### Regulation chunks

These represent parts of the study regulation.

### Module chunks

These represent individual module descriptions.

The current pipeline produces:

```text
Regulation chunks: 16
Module chunks:     38
Total chunks:      54
```

Each chunk contains metadata such as:

```text
chunk_id
chunk_index
document_id
chunk_type
text
context
page_start
page_end
zone
```

Context can include:

```text
part
part_title
paragraph
paragraph_title
section
section_title
module_code
module_name
```

This metadata is important because it allows the application to show users where retrieved information originated.

---

# 9. 🧠 Embeddings

The project uses:

**BAAI/bge-m3**

as the embedding model.

BGE-M3 converts both:

* Document chunks
* User queries

into numerical vectors.

The current embedding dimension is:

```text
1024
```

The embedding process creates semantic representations of the chunks.

For example, a question such as:

```text
Wie lange dauert das Studium?
```

does not need to contain the exact phrase used in the document.

The embedding representation allows the system to identify semantically related content such as:

```text
Studienbeginn und Regelstudienzeit
```

---

# 10. 🔎 FAISS Retrieval

The project uses **FAISS** for vector similarity search.

The index uses:

```text
IndexFlatIP
```

with normalized vectors.

Because the vectors are normalized, inner-product similarity corresponds to cosine similarity.

The FAISS directory contains:

```text
index.faiss
metadata.json
```

### index.faiss

Contains the vector index.

### metadata.json

Contains the metadata associated with each vector.

The ordering between the FAISS vectors and metadata is maintained so that a retrieved vector can be mapped back to its original chunk.

---

# 11. 🔗 Retrieval

When the user asks a question:

```text
Welche Voraussetzungen gelten für die Zulassung?
```

the query is embedded using BGE-M3.

FAISS then searches for the most semantically similar chunks.

For example:

```text
[1] regulation_§ 3
Score: 0.8732

[2] regulation_§ 1
Score: 0.7537

[3] regulation_§ 11
Score: 0.7488
```

The top-K retrieved chunks are passed to the generation stage.

---

# 12. 📝 Prompt Construction

The retrieved chunks are inserted into a controlled prompt.

The system prompt instructs the LLM to:

* Use only retrieved information
* Avoid general model knowledge
* Avoid inventing facts
* Avoid unsupported conclusions
* Preserve important original details
* Provide source references
* Explicitly state when the retrieved information is insufficient

The intended fallback response is:

```text
Dazu enthalten die bereitgestellten Quellen keine ausreichenden Informationen.
```

This is particularly important for a study-regulation assistant because factual accuracy is more important than producing an answer to every question.

---

# 13. 🤖 LLM Generation

The generation component uses a local **Qwen** language model.

The LLM receives:

```text
System Instructions
        +
User Question
        +
Retrieved Context
```

and generates the final response.

The LLM is therefore not responsible for finding the relevant documents.

That task is performed by:

```text
BGE-M3 + FAISS
```

The LLM's primary responsibility is to formulate a natural-language answer from the retrieved evidence.

---

# 14. 📌 Source Grounding

The generated answer uses source references such as:

```text
[Quelle 1]
[Quelle 2]
```

The Gradio application additionally displays the actual retrieved sources below the answer.

For example:

```text
Antwort
────────────────────────

Die Regelstudienzeit beträgt vier Semester.
[Quelle 1]


📚 Quellen

Quelle 1
§ 2 — Studienbeginn und Regelstudienzeit
Seite X

> Der Studiengang hat eine Regelstudienzeit
> von vier Semestern ...
```

This provides a simple form of answer traceability.

---

# 15. 🖥️ Gradio User Interface

The user interface is implemented using **Gradio**.

The UI provides:

* Question input
* Submit button
* Enter-to-submit
* Answer display
* Retrieved source display
* Source metadata
* Page information
* Reset button

The application can be launched locally with:

```bash
python app.py
```

The Gradio server listens on:

```text
0.0.0.0:7860
```

which makes it suitable for containerized and Hugging Face deployment.

---

# 📁 Project Structure

```text
WebEng-RAG-System/
│
├── app.py
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
│
├── src/
│   │
│   ├── config/
│   │   └── settings.py
│   │
│   ├── etl/
│   │   │
│   │   ├── extract/
│   │   │   └── pdf_extractor.py
│   │   │
│   │   ├── parser/
│   │   │   ├── cleaner.py
│   │   │   ├── zone_detector.py
│   │   │   ├── toc/
│   │   │   ├── regulation/
│   │   │   └── module_description/
│   │   │
│   │   ├── persistence/
│   │   │   ├── regulation_writer.py
│   │   │   ├── normalized_main_regulation_writer.py
│   │   │   └── module_description_writer.py
│   │   │
│   │   └── validator/
│   │       └── cross_document_validator.py
│   │
│   ├── chunking/
│   │   ├── regulation_chunker.py
│   │   ├── module_chunker.py
│   │   ├── chunk_writer.py
│   │   └── chunk_validator.py
│   │
│   ├── embedding/
│   │   ├── embedder.py
│   │   └── embedding_writer.py
│   │
│   ├── retrieval/
│   │   ├── faiss_index.py
│   │   ├── retriever.py
│   │   ├── retrieval_models.py
│   │   └── test_retrieval.py
│   │
│   └── generation/
│       ├── llm_client.py
│       ├── prompt_builder.py
│       ├── rag_pipeline.py
│       └── test_rag.py
│
├── data/
│   ├── raw/
│   ├── extracted/
│   ├── metadata/
│   └── processed/
│
└── ...
```

---

# ⚙️ Technology Stack

| Component                | Technology                     |
| ------------------------ | ------------------------------ |
| Programming Language     | Python                         |
| PDF Processing           | PyMuPDF                        |
| Embedding Model          | BAAI/bge-m3                    |
| Embedding Dimension      | 1024                           |
| Vector Database / Search | FAISS                          |
| Generation Model         | Qwen                           |
| RAG Architecture         | Retrieval-Augmented Generation |
| Web Interface            | Gradio                         |
| Deployment Target        | Hugging Face Spaces            |
| Data Format              | JSON / JSONL                   |
| Version Control          | Git / GitHub                   |

---

# 🚀 Running Locally

## 1. Clone the repository

```bash
git clone <repository-url>
cd WebEng-RAG-System
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Prepare the data

Run the ETL pipeline:

```bash
python main.py
```

The pipeline performs:

```text
PDF Extraction
      ↓
Zone Detection
      ↓
TOC Extraction
      ↓
Cleaning
      ↓
Regulation Parsing
      ↓
Module Parsing
      ↓
Normalization
      ↓
Validation
      ↓
Chunking
      ↓
Embedding
```

---

# 🔎 Building the FAISS Index

After generating embeddings, the embeddings are indexed using FAISS.

The resulting directory should contain:

```text
data/
└── processed/
    └── faiss_index/
        ├── index.faiss
        └── metadata.json
```

The application uses this directory for retrieval.

---

# ▶️ Running the Application

Start the Gradio application:

```bash
python app.py
```

The application will start on:

```text
http://localhost:7860
```

---

# 🧪 Testing

The retrieval system can be tested independently:

```bash
python -m src.retrieval.test_retrieval
```

Example questions include:

```text
Welche Voraussetzungen gelten für die Zulassung zum Masterstudiengang Web Engineering?

Wie lange dauert das Studium Web Engineering?

Welche Module gehören zu den Grundlagenmodulen?

Was lernt man im Modul Advanced Management of Data?

Was gilt für ein Teilzeitstudium?
```

The RAG generation pipeline can be tested using:

```bash
python -m src.generation.test_rag
```

---

# ☁️ Hugging Face Deployment

The application is designed to run as a **Hugging Face Space** using Gradio.

The expected deployment structure is approximately:

```text
WebEng-RAG-System/
│
├── app.py
├── requirements.txt
├── README.md
│
├── src/
│
└── data/
    └── processed/
        └── faiss_index/
            ├── index.faiss
            └── metadata.json
```

The large raw/intermediate ETL files do not need to be included in the deployed application if the final FAISS index and required metadata are already generated.

This separates:

```text
Development / ETL
```

from:

```text
Production / Inference
```

The deployed application only needs the artifacts required for retrieval and generation.

---

# 🔐 Data and Git

Raw and intermediate processing data should generally not be committed to Git if they are large or unnecessary for deployment.

For example:

```text
data/raw/
data/extracted/
data/metadata/
```

can be excluded using `.gitignore`.

The final deployment artifacts should be deliberately selected rather than committing every intermediate processing file.

If a file was already committed before being added to `.gitignore`, Git will continue tracking it.

It must first be removed from Git's index:

```bash
git rm -r --cached data/
```

and then committed again.

---

# 🎯 Design Principles

The project follows several important design principles.

## 1. Retrieval before generation

The LLM does not directly answer the question from its pretrained knowledge.

Instead:

```text
Question
   ↓
Retrieval
   ↓
Evidence
   ↓
Generation
```

---

## 2. Structured document processing

Rather than embedding raw PDF text directly, the project first extracts meaningful structures such as:

```text
Paragraphs
Sections
Modules
Module categories
Context
Page information
```

This improves retrieval quality and source traceability.

---

## 3. Metadata preservation

Each chunk retains information about its origin.

This allows the application to answer:

```text
Where did this information come from?
```

rather than returning only an anonymous generated response.

---

## 4. Source-grounded generation

The generation prompt explicitly instructs the model not to invent information that is not supported by the retrieved context.

---

## 5. Validation

The pipeline validates intermediate representations before they are used for chunking and embedding.

This reduces the possibility of silently propagating parsing errors into the RAG system.

---

# ⚠️ Current Limitations

This is a focused RAG system rather than a general-purpose university assistant.

Current limitations include:

### Retrieval

The current system uses a relatively simple:

```text
BGE-M3
+
FAISS IndexFlatIP
```

retrieval approach.

It does not currently include a dedicated reranking model.

---

### Context size

Only the top:

```text
5
```

retrieved chunks are passed to the generation stage.

Some complex questions may require information distributed across more than five chunks.

---

### Citation verification

The LLM is instructed to provide source references, but the current implementation does not independently verify every generated citation against the exact source span.

---

### No conversational memory

Each question is currently handled independently.

The system does not maintain a multi-turn conversation history.

---

### Document versioning

The system currently focuses on the supplied Web Engineering study regulation and module descriptions.

If TU Chemnitz publishes a new version, the ETL and indexing pipeline should be executed again.

---

# 🔮 Possible Future Improvements

Several improvements could be added in future versions.

## Hybrid Retrieval

Combine:

```text
Dense Retrieval
+
BM25 / Keyword Retrieval
```

to improve retrieval for exact module numbers, paragraph numbers and technical terminology.

---

## Reranking

Add a cross-encoder or reranking model:

```text
Query
  ↓
FAISS Top-K
  ↓
Reranker
  ↓
Best Context
  ↓
LLM
```

This could improve retrieval precision.

---

## Better Citation Verification

Instead of trusting the LLM-generated citation numbers, the application could generate citations programmatically from the retrieved chunks.

---

## Conversation History

Support follow-up questions such as:

```text
User:
What is the regular study duration?

Assistant:
Four semesters.

User:
And what about part-time?

Assistant:
...
```

---

## Document Version Management

Support multiple versions of the study regulation:

```text
2025 Regulation
2026 Regulation
Previous Regulation
```

and allow retrieval to be filtered by document version.

---

## Streaming Generation

The Gradio interface could stream generated responses token-by-token for a more responsive user experience.

---

# 📊 Current Pipeline Statistics

The current processed dataset contains approximately:

```text
Cleaned blocks:              971

Main regulation paragraphs:   11

Module descriptions:          38

Regulation chunks:            16

Module chunks:                38

Total chunks:                 54

Embedding dimension:        1024

Embedding model:        BAAI/bge-m3

Vector index:        FAISS IndexFlatIP

Default retrieval K:          5
```

---

# 🧩 Example

### Question

```text
Wie lange dauert das Studium Web Engineering?
```

### Retrieval

The system retrieves the relevant regulation section:

```text
§ 2 — Studienbeginn und Regelstudienzeit
```

which contains information about:

```text
4 semesters / 2 years
```

and:

```text
8 semesters / 4 years for part-time study
```

### Generation

The retrieved information is provided to the Qwen LLM.

### Output

The application generates a natural-language answer and displays the retrieved source below it.

---

# 🏁 Summary

This project implements an end-to-end Retrieval-Augmented Generation system for the Web Engineering Master's programme at TU Chemnitz.

The complete workflow is:

```text
Official Documents
       ↓
PDF Extraction
       ↓
Document Structure Detection
       ↓
Cleaning
       ↓
Parsing
       ↓
Normalization
       ↓
Validation
       ↓
Chunking
       ↓
BGE-M3 Embeddings
       ↓
FAISS Vector Index
       ↓
Semantic Retrieval
       ↓
Prompt Construction
       ↓
Qwen LLM
       ↓
Grounded Answer
       ↓
Source Display
       ↓
Gradio Web Application
       ↓
Hugging Face Space
```

The project demonstrates how unstructured university documents can be transformed into a structured knowledge base and used to build a practical, source-grounded question-answering system.

---

## 👨‍💻 Author

**Sujan Karna**

M.Sc. Web Engineering
Technische Universität Chemnitz

---

## 📄 Disclaimer

This application is an experimental educational project.

For official academic decisions, users should always consult the current official regulations and publications of Technische Universität Chemnitz.

```

