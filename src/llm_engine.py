from groq import Groq
from src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(query: str, docs: list[str]) -> str:
    context = "\n\n---\n\n".join(docs)
    prompt = f"""
You are an assistant for questions about Web Engineering at TU Chemnitz.

Use ONLY the following context to answer the question.

Context:
{context}

Question:
{query}

If the answer is not in the context, say you don't know.
Answer in clear, concise sentences.
"""

    out = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512,
    )

    return out.choices[0].message.content.strip()
