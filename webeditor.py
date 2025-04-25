import os
import hashlib

CONTENT_DIR = 'content'


def save(page, content):
  filename = os.path.join(CONTENT_DIR, f"{page}.md")
  with open(filename, 'w+') as file:
    # THIS IS A PAIN IN THE FUCKING ASS HELP ME PLEASE COMPARE TEXT...
    file.write(content)


def load(page):
  filename = os.path.join(CONTENT_DIR, f'{page}.md')
  try:
    with open(filename, 'r') as file:
      return file.read()
  except FileNotFoundError:
    return ''


def create(title, content):
  filename = os.path.join(CONTENT_DIR, f'{title}.md')
  with open(filename, 'w') as md_file:
    md_file.write(content)