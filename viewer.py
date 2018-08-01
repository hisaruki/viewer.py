#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile
import argparse
import zipfile
import time
import webbrowser
import random
import yaml
from mimetypes import guess_type
from pathlib import Path
from base64 import encodestring
from collections import deque


parser = argparse.ArgumentParser(description="path")
parser.add_argument("path")
parser.add_argument("--order", default="page")
parser.add_argument("--maxlen", type=int, default=300)
parser.add_argument("--data", action="store_true")
parser.add_argument("--reverse", action="store_true")
args = parser.parse_args()

fp = Path(args.path).resolve()

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
        try:
            conf = Path.home() / Path(".config/viewer.py.yaml")
            conf = yaml.load(conf.read_text())
            if str(fp.parent) in conf:
                conf = conf[str(fp.parent)]
                for k, v in conf.items():
                    if k == "order":
                        args.order = v
                    if k == "reverse":
                        args.reverse = v
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

        for p in deque(files, args.maxlen):
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
        webbrowser.open(url.as_uri())

        time.sleep(1)
