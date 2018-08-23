#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile
import argparse
import zipfile
import time
import random
import yaml
import re
import sys
from mimetypes import guess_type
from pathlib import Path
from base64 import encodestring
from collections import deque
import webbrowser

parser = argparse.ArgumentParser(description="path")
parser.add_argument("path", nargs="*")
parser.add_argument("--order", default="page")
parser.add_argument("--maxpage", type=int, default=500)
parser.add_argument("--maxpath", type=int, default=32)
parser.add_argument("--data", action="store_true")
parser.add_argument("--reverse", action="store_true")
parser.add_argument("--repeat", type=int, default=1)
args = parser.parse_args()

if not sys.stdin.isatty():
    for l in sys.stdin:
        args.path.append(l.strip())

for fp in deque(args.path, args.maxpath):
    fp = Path(fp).resolve()

    html = (Path(__file__).resolve().parent / Path("header.html")).read_text()
    html += '\n    <body><article id="main">\n'

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
        src += encodestring(bin).decode("utf-8")
        return src

    if fp.exists():
        with tempfile.TemporaryDirectory() as tf:
            files = []
            try:
                conf = Path.home() / Path(".config/viewer.py.yaml")
                conf = yaml.load(conf.read_text())
                for d in conf.keys():
                    if re.search(d, str(fp.resolve().parent)):
                        myconf = conf[d]
                for k, v in myconf.items():
                    if k == "order":
                        args.order = v
                    if k == "reverse":
                        args.reverse = v
                    if k == "repeat":
                        args.repeat = int(v)
            except Exception as e:
                pass

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
                files = [p for p in fp.glob("**/*.*")]

            files = sorted(files, key=lambda x: x.stem.split("_")[0].zfill(5))
            files = sorted(files, key=lambda x: x.stem.split("_")[-1].zfill(5))
            if args.order == "filename":
                files = sorted(files, key=lambda x: x.name)
            if args.order == "path":
                files = sorted(files, key=lambda x: str(x))
            if args.order == "random":
                random.shuffle(files)
            if args.order == "ctime":
                files = sorted(files, key=lambda x: x.stat().st_ctime)
            if args.reverse:
                files = sorted(files, reverse=True)

            fc = files
            files = []
            for i in range(0, args.repeat):
                files += fc
            print(len(files), "pages")

            for p in deque(files, args.maxpage):
                try:
                    if guess_type(p.name)[0].split("/")[0] == "image":
                        src = p.as_uri()
                        if args.data:
                            src = as_data_uri(p)
                        img = '\t\t\t<img src=" ' + src + ' ">\n'
                        html += img
                except Exception as e:
                    print(e)

            html += '</article>'
            html += add_script('jquery-3.3.1.slim.min.js')
            html += add_script('script.js')

            html += '</body>'
            html += '</html>'
            url = Path(str(tf)) / Path("index.html")
            url.write_text(html)
            if len(files):
                webbrowser.open(url.as_uri())
            time.sleep(1)