import os
import hashlib

CONTENT_DIR = 'content'


def save(page, content):
  filename = os.path.join(CONTENT_DIR, f"{page}.md")
  if hashlib.sha512(load(page).replace('\n', ' ').replace('\r', '').encode(encoding='UTF-8')).digest() != hashlib.sha512(content.replace('\n', ' ').replace('\r', '').encode(encoding='UTF-8')).digest():
    with open(filename, 'w+') as file:
      file.write(content)
      return None
  else:
    return False

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