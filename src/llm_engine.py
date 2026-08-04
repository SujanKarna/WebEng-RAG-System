from groq import Groq
from src.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def generate_answer(query: str, docs: list[str]) -> str:
    context = "\n\n---\n\n".join(docs)
    prompt = f"""
You are an AI assistant that answers questions strictly using the provided context.

The documents you receive may contain hierarchical structures such as:
- Module categories (e.g., Schwerpunktmodule, Vertiefungsmodule, Seminarmodule)
- Submodules
- LP/ECTS allocations
- Numbered lists
- Nested sections

Your rules:
1. Reconstruct the hierarchy exactly as it appears in the context.
2. Never mix categories. Never assume relationships that are not explicitly stated.
3. When counting items, count ONLY items that belong to the same category and appear under the same heading.
4. If the context does not contain enough information to answer, say:
   "The provided documents do not contain enough information to answer this question."
5. Never guess or hallucinate missing module counts.
6. Always cite the document fragments used.
7. Preserve exact module names and LP values.

Output format:
- Answer: clear, grounded, structured.
- Hierarchy: show the relevant parent → child structure.
- Sources: list the document chunks used.


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
