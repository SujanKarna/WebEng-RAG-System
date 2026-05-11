# WebEng‑RAG‑System  
A Retrieval‑Augmented Generation system for exploring the **M.Sc. Web Engineering** study regulations at **TU Chemnitz**.

---

## 📘 Overview  
WebEng‑RAG‑System is a lightweight, fast, and modular RAG application that allows students to query the **2015 Web Engineering Study Regulation (AB 31/2015)** using natural language.  
It combines **vector search**, **local embeddings**, and **Groq LLM inference** to deliver context‑grounded answers with source transparency.

This project is still **under active development** and will expand to support newer regulations and additional academic documents.

---

## 🚀 Features  
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-green)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)
![Gradio](https://img.shields.io/badge/UI-Gradio-yellow)
![Status](https://img.shields.io/badge/Status-Prototype-lightgrey)

- Natural‑language question answering  
- Context‑aware responses grounded in regulation text  
- Fast inference using **llama‑3.1‑8b‑instant** (Groq)  
- Transparent retrieval: answer + retrieved chunks  
- Modular architecture for easy extension  
- Clean Gradio interface  

---

## 🧠 Architecture  
- **Embeddings:** SentenceTransformers  
- **Vector Store:** ChromaDB  
- **Retrieval:** Semantic search over chunked regulation text  
- **LLM Backend:** `llama‑3.1‑8b‑instant` via Groq API  
- **Frontend:** Gradio Blocks UI  

---

## 📚 Data Source  
Currently indexed:

- **AB 31/2015 – Study Regulation for M.Sc. Web Engineering**  
  (Official TU Chemnitz publication)

Upcoming additions:
- Module descriptions (Anlage 2)  
- Updated regulations (post‑2015)  

---

## 🛠️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/SujanKarna/WebEng-RAG-System.git
cd WebEng-RAG-System 
'''

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
'''

### 3. Install dependencies

```bash
pip install -r requirements.txt 
'''

### 4. Set your Groq API key

```bash
GROQ_API_KEY = "your_key_here"
'''

### 5. Build the vectorstore

```bash
python -m src.build_vectorstore
'''

### 6. Run the Gradio app

```bash
python -m src.app_gradio
'''

## 🤝 Contributing
Contributions are welcome.
Feel free to open issues, submit pull requests, or suggest improvements.