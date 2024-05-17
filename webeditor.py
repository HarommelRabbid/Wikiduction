import os

CONTENT_DIR = 'content'


def save(page, content):
  filename = os.path.join(CONTENT_DIR, f"{page}.md")
  with open(filename, 'w') as file:
    file.write(content)


def load(page):
  filename = os.path.join(CONTENT_DIR, f'{page}.md')
  try:
    with open(filename, 'r') as file:
      return file.read()
  except FileNotFoundError:
    return None


def create(title, content):
  filename = os.path.join(CONTENT_DIR, f'{title}.md')
  with open(filename, 'w') as md_file:
    md_file.write(content)