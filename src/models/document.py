

class Document:
    def __init__(self):
        self.parts = []

class Part:
    def __init__(self, title):
        self.title = title
        self.children = []

class Section:
    def __init__(self, title):
        self.title = title
        self.children = []

class Paragraph:
    def __init__(self, text):
        self.text = text

class Table:
    def __init__(self, headers, rows):
        self.headers = headers or []
        self.rows = rows or []