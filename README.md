# Hallmarks of Cancer — PubMed Abstracts

A CSV consolidation of the *Hallmarks of Cancer (HOC) Corpus*
(see [3. Attribution](#3-attribution)). One row per scientific article.

> ⚠️ NOTE: **Sentence-to-label mapping is discarded.** The original corpus
> annotates labels at the *sentence* level, but this CSV drops that mapping:
> each row is one full abstract, and the label columns are multi-label outputs
> for the whole abstract — a `1` means the label occurs somewhere in the
> abstract, not which sentence carried it.

Label columns are **ancestor-inclusive**: if an abstract is tagged `x/y/z`,
then `x`, `x/y`, and `x/y/z` are all set to `1`.

## 1. What this is

- **1,852** PubMed abstracts, manually annotated by experts against the
  *hallmarks of cancer* taxonomy of Hanahan & Weinberg.
- Each abstract was tagged sentence-by-sentence with a hierarchical label from
  a 10-hallmark taxonomy (37 classes, plus a `null` class — see below). Here the
  sentence-level labels are rolled up into one row per article and stored as
  binary columns.
- Multi-label: an abstract can exhibit several hallmarks at once (median
  3 labels per article; 1,580 of the 1,852 abstracts carry at least one).

## 2. Schema

| column                | meaning                                                            |
| --------------------- | ------------------------------------------------------------------ |
| `article`             | full abstract text                                                 |
| `<hallmark>/<child>/…` | one column per label: `1` if the article has that label, else `0` |

Label columns are named by their path, with spaces replaced by `_`. Examples:

- `sustaining_proliferative_signaling/receptors`
- `genomic_instability_and_mutation/dna_damage/strand_breaks`
- `tumor_promoting_inflammation/inflammation/oxidative_stress`

The abstract text contains commas, quotes, and newlines (one sentence per line),
so the file is RFC-4180 quoted. Parse it with a CSV reader, not a naive
`split(",")`.

### The taxonomy — 10 hallmarks

The top-level columns follow Hanahan & Weinberg, *"Hallmarks of cancer: the
next generation"* (Cell, 2011): ten hallmarks and enabling characteristics,
each with subclasses. The `abstracts` column counts rows where that top-level
label is `1`; counts overlap because labelling is multi-label.

| Top-level column                      | Subclasses                                                              | Abstracts |
| ------------------------------------- | ----------------------------------------------------------------------- | --------: |
| `sustaining_proliferative_signaling`  | `cell_cycle`, `growth_factors_growth_promoting_signals` → `downstream_signaling`, `receptors` | 462 |
| `resisting_cell_death`                | `apoptosis`, `autophagy`, `necrosis`                                    | 429 |
| `genomic_instability_and_mutation`    | `dna_damage` → `adducts`, `strand_breaks`; `dna_repair_mechanisms`, `mutation` | 333 |
| `activating_invasion_and_metastasis`  | `invasion`, `metastasis`                                                | 291 |
| `evading_growth_suppressors`          | `by_deregulating_cell_cycle_checkpoints` → `cell_cycle`, `by_evading_contact_inhibition` | 240 |
| `tumor_promoting_inflammation`        | `immune_response`, `inflammation` → `oxidative_stress`                  | 240 |
| `inducing_angiogenesis`               | `by_deregulating_angiogenesis` → `angiogenic_factors`                   | 143 |
| `enabling_replicative_immortality`    | `immortalization`, `senescence`                                         | 115 |
| `avoiding_immune_destruction`         | `immune_response`, `immunosuppression`                                  | 108 |
| `cellular_energetics`                 | `glycolysis-or-warburg_effect`                                          | 105 |

### The `null` column

`null` is one of the top-level columns. In the source annotations it is an
explicit `NULL` label applied to a sentence that exhibits no hallmark of
cancer. In this CSV it is a per-article binary column: `1` means at least one
sentence in the abstract was explicitly marked `NULL`. Only 11 abstracts have
`null = 1`; 270 abstracts carry no label at all (every label column, `null`
included, is `0`).

### Class-name normalization

The source class *"Glycolysis/Warburg effect"* contains a literal `/` that is
part of the name, not a hierarchy separator. To keep the `/`-path convention
unambiguous, that `/` is rewritten to `-or-`, so the class appears as the single
column `cellular_energetics/glycolysis-or-warburg_effect` (98 abstracts) rather
than two columns.

### Conversion from the source format

The source encodes one label per sentence as a `--`-separated path ending in a
trailing `--`, with co-occurring labels joined by ` AND `, and one `<`-delimited
slot per sentence:

```
<Activating invasion and metastasis--Metastasis ANDInducing angiogenesis--By deregulating angiogenesis--Angiogenic factors< <
```

We convert it because nested `--` + `AND` delimiters are hard to read and
parse. Each `AND`-joined label becomes its own column, and:

- the `<`-delimited sentence slots are flattened into the article
- the trailing `--` (a root artifact) is dropped
- a literal `/` in a class name → `-or-` (only *"Glycolysis/Warburg effect"*)
- `--` → `/`
- spaces → `_`
- text is lowercased

## 3. Attribution

This is a reformatting of the *Hallmarks of Cancer (HOC) Corpus*:

> Baker, Simon; Silins, Ilona; Guo, Yufan; Ali, Imran; Högberg, Johan;
> Stenius, Ulla; Korhonen, Anna (2016). *Automatic semantic classification of
> scientific literature according to the hallmarks of cancer*. Bioinformatics
> 32(3): 432–440. https://doi.org/10.1093/bioinformatics/btv585

Corpus: https://github.com/sb895/Hallmarks-of-Cancer
License: GNU General Public License v3.0 (GPL-3.0) — see `data/LICENSE`.

The taxonomy derives from:

> Hanahan, Douglas; Weinberg, Robert A. (2011). *Hallmarks of cancer: the next
> generation*. Cell 144(5): 646–674. https://doi.org/10.1016/j.cell.2011.02.013

> Hanahan, Douglas; Weinberg, Robert A. (2000). *The hallmarks of cancer*. Cell
> 100(1): 57–70. https://doi.org/10.1016/S0092-8674(00)81683-9

A follow-up paper builds a tool on top of this corpus:

> Baker, Simon; Ali, Imran; Silins, Ilona; Pyysalo, Sampo; Guo, Yufan;
> Högberg, Johan; Stenius, Ulla; Korhonen, Anna (2017). *Cancer Hallmarks
> Analytics Tool (CHAT): a text mining approach to organize and evaluate
> scientific literature on cancer*. Bioinformatics 33(24): 3973–3981.

Changes: label strings reformatted to `/`-paths with `_` for spaces, and the
sentence-level labels consolidated into per-article binary columns.

## Extras

- `hallmarks_cancer.csv`: the consolidated dataset (this file).
- `consolidate.py`: rebuilds `hallmarks_cancer.csv` from
  `data/corpus/cei/{class,txt}/*.txt`.
- `taxonomy.json`: the label forest, precomputed from the gold labels.
- `taxonomy_preprocess.py`: rebuilds `taxonomy.json` from `data/corpus/cei/class/*.txt`.
- `taxonomy_viewer.py`: interactive Streamlit browser (one tree per tab, zoomable).

Usage (consolidate → preprocess → json → viewer):

```bash
python consolidate.py           # rebuild the CSV from the raw corpus
python taxonomy_preprocess.py   # rebuild taxonomy.json
streamlit run taxonomy_viewer.py
```

`consolidate.py`, `taxonomy_preprocess.py`, and `taxonomy_viewer.py` were
generated by AI (Claude Code).
