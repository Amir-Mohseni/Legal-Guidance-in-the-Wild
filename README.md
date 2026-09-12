# Legal Guidance in the Wild

People ask conversational AI models about their legal rights, obligations, procedures, and personal situations that may have legal consequences. Legally themed chat is not the same as seeking guidance: a conversation may translate a statute, discuss a fictional dispute, or ask for an academic explanation without requesting personalized or practical help.

This repository accompanies **Legal Guidance in the Wild**, a JURIX 2026 paper. We contribute a multi-axis taxonomy of legal queries (whether guidance is sought, how the request is formulated, and which legal domains it concerns), apply it to 2,122 naturally occurring [WildChat-1M](https://huggingface.co/datasets/allenai/WildChat-1M) conversations, and release a human-adjudicated gold set of 200 conversations (84 guidance-positive, 116 guidance-negative).

This repo holds the gold annotations and supplementary artifacts. Datasets, model checkpoints, and evaluation models live on Hugging Face.

## Resources

- [Hugging Face collection](https://huggingface.co/collections/AmirMohseni/legal-guidance-in-the-wild) — datasets, checkpoints, and evaluation artifacts
- [WildChat-Legal-Classification](https://huggingface.co/datasets/AmirMohseni/WildChat-Legal-Classification) — 2,122 silver-labeled conversations (test split = this gold set)
- [WildChat-Legal-Classification-V3-Hierarchical](https://huggingface.co/datasets/AmirMohseni/WildChat-Legal-Classification-V3-Hierarchical) — train / validation split used for model development

## Repository contents

| Path | Description |
| --- | --- |
| [`annotations/gold_set.csv`](annotations/gold_set.csv) | Adjudicated gold labels for 200 conversations |
| [`annotations/TAXONOMY_V3.md`](annotations/TAXONOMY_V3.md) | Label taxonomy used for the gold set |
| [`supplementary/results.tex`](supplementary/results.tex) | Supplementary results and reliability analyses |
| [`supplementary/training_details.tex`](supplementary/training_details.tex) | Training and model-selection details |
| [`supplementary/generated/`](supplementary/generated) | Tables and figures included by the supplementary TeX |
| [`supplementary/evaluation/`](supplementary/evaluation) | Frozen gold-set evaluation bundle |

The gold set has four columns: `id`, `conversation`, `seeks_legal_guidance`, and `primary_topic`. Topic is filled only when guidance is present.

## License

WildChat source conversations are released under [ODC-BY](https://opendatacommons.org/licenses/by/1-0/). The added labels and taxonomy annotations in this repository are [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

## Authors

Amirreza Mohseni and Gerasimos Spanakis, Maastricht University.
