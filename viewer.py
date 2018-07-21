#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tempfile
import argparse
import zipfile
import time
import webbrowser
from mimetypes import guess_type
from pathlib import Path

parser = argparse.ArgumentParser(description="path")
parser.add_argument("path")
args = parser.parse_args()

fp = Path(args.path).resolve()

html = (Path(__file__).resolve().parent / Path("header.html")).read_text()
html += '\n    <body><article>\n'

if fp.exists():
    with tempfile.TemporaryDirectory() as tf:

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

        files = sorted(files, key=lambda x: x.stem.split("_")[-1].zfill(5))

        for p in files:
            try:
                if guess_type(p.name)[0].split("/")[0] == "image":
                    src = p.as_uri()
                    img = '\t\t\t<img src=" ' + src + ' ">\n'
                    html += img
            except Exception as e:
                pass
        html += '</article>'
        html += '<script>'
        html += (Path(__file__).resolve().parent /
                 Path('jquery-3.3.1.slim.min.js')).read_text()
        html += '</script>'
        html += '<script>'
        html += (Path(__file__).resolve().parent /
                 Path('script.js')).read_text()
        html += '</script>'
        html += '</body>'
        html += '</html>'
        url = Path(str(tf)) / Path("index.html")
        url.write_text(html)
        webbrowser.open(url.as_uri())
        time.sleep(1)
