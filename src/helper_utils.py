import textwrap

def word_wrap(text: str, width: int = 80) -> str:
    return "\n".join(textwrap.wrap(text, width=width))
