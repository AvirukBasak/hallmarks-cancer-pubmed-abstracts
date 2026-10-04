#!/usr/bin/env python3
"""Consolidate the Hallmarks of Cancer (HOC) corpus into a single CSV.

One row per article: an ``article`` column (abstract text) plus one binary
(0/1) column per distinct label, named ``top/child/leaf`` with spaces replaced
by ``_``.

Source label format::

    Sustaining proliferative signaling--Growth factors growth promoting signals--Downstream signaling

becomes the column ``sustaining_proliferative_signaling/growth_factors_growth_promoting_signals/downstream_signaling``.

A literal ``/`` in a class name (only ``Glycolysis/Warburg effect``) is
rewritten to ``-or-`` *before* the ``--`` hierarchy separators become ``/``, so
it survives as the single class
``cellular_energetics/glycolysis-or-warburg_effect`` instead of two columns.
"""
import csv
import os

TEXT_PATH = "./data/corpus/cei/txt"
LABEL_PATH = "./data/corpus/cei/class"

name_text_files = sorted(f for f in os.listdir(TEXT_PATH) if f.endswith(".txt"))
name_label_files = sorted(f for f in os.listdir(LABEL_PATH) if f.endswith(".txt"))

assert name_text_files == name_label_files

text_files = [f"{TEXT_PATH}/{f}" for f in name_text_files]
label_files = [f"{LABEL_PATH}/{f}" for f in name_label_files]


def parse_labels(content):
    """Return every label in one class file, plus all its ancestor paths.

    A source label ``x--y--z--`` becomes ``x``, ``x/y`` and ``x/y/z``, so a
    leaf present in an article also marks its parents as present.
    """
    labels = set()
    for slot in content.split("<"):              # one slot per sentence
        slot = slot.strip()
        if not slot:
            continue
        for lab in slot.split("AND"):            # co-occurring labels
            lab = lab.strip().lower().strip("-")  # drop trailing '--'
            if not lab:
                continue
            path = lab.replace("/", "-or-").replace("--", "/").replace(" ", "_")
            parts = path.split("/")
            for i in range(1, len(parts) + 1):    # full path + every ancestor
                labels.add("/".join(parts[:i]))
    return labels


labels_set = set()
texts = []
labels = []  # each entry is the set of labels for one article

for text_file, label_file in zip(text_files, label_files):
    with open(text_file) as f:
        texts.append(f.read().strip())

    with open(label_file) as f:
        article_labels = parse_labels(f.read())

    labels_set.update(article_labels)
    labels.append(article_labels)

all_labels = sorted(labels_set)

with open("hallmarks_cancer.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["article"] + all_labels)
    for text, article_labels in zip(texts, labels):
        writer.writerow([text] + [1 if lab in article_labels else 0
                                  for lab in all_labels])

print("articles:", len(texts))
print("label columns:", len(all_labels))
print("shape:", (len(texts), 1 + len(all_labels)))
