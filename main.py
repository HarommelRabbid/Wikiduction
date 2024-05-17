# Wikiduction, written by Harommel Rabbid.
# Current Version 0.0.8
import os
import time
from datetime import datetime
import random
import json
import sqlite3

import markdown
import werkzeug.security
from flask import Flask, redirect, render_template, request, url_for, globals, flash, make_response 

import webeditor

with open("LocalSettings.json", "r") as read_file:
    data = json.load(read_file)


app = Flask(__name__)
app.secret_key = 'bwaaaaah'


wikiname = data["name"]
now = datetime.now()
current_time = now.strftime("%H:%M:%S %D-%M-%y")
defaulttheme = data["default_theme"]
logo = data["logo"]


@app.route('/')
def main():
  theme = request.cookies.get('theme', defaulttheme)
  with open(os.path.join('content', 'main.md'), 'r') as md_file:
    content = md_file.read()
    html_content = markdown.markdown(content)
    l1 = os.path.getmtime(os.path.join('content', 'main.md'))
    last_modified = datetime.fromtimestamp(l1).strftime('%Y-%m-%d %H:%M:%S')
    title = wikiname
    return render_template(f'{theme}/base.html',
                           content=html_content,
                           title=title,
                           wikiname=wikiname,
                           last_modified=last_modified,
                           logo=logo)


@app.route('/<page>')
def view_page(page):
  try:
    with open(os.path.join('content', f'{page}.md'), 'r') as md_file:
      theme = request.cookies.get('theme', defaulttheme)
      content = md_file.read()
      html_content = markdown.markdown(content)
      title = page.replace('.md', '')
      l1 = os.path.getmtime(os.path.join('content', f'{page}.md'))
      last_modified = datetime.fromtimestamp(l1).strftime('%Y-%m-%d %H:%M:%S')
      return render_template(f'{theme}/base.html',
                             content=html_content,
                             title=title,
                             wikiname=wikiname,
                             last_modified=last_modified,
                             logo=logo)
  except FileNotFoundError:
    theme = request.cookies.get('theme', defaulttheme)
    return render_template(f"{theme}/404.html", wikiname=wikiname)


@app.route('/<page>/edit', methods=['GET', 'POST'])
def edit_page(page):
  if request.method == 'POST':
    content = request.form.get('content')
    webeditor.save(page, content)
    print(f"Edited page {page} at {current_time}")
    flash('Edit saved successfully.', category="success")
    return redirect(url_for('view_page', page=page, wikiname=wikiname))
  else:
    theme = request.cookies.get('theme', defaulttheme)
    existing_content = webeditor.load(page)
    return render_template(f'{theme}/editor.html',
                           page=page,
                           content=existing_content,
                           wikiname=wikiname,
                           logo=logo)


def get_all_pages():
  markdown_files = os.listdir('content')
  return [os.path.splitext(filename)[0] for filename in markdown_files]


@app.route('/allpages')
def index():
  theme = request.cookies.get('theme', defaulttheme)
  all_pages = get_all_pages()
  return render_template(f'{theme}/index.html',
                         pages=all_pages,
                         wikiname=wikiname,
                         logo=logo)


@app.route('/create', methods=['GET', 'POST'])
def create_page():
  theme = request.cookies.get('theme', defaulttheme)
  if request.method == 'POST':
    title = request.form.get('title')
    content = request.form.get('content')

    # Create a new page using the utility function
    webeditor.create(title, content)
    flash('Page created successfully.', category="success")
    print(f"Created page {title} at {current_time}")
    # Redirect to the newly created page
    return redirect(url_for('view_page', page=title))
  else:
    return render_template(f'{theme}/create_page.html',
                           wikiname=wikiname,
                           logo=logo)


def random_page():
  markdown_files = os.listdir('content')
  pages = [os.path.splitext(filename)[0] for filename in markdown_files]
  pa1 = random.choice(pages)
  return pa1


@app.route("/random")
def random_view():
  page = random_page()
  return redirect(url_for('view_page', page=page))


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
  theme = request.cookies.get('theme', defaulttheme)
  if request.method == 'POST':
        theme = request.form.get('theme')
        resp = make_response(redirect(url_for('preferences')))
        resp.set_cookie('theme', theme)
        return resp
  return render_template(f'{theme}/prefs.html', logo=logo, wikiname=wikiname, theme=theme)


if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
