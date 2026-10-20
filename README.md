# Legal Guidance in the Wild

[Paper (arXiv)](https://arxiv.org/abs/2610.25159) | [Hugging Face paper page](https://huggingface.co/papers/2610.25159) | [Hugging Face collection](https://huggingface.co/collections/AmirMohseni/legal-guidance-in-the-wild)

People ask conversational AI models about their legal rights, obligations, procedures, and personal situations that may have legal consequences. Legally themed chat is not the same as seeking guidance: a conversation may translate a statute, discuss a fictional dispute, or ask for an academic explanation without requesting personalized or practical help.

This repository accompanies **Legal Guidance in the Wild**, a JURIX 2026 paper. We contribute a multi-axis taxonomy of legal queries (whether guidance is sought, how the request is formulated, and which legal domains it concerns), apply it to 2,122 naturally occurring [WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) conversations, and release a human-adjudicated gold set of 200 conversations (84 guidance-positive, 116 guidance-negative).

This repo holds the gold annotations, supplementary artifacts, and code for reproducing the TF-IDF baselines and the gold-set results. Datasets and model checkpoints live on Hugging Face.

## Resources

- [Hugging Face collection](https://huggingface.co/collections/AmirMohseni/legal-guidance-in-the-wild) — datasets, checkpoints, and evaluation artifacts
- [WildChat-Legal-Classification](https://huggingface.co/datasets/AmirMohseni/WildChat-Legal-Classification) — 2,122 silver-labeled conversations (test split = this gold set)
- [WildChat-Legal-Classification-V3-Hierarchical](https://huggingface.co/datasets/AmirMohseni/WildChat-Legal-Classification-V3-Hierarchical) — train / validation split used for model development

## Code

[`notebooks/train_tfidf.ipynb`](notebooks/train_tfidf.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Amir-Mohseni/Legal-Guidance-in-the-Wild/blob/main/notebooks/train_tfidf.ipynb) trains the full-conversation TF-IDF cascade and the prefix TF-IDF guidance model on the silver development data, then scores both on the gold set. It runs on CPU in a few minutes.

[`scripts/evaluate_gold.py`](scripts/evaluate_gold.py) recomputes the gold-set guidance, topic, end-to-end, and McNemar results for all six systems from the frozen predictions in [`supplementary/evaluation/`](supplementary/evaluation):

```bash
pip install -r requirements.txt
python scripts/evaluate_gold.py
```

The ModernBERT checkpoints are on Hugging Face; each model card gives an inference snippet and the frozen guidance threshold.

## Repository contents

| Path | Description |
| --- | --- |
| [`annotations/gold_set.csv`](annotations/gold_set.csv) | Adjudicated gold labels for 200 conversations |
| [`annotations/TAXONOMY_V3.md`](annotations/TAXONOMY_V3.md) | Label taxonomy used for the gold set |
| [`notebooks/train_tfidf.ipynb`](notebooks/train_tfidf.ipynb) | TF-IDF training and gold evaluation |
| [`scripts/evaluate_gold.py`](scripts/evaluate_gold.py) | Gold-set results from the frozen predictions |
| [`supplementary/results.tex`](supplementary/results.tex) | Supplementary results and reliability analyses |
| [`supplementary/training_details.tex`](supplementary/training_details.tex) | Training and model-selection details |
| [`supplementary/generated/`](supplementary/generated) | Tables and figures included by the supplementary TeX |
| [`supplementary/evaluation/`](supplementary/evaluation) | Frozen gold-set evaluation bundle |

The gold set has four columns: `id`, `conversation`, `seeks_legal_guidance`, and `primary_topic`. Topic is filled only when guidance is present.

## Citation

```bibtex
@inproceedings{mohseni2026legal,
  title         = {Legal Guidance in the Wild: How Users Seek Legal Help in Real-World {LLM} Conversations},
  author        = {Mohseni, Amirreza and Spanakis, Gerasimos},
  booktitle     = {Legal Knowledge and Information Systems (JURIX 2026)},
  year          = {2026},
  eprint        = {2610.25159},
  archivePrefix = {arXiv}
}
```

## License

WildChat source conversations are released under [ODC-BY](https://opendatacommons.org/licenses/by/1-0/). The added labels and taxonomy annotations in this repository are [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

## Authors

Amirreza Mohseni and Gerasimos Spanakis, Maastricht University.
