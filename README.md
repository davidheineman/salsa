# SALSA 💃
Our code for "Dancing Between Success and Failure: Edit-level Simplification Evaluation using SALSA 💃", currently under review. We are still preparing our code for release.

## SALSA Interface
Our interface is built with [**nlproc.tools**](https://nlproc.tools/?t=salsa) and is available at [**salsa-eval.com/interface**](https://salsa-eval.com/interface) with our interactive tutorial at [**salsa-eval.com/tutorial**](https://salsa-eval.com/tutorial). 

Our entire interface is defined in [**interface.yml**](./interface.yml).

## SALSA Dataset
Our dataset is available in [**/data**](./data)

## LENS-SALSA
Fine-tuned LENS 🔎 on SALSA 💃 edit-level evaluation. First, we re-implemented the original multi-reference LENS using the new COMET implementation, then modeled our design on the unified-objective COMET-22 WMT submission (which, in turn was based on the COMETKIWI QE submission).

Our new LENS-SALSA is capable of both reference and referenceless evaluation.

See [**/lens-salsa**](./lens-salsa) for more details and training instructions.

### Setup & Usage
```
cd lens-salsa
pip install -r requirements.txt
```

```
from comet.lens_salsa import LENS_SALSA
lens_salsa = LENS_SALSA('checkpoint/lens-salsa-trained')
score = lens_salsa.score(
    complex=[
        "This is a complex sentence."
    ],
    simple=[
        "This is a simple sentence."
    ]
)
```