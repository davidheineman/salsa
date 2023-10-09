<div align="center">
    <h1>SALSA 💃</h1>

[**View the SALSA Interface**](https://salsa-eval.com/interface) | [**Tutorial**](https://salsa-eval.com/tutorial) | [**Download Dataset**](./data) | [**Use LENS-SALSA**](#lens_salsa) | [**Paper**](https://arxiv.org/abs/2305.14458)
</div>


Our code and data for *Dancing Between Success and Failure: Edit-level Simplification Evaluation using SALSA 💃* to appear at EMNLP 2023.

## SALSA Annotation Interface
Our interface is built with [**thresh.tools**](https://thresh.tools/?t=salsa) and is available at [**salsa-eval.com/interface**](https://salsa-eval.com/interface) with our interactive tutorial at [**salsa-eval.com/tutorial**](https://salsa-eval.com/tutorial). Our interface configuration is defined in [**./interface/salsa.yml**](./interface/salsa.yml). The source for our interactive tutorial is available in [**/interface/tutorial**](./interface/tutorial).

## SALSA Dataset
Our dataset 12K edit annotations are available in [**/data**](./data), you can use the Thresh library to easily load SALSA data for your project!

```sh
pip install thresh
git clone https://github.com/davidheineman/salsa.git
```

```python
# Load the SALSA interface
SALSA = load_interface("interface/salsa.yml")

# We can load our JSON data by using our interface object and calling load_annotations()
salsa_data = SALSA.load_annotations("data/salsa.json")

print(salsa_data[0])
```

You may use the SALSA data in its json format, or for a full tutorial on the Thresh data tools, please see [**load_data.ipynb**](https://github.com/davidheineman/thresh/blob/main/notebook_tutorials/load_data.ipynb).

## Analysis & Figures
To replicate the analysis tables and figures in our work please refer to [**/analysis/notebooks**](./analysis/notebooks).

<a id="lens_salsa"></a>

## LENS-SALSA Automatic Evaluation
Our fine-tuned LENS 🔎 on SALSA 💃 edit-level evaluation. First, we re-implemented the original multi-reference LENS using the new COMET implementation, then modeled our design on the unified-objective COMET-22 WMT submission. **Our LENS-SALSA metric is capable of both reference and referenceless evaluation.** See [**/lens-salsa**](./lens-salsa) for replicating the training setup.

### Setup & Usage
```sh
pip install lens-metric
```

```python
from lens import download_model
from lens.lens_salsa import LENS_SALSA

model_path = download_model("davidheineman/lens-salsa") # see https://huggingface.co/davidheineman/lens-salsa
lens_salsa = LENS_SALSA(model_path)

score = lens_salsa.score(
    complex = [
        "They are culturally akin to the coastal peoples of Papua New Guinea."
    ],
    simple = [
        "They are culturally similar to the people of Papua New Guinea."
    ]
)
```

## Cite SALSA
If you find our paper, code or data helpful, please consider citing [**our work**](https://arxiv.org/abs/2305.14458):
```tex
@article{heineman2023dancing,
  title={Dancing {B}etween {S}uccess and {F}ailure: {E}dit-level {S}implification {E}valuation using {SALSA}},
  author = "Heineman, David and Dou, Yao and Xu, Wei",
  journal={arXiv preprint arXiv:2305.14458},
  year={2023}
}
```