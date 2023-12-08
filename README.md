<div align="center">
    <h1>SALSA 💃</h1>

[**SALSA Interface**](https://salsa-eval.com/interface) | [**SALSA Tutorial**](https://salsa-eval.com/tutorial) | [**Download Dataset**](./data) | [**Use LENS-SALSA**](#lens_salsa) | [**Paper**](https://aclanthology.org/2023.emnlp-main.211)
</div>


Our code and data for *Dancing Between Success and Failure: Edit-level Simplification Evaluation using SALSA 💃* to appear at EMNLP 2023.

## SALSA Annotation Interface
Our interface is built with [**thresh.tools**](https://thresh.tools/?t=salsa) and is available at [**salsa-eval.com/interface**](https://salsa-eval.com/interface) with our interactive tutorial at [**salsa-eval.com/tutorial**](https://salsa-eval.com/tutorial). Our interface configuration is defined in [**interface/salsa.yml**](./interface/salsa.yml). The source code for our interactive tutorial is available in [**interface/tutorial**](./interface/tutorial).

## SALSA Dataset
Our dataset 12K edit annotations are available in [**data**](./data), you can use the Thresh library to easily load SALSA data for your project! We also include our train/test/validation splits for training LENS-SALSA in `data/lens-salsa-training` and our data before adjucation (for calculating annotator agreement) in `data/non-adjudicated`.

```sh
pip install thresh
git clone https://github.com/davidheineman/salsa.git
```

```python
from thresh import load_interface, convert_dataset

# Load the SALSA interface
SALSA = load_interface("interface/salsa.yml")

# We can load our JSON data by using our interface object and calling load_annotations()
salsa_data = SALSA.load_annotations("data/salsa.json")

print(salsa_data[0])
```

You may use the SALSA data in its json format, or for a full tutorial on the Thresh data tools, please see [**load_data.ipynb**](https://github.com/davidheineman/thresh/blob/main/notebook_tutorials/load_data.ipynb).

<a id="lens_salsa"></a>

## LENS-SALSA Automatic Evaluation
You may plug-and-play our LENS-SALSA metric (fine-tuned LENS 🔎 on SALSA 💃 edit-level evaluation) for your simplification project! **Our LENS-SALSA metric is capable of both reference and referenceless evaluation.**

We re-implemented the original multi-reference LENS using the new COMET implementation, then modeled our design on the unified-objective COMET-22 WMT submission. See [**lens-salsa**](./lens-salsa) for source code and replicating the training setup.

### Setup & Usage
```sh
pip install lens-metric
```

```python
from lens import download_model, LENS_SALSA

lens_salsa_path = download_model("davidheineman/lens-salsa") # see https://huggingface.co/davidheineman/lens-salsa
lens_salsa = LENS_SALSA(lens_salsa_path)

complex = [
    "They are culturally akin to the coastal peoples of Papua New Guinea."
]
simple = [
    "They are culturally similar to the people of Papua New Guinea."
]

scores, word_level_scores = lens_salsa.score(complex, simple, batch_size=8, devices=[0])
print(scores) # [72.40909337997437]

# LENS-SALSA also returns an error-identification tagging, recover_output() will return the tagged output
tagged_output = lens_salsa.recover_output(word_level_scores, threshold=0.5)
print(tagged_output)

```

## Analysis & Figures
To replicate the analysis tables and figures in our work please refer to [**analysis**](./analysis).

## Cite SALSA
If you find our paper, code or data helpful, please consider citing [**our work**](https://arxiv.org/abs/2305.14458):
```tex
@inproceedings{heineman-etal-2023-dancing,
    title = "Dancing Between Success and Failure: Edit-level Simplification Evaluation using {SALSA}",
    author = "Heineman, David and Dou, Yao and Maddela, Mounica and Xu, Wei",
    editor = "Bouamor, Houda and Pino, Juan and Bali, Kalika",
    booktitle = "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing",
    month = dec,
    year = "2023",
    address = "Singapore",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.emnlp-main.211",
    pages = "3466--3495"
}
```