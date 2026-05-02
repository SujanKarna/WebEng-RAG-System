import textwrap

def word_wrap(text: str, width: int = 80) -> str:
    """
    Wraps the input text to the specified width.

    Args:
        text (str): The input text to wrap.
        width (int): The maximum line width. Default is 80.

    Returns:
        str: The wrapped text.
    """
    return "\n".join(textwrap.wrap(text, width=width))
