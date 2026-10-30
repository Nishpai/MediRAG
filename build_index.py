"""Download MedlinePlus health topics, split them into chunks and embed them.

Run from the repo root: python build_index.py
"""

import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

import rag

DATA_DIR = Path("data")
XML_PATH = DATA_DIR / "mplus_topics.xml"
CHUNKS_PATH = DATA_DIR / "chunks.json"
EMB_PATH = DATA_DIR / "embeddings.npy"
LIST_URL = "https://medlineplus.gov/xml.html"
MAX_WORDS = 120


def download_xml():
    if XML_PATH.exists():
        print("Using cached", XML_PATH)
        return
    DATA_DIR.mkdir(exist_ok=True)
    page = urllib.request.urlopen(LIST_URL).read().decode("utf-8")
    # The file name has the date in it, so find the newest one on the page
    names = sorted(set(re.findall(r"mplus_topics_\d{4}-\d{2}-\d{2}\.xml", page)))
    url = "https://medlineplus.gov/xml/" + names[-1]
    print("Downloading", url)
    urllib.request.urlretrieve(url, XML_PATH)


def clean_html(text):
    # The summaries are stored as HTML, turn list items and paragraphs into lines
    text = re.sub(r"</(p|li|h3)>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return [line for line in lines if line]


def split_into_chunks(title, lines):
    # Join lines until a chunk reaches about MAX_WORDS words
    chunks = []
    current = []
    count = 0
    for line in lines:
        words = len(line.split())
        if current and count + words > MAX_WORDS:
            chunks.append(" ".join(current))
            current = []
            count = 0
        # List items have no full stop, add one so lines do not run together
        if line[-1] not in ".?!:":
            line = line + "."
        current.append(line)
        count += words
    if current:
        chunks.append(" ".join(current))
    # Put the title in front so each chunk says what it is about
    return [title + ". " + chunk for chunk in chunks]


def parse_topics(xml_path):
    root = ET.parse(xml_path).getroot()
    chunks = []
    topics = 0
    for topic in root.findall("health-topic"):
        if topic.get("language") != "English":
            continue
        title = topic.get("title")
        url = topic.get("url")
        summary = topic.findtext("full-summary") or ""
        lines = clean_html(summary)
        other_names = [a.text for a in topic.findall("also-called")]
        if other_names:
            lines.insert(0, "Also called: " + ", ".join(other_names) + ".")
        topics += 1
        for text in split_into_chunks(title, lines):
            chunks.append({"title": title, "url": url, "text": text})
    return topics, chunks


def main():
    download_xml()
    topics, chunks = parse_topics(XML_PATH)
    print("English topics:", topics, "chunks:", len(chunks))
    CHUNKS_PATH.write_text(json.dumps(chunks, indent=1))

    model = rag.load_model()
    texts = [c["text"] for c in chunks]
    emb = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    np.save(EMB_PATH, emb.astype(np.float32))
    print("Saved", EMB_PATH, emb.shape)


if __name__ == "__main__":
    main()
