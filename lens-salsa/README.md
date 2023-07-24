## LENS-SALSA
Please note this library is built on the [**COMET**](https://github.com/Unbabel/COMET) library. 

### Setup
**Data setup:**
Place all data in the `data` directory. The following files are required:
- `simpeval-regression/[train/valid].csv` - Raw SimpEval scores used to train regression model
- `simpeval-multi-ref/[train/valid].csv` - Grouped references used to train multi-reference metric
- `salsa/[train/valid].csv` - Pre-processed edit-level SALSA ratings, along with their associated SimpEval_test score used to train dual-objective

**Download LENS checkpoint:**
```
mkdir checkpoints
cd checkpoints
gdown 179cuRZdJZEtEObovVf_KPhNFWnMF8pkN
```

### Training setups
Fine-tune multi-reference LENS on LENS data:
```
python cli/train.py --cfg ~/nlprx/lens-salsa/configs/models/lens_fine_tuned_multi_ref_model.yml --load_from_checkpoint "checkpoints/lens/epoch=5-step=6102.ckpt"
```

Train LENS from scratch using multi-reference model:
```
python cli/train.py --cfg ~/nlprx/lens-salsa/configs/models/lens_fine_tuned_multi_ref_model.yml
```

Train LENS from scratch using out-of-box regression model (no fancy concatenation or multi-reference training):
```
python cli/train.py --cfg ~/nlprx/lens-salsa/configs/models/lens_regression_model.yml
```

Train LENS-SALSA using the Unified Metric (use `--eval` for running evaluation script after training):
```
python cli/train.py --cfg ~/nlprx/lens-salsa/configs/models/lens_salsa_unified_metric.yaml 
```

Evaluate a trained metric:
```
# Pre-trained
python cli/evaluate.py --model_path ../checkpoints/lens-pretrained-unified/checkpoints/epoch=3-step=22500-val_kendall=0.628.ckpt --val_data_path /nethome/dheineman3/nlprx/lens-salsa/data/salsa/valid.csv --output_file 5-scores-lens-salsa.json 

# Fine-tuned [-3,3]
python cli/evaluate.py --model_path X --output_file 5-scores-lens-salsa.json

# Fine-tuned {GOOD, OK, BAD}
python cli/evaluate.py --model_path ../checkpoints/lens-salsa-testing/model_8/checkpoints/epoch=3-step=1292-val_kendall=0.312.ckpt --output_file 5-scores-lens-salsa.json
```

To replicate the table(s) in the paper:
```
python cli/train.py --eval --cfg ~/nlprx/lens-salsa/configs/models/lens_salsa_unified_metric.yaml 
```

python cli/evaluate.py --model_path ../checkpoints/lens-salsa-testing/model_10/checkpoints/epoch=3-step=1460-val_kendall=0.409.ckpt --val_data_path ../data/salsa/test.csv
