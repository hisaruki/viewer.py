#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import tempfile
import argparse
import zipfile
import time
import random
import yaml
import re
import sys
from mimetypes import guess_type
from subprocess import Popen
from pathlib import Path
from base64 import encodebytes
from collections import deque
from PIL import Image
from screeninfo import get_monitors

monitors = get_monitors()
seq = 0
while not len(monitors):
    monitors = get_monitors()
    seq += 1
    if seq > 300:
        sys.stderr.write("can not detect monitors.")
        sys.exit()
for m in monitors:
    window_height = m.height

parser = argparse.ArgumentParser(description="path")
parser.add_argument("path", nargs="*")
parser.add_argument("--order", default=None)
parser.add_argument("--sort", default=None)
parser.add_argument("--maxpage", type=int, default=500)
parser.add_argument("--maxpath", type=int, default=32)
parser.add_argument("--resample", type=int, default=window_height)
parser.add_argument("--reverse", action="store_true")
parser.add_argument("--nocrop", action="store_true")
parser.add_argument("--repeat", type=int, default=None)
args = parser.parse_args()

if args.sort:
    args.order = args.sort

if not sys.stdin.isatty():
    for l in sys.stdin:
        args.path.append(l.strip())

args.path = map(lambda x:x.replace('`', ''), args.path)
args.path = [Path(fp) for fp in args.path]

def res(p):
    if not p.is_absolute():
        p = p.resolve()
    m, e = guess_type(p.name)
    if m and m.find("image") == 0:
        p = p.parent
    if m:
        p = p.resolve()
    return p
args.path = map(res, args.path)

def resample(p, size):
    np = p.parent / Path(p.stem + ".jpg")
    i = Image.open(str(p)).convert('RGB')
    i.thumbnail((size, size), resample=Image.LANCZOS)
    i.save(str(np), quality=97, optimize=True, progressive=True)
    return np

def autocrop(p, threshold=208, giveup=6):
    def is_edge(div):
        result = False
        c = div.getcolors()
        if len(c) > 1:
            result = True
            mi = min([x[0] for x in c])
            ma = max([x[0] for x in c])
            if mi / ma < 0.001:
                result = False
        return result

    try:
        image = Image.open(p)
    except:
        return p
    image = image.convert("L")
    image = image.point(lambda x: 255 if x > threshold else 0)

    for left in range(0, image.size[0]):
        div = image.crop((0, 0, left, image.size[1]))
        if is_edge(div):
            left -= 1
            break
        if left > image.size[0] / giveup:
            break

    for right in range(0, image.size[0]):
        div = image.crop((image.size[0] - right, 0, image.size[0], image.size[1]))
        if is_edge(div):
            right -= 1
            right = image.size[0] - right
            break
        if right > image.size[0] / giveup:
            break

    for top in range(0, image.size[1]):
        div = image.crop((0, 0, image.size[0], top))
        if is_edge(div):
            top -= 1
            break
        if top > image.size[1] / giveup:
            break

    for bottom in range(0, image.size[1]):
        div = image.crop((0, image.size[1] - bottom, image.size[0], image.size[1]))
        if is_edge(div):
            bottom -= 1
            bottom = image.size[1] - bottom
            break
        if bottom > image.size[1] / giveup:
            break

    print(left, right, top, bottom)

    image = Image.open(p)
    image = image.crop((left, top, right, bottom))


    image.save(str(p), quality=100, compress_level=0)
    return p

for fp in deque(args.path, args.maxpath):
    print(fp, fp.exists())
    html = (Path(__file__).resolve().parent / Path("header.html")).read_text()
    html += '\n    <body><article id="main">\n'

    title = fp.stem
    brackets_list = [('\[', '\]'), ('\(', '\)'), ('【', '】'), ('（', '）')]
    brackets_solid = [x[0] for x in brackets_list] + [x[1] for x in brackets_list]
    def replace_brakets(text, brackets):
        b0 = brackets[0]
        b1 = brackets[1]
        m = '{}[^{}{}]*{}'.format(b0, b0, b1, b1)
        m = re.compile(m)
        return re.sub(m, '', text)

    while True in list(map(lambda x:bool(re.search(x, title)), brackets_solid)):
        for brakets in brackets_list:
            title = replace_brakets(title, brakets)
    title = title.strip()
    html += '<title>' + title + '</title>\n'

    def add_script(path, tag='script'):
        html = '<' + tag + '>'
        p = Path(__file__).resolve().parent
        p /= Path(path)
        html += p.read_text()
        html += '</' + tag + '>'
        return html

    def as_data_uri(p):
        m, e = guess_type(p.name)
        bin = p.read_bytes()
        src = 'data:'
        src += m
        src += ';base64,'
        src += encodebytes(bin).decode("utf-8")
        return src

    if fp.exists():
        with tempfile.TemporaryDirectory() as tf:
            files = []
            try:
                conf = Path.home() / Path(".config/viewer.py.yaml")
                conf = yaml.load(conf.read_text())
                td = str(fp.resolve().parent)
                if fp.is_dir():
                    td = str(fp.resolve())
                for cd in conf.keys():
                    if re.search(cd, td):
                        myconf = conf[cd]
                for k, v in myconf.items():
                    if k == "order" and args.order is None:
                        args.order = v
                    if k == "reverse" and args.reverse is False:
                        args.reverse = v
                    if k == "repeat" and args.repeat is None:
                        args.repeat = int(v)
            except Exception as e:
                pass

            if args.order is None:
                args.order = "numeric"
            if args.repeat is None:
                args.repeat = 1

            if zipfile.is_zipfile(str(fp)):
                zf = zipfile.ZipFile(str(fp))
                for i in zf.infolist():
                    if not i.is_dir():
                        with zf.open(i.filename) as mf:
                            bin = mf.read()
                        arcname = i.filename.replace('/', "_")
                        p = Path(tf) / Path(arcname)
                        print(p, len(bin))
                        p.write_bytes(bin)
                files = [p for p in Path(str(tf)).glob("**/*.*")]

            if fp.is_dir():
                for seq, p in enumerate(fp.glob("**/*.*")):
                    if seq >= args.maxpage:
                        break
                    tp = Path(tf) / Path(p.name)
                    tp.write_bytes(p.read_bytes())
                    files.append(tp)


            if args.order == "alphabetical" or 1:
                indexes = []
                for file in files:
                    parts = re.split(r'[_-]', file.name)
                    indexes.append((parts, file))
                for i in range(0, 10):
                    try:
                        indexes = sorted(indexes, key=lambda x: x[0][i])
                    except:
                        pass
                files = [y for x, y in indexes]

            if args.order == "filename":
                files = sorted(files, key=lambda x: x.name)
            if args.order == "path":
                files = sorted(files, key=lambda x: str(x))
            if args.order == "random":
                random.shuffle(files)
            if args.order == "ctime":
                files = sorted(files, key=lambda x: x.stat().st_ctime)
            if args.order == "mtime":
                files = sorted(files, key=lambda x: x.stat().st_mtime)
            if args.order in ["numeric", "rnumeric"]:
                indexes = []
                for file in files:
                    nums = re.split(r'[^0-9]', file.name)
                    nums = list(filter(lambda x:x, nums))
                    nums = list(map(lambda x:int(x), nums))
                    indexes.append((nums, file))
                s, e = 0, 10
                if args.order == "rnumeric":
                    s, e = 10, 0
                for i in range(s, e):
                    try:
                        indexes = sorted(indexes, key=lambda x: x[i * -1])
                    except:
                        pass
                files = [y for x, y in indexes]
            if args.reverse:
                files = sorted(files, reverse=True)

            fc = files
            files = []
            for i in range(0, args.repeat):
                files += fc
            print(len(files), "pages")
            
            for p in deque(files, args.maxpage):
                try:
                    print(p)
                    if guess_type(p.name)[0].split("/")[0] == "image":
                        if args.nocrop is False:
                            p = autocrop(p)
                        if args.resample:
                            p = resample(p, args.resample)

                        #src = p.as_uri()
                        src = as_data_uri(p)
                        img = '\t\t\t<img src=" ' + src + ' ">\n'
                        html += img
                except Exception as e:
                    print(e)

            html += '</article>'
            html += '<article id="sub"></article>'
            html += '<script>'
            html += 'var filename = "' +fp.name+ '";\n'
            html += '</script>'
            html += add_script('sub.css', 'style')
            html += add_script('jquery-3.3.1.slim.min.js')
            html += add_script('script.js')
            html += add_script('autohide_mouse.js')

            html += '</body>'
            html += '</html>'
            url = Path(str(tf)) / Path("index.html")
            url.write_text(html, encoding="utf-8")
            if len(files):
                userdatadir = Path().home() / Path('.config/viewer')
                if not userdatadir.exists(): userdatadir.mkdir(parents=True)
                chrome = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
                if not Path(chrome).exists():
                    chrome = "google-chrome-stable"
                Popen([
                    chrome,
                    '--user-data-dir={}'.format(str(userdatadir)),
                    url.as_uri()
                ])
                time.sleep(3)
