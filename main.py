# Wikiduction WIP
# Restructuring the structure
import os, sys
import time
from datetime import datetime, timezone
from zoneinfo import *
import random
import re
import json
import sqlite3
import hashlib
import qrcode

from bleach.css_sanitizer import CSSSanitizer
from lupa.lua54 import LuaRuntime

import markdown
import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach_allowlist import *
from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.extensions.smarty import SmartyExtension
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, redirect, render_template, request, url_for, globals, flash, make_response, abort, session
from flask_sqlalchemy import SQLAlchemy
import pygments
import webeditor
import pymysql
#from db import *

# Was planning to use this for Wikiduction extensions in Lua, but it's a hassle for myself, also i'm just lazy :/
lua = LuaRuntime()
lua_dir = "include"
pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.secret_key = 'bwaaaaah'
app.template_folder=os.path.abspath('themes')

# Can't this automatically update without restarting the whole app? i have no idea how to do it
with open("LocalSettings.json", "r") as read_file:
    data = json.load(read_file)

app.config["SQLALCHEMY_DATABASE_URI"] = data["database_uri"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
wikiname = data["name"]
global_tz = data["tz"]
now = datetime.now()
current_time = now.astimezone(ZoneInfo(global_tz)).strftime("%d %B %Y at %H:%M:%S")
defaulttheme = data["default_theme"]
logo = data["logo"]
main_page = data["main_page"]
main_title = data["main_title"]
logs = data["logs"]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route('/')
def main():
  try:
    if data["notice"] != "":
      flash(data["notice"], category="success")
  except Exception:
      pass
  theme = request.cookies.get('theme', defaulttheme)
  tz = request.cookies.get('timezone', global_tz)
  with open(os.path.join('content', f'{main_page}.md'), 'r') as md_file:
    raw = md_file.read()
    if data["rawhtml"]:
          content = raw
    else:
          content = bleach.clean(raw, tags=generally_xss_safe + ["svg", "rect", "text", "video", "audio"],
                                 attributes=print_attrs | {
                                     "*": ["class", "style", "id", "role", "width", "height", "type", "data-bs-target",
                                           "data-bs-slide-to", "fill", "data-bs-slide", "x", "y", "dy", "focusable",
                                           "xmlns"]}, css_sanitizer=CSSSanitizer(all_styles))
    html_content = markdown.markdown(content,
                                     extensions=[
                                         'tables', 'toc', SmartyExtension(smart_angled_quotes=True),
                                         'footnotes', 'fenced_code',
                                         'codehilite', 'abbr', 'admonition', 'sane_lists', 'extra',
                                         WikiLinkExtension(end_url='')
                                     ])
    l1 = os.path.getmtime(os.path.join('content', 'main.md'))
    last_modified = datetime.fromtimestamp(l1).astimezone(ZoneInfo(global_tz)).strftime('%d %B %Y at %H:%M:%S')
    if main_title in ["", "default" , "wikiname"]:
        title = wikiname
    elif main_title in ["page", "pagename", "pagetitle"]:
        title = main_page
    else:
        title = main_title
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
      tz = request.cookies.get('timezone', global_tz)
      raw = md_file.read()
      if data["rawhtml"]:
          content = raw
      else:
          content = bleach.clean(raw, tags=generally_xss_safe + ["svg", "rect", "text", "video", "audio"],
                                 attributes=print_attrs | {
                                     "*": ["class", "style", "id", "role", "width", "height", "type", "data-bs-target",
                                           "data-bs-slide-to", "fill", "data-bs-slide", "x", "y", "dy", "focusable",
                                           "xmlns"]}, css_sanitizer=CSSSanitizer(all_styles))
      html_content = markdown.markdown(content,
                                       extensions=[
                                           'tables', 'toc', SmartyExtension(smart_angled_quotes=True),
                                           'footnotes', 'fenced_code',
                                           'codehilite', 'admonition', 'abbr', 'sane_lists', 'extra',
                                           WikiLinkExtension(end_url='')
                                       ])
      l1 = os.path.getmtime(os.path.join('content', f'{page}.md'))
      last_modified = datetime.fromtimestamp(l1).astimezone(ZoneInfo(global_tz)).strftime('%d %B %Y at %H:%M:%S')
      return render_template(f'{theme}/base.html',
                             content=html_content,
                             title=page,
                             wikiname=wikiname,
                             last_modified=last_modified,
                             logo=logo)
  except FileNotFoundError:
    return abort(404)


@app.route(f'/{main_page}')
def mainname():
  return redirect(url_for('main'))


@app.route('/edit')
def mainname_edit():
  return redirect(url_for('edit_page', page=main_page))


@app.route('/<page>/edit', methods=['GET', 'POST'])
def edit_page(page):
  if request.method == 'POST':
    content = request.form.get('content', '')
    webeditor.save(page, content)
    flash('Edit saved successfully.', category="success")
    rch = open("data/recentchanges.md", 'a')
    rch.write(f"* Edited page '{page}' on {current_time}\n")
    if "edits" in logs:
        print(f"Edited page '{page}' on {current_time}")
    return redirect(url_for('view_page', page=page))
  else:
    if page in ["allpages", "random", "preferences", "create", "edit", "search", "login", "signup", "qrcode"]:
        flash('Invalid page name!', category="error")
        return redirect(url_for('view_page', page=page))
    else:
        theme = request.cookies.get('theme', defaulttheme)
        existing_content = webeditor.load(page)
        return render_template(f'{theme}/editor.html',
                           page=page,
                           content=existing_content,
                           wikiname=wikiname,
                           logo=logo)


def get_all_pages():
  return [os.path.splitext(filename)[0] for filename in os.listdir('content') if filename != main_page+".md"]


@app.route('/allpages', methods=['GET'])
def index():
  theme = request.cookies.get('theme', defaulttheme)
  return render_template(f'{theme}/index.html',
                         pages=get_all_pages(),
                         wikiname=wikiname,
                         logo=logo)


@app.route('/search', methods=['GET'])
def search():
    theme = request.cookies.get('theme', defaulttheme)
    query = request.args.get('query', '')
    query_list = [q for q in get_all_pages() if query in q]
    if query:
        if query in query_list:
            return redirect(url_for('view_page', page=query))
        else:
            return f'''Search placeholder page, query is "{query}"<br><form method="GET" action="?query=">
        <input type="text" id="query" name="query" value="{query}">
        </form>
        Matches:<br>
        {query_list}'''
    else:
        return f'''
        Search placeholder page, enter query: <form method="GET" action="?query=">
        <input type="text" id="query" name="query">
        </form>
        '''


@app.route('/create', methods=['GET', 'POST'])
def create_page():
  theme = request.cookies.get('theme', defaulttheme)
  if request.method == 'POST':
    title = request.form.get('title', '')
    content = request.form.get('content', '')
    if not (title in ["allpages", "random", "preferences", "create", "edit", "search", "login", "signup", "qrcode"] or title in get_all_pages()):
        webeditor.create(title, content)
        flash('Page created successfully.', category="success")
        rch = open("data/recentchanges.md", 'a')
        rch.write(f"Created page '{title}' on {current_time}\n")
        if "creations" in logs:
            print(f"Created page '{title}' on {current_time}")
        return redirect(url_for('view_page', page=title))
    else:
        if not title in get_all_pages():
            flash('Invalid page name!', category="error")
        else:
            flash('Page name already taken!', category="error")
        return redirect(url_for('view_page', page=title))
  else:
    return render_template(f'{theme}/create_page.html',
                           wikiname=wikiname,
                           logo=logo)


def random_page():
  return random.choice([os.path.splitext(filename)[0] for filename in os.listdir('content')])


@app.route("/random")
def random_view():
  page = random_page()
  return redirect(url_for('view_page', page=page))


def get_all_themes():
    themes = os.listdir('themes')
    #theme_name1 = json.load(open(f"templates/{theme}/theme.json")) Non-functional implementation
    #theme_name = theme_name1["name"] There's a better one below
    return themes


def get_all_theme_names():
    themes = next(os.walk('themes'))[1]
    theme_list = []
    theme_list1 = []
    for i in themes:
        try:
            json_f = open(os.path.join('themes', i, 'theme.json'))
        except FileNotFoundError:
            continue
        i1 = json.load(json_f)
        try:
            i1['excluded'] or True == True
        except KeyError:
            theme_list.append(i1['name'])
            theme_list1.append(i)
    return [filename for filename in theme_list], [filename for filename in theme_list1]


hhh = list(available_timezones())


@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
  theme = request.cookies.get('theme', defaulttheme)
  tz = request.cookies.get('timezone', global_tz)
  t1, t2 = get_all_theme_names()
  all_themes = zip(t1, t2)
  if request.method == 'POST':
    theme = request.form.get('theme')
    #tz = request.form.get('time')
    resp = make_response(redirect(url_for('preferences')))
    #resp.set_cookie('timezone', hhh[hhh.index(tz)])
    resp.set_cookie('theme', theme)
    return resp
  return render_template(f'{theme}/prefs.html',
                         logo=logo,
                         wikiname=wikiname,
                         curr_theme=theme,
                         curr_tz=tz,
                         themes=all_themes,
                         timezones=available_timezones())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8080)
