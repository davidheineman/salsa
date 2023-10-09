## LENS-SALSA
This guide is to train the LENS-SALA metric from scratch. For general usage, please see [**the SALSA Readme**](./README.md). Please note the LENS-SALSA training code is built on the [**COMET**](https://github.com/Unbabel/COMET) library. 

### Setup
```sh
# Clone the 
git clone https://github.com/davidheineman/salsa.git

# (Optional) Create Conda env
conda create -n lens-salsa
conda install -n lens-salsa pip
conda activate lens-salsa

# Install dependencies
pip install -r requirements.txt

# Download LENS checkpoint for fine-tuning
mkdir lens-salsa/lens-checkpoint && cd lens-salsa/lens-checkpoint
gdown 179cuRZdJZEtEObovVf_KPhNFWnMF8pkN
unzip LENS-checkpoint

# Preprocess SALSA data for training
mkdir data
```

### Preprocess Data
The following files are used for training:
- `simpeval-regression/[train/valid].csv` - Raw SimpEval scores used to train regression model
- `simpeval-multi-ref/[train/valid].csv` - Grouped references used to train multi-reference metric
- `salsa/[train/valid].csv` - Pre-processed edit-level SALSA ratings (along with their associated SimpEval score) used to train dual-objective word-level predictions

### Training LENS-SALSA
Pre-train LENS-SALSA on SimpEval data:
```sh
python cli/train.py --cfg configs/models/lens_salsa_pretrain.yml
```

Fine-tune LENS-SALSA to predict word-level quality using the Unified Metric (add `--eval` to run evaluation after training):
```sh
python cli/train.py --cfg configs/models/lens_salsa_ft_binary.yaml            # Use {OK, ERROR} objective
python cli/train.py --cfg configs/models/lens_salsa_ft_three_class.yaml       # Use {GOOD, OK, ERROR} objective
python cli/train.py --cfg configs/models/lens_salsa_ft_three_continuous.yaml  # Use [-3, 3] objective
```

Evaluate a trained LENS-SALSA metric:
```sh
# (Optional) For separate validation data: Add --val_data_path [VALIDATION_DATA].csv
python cli/evaluate.py --model_path checkpoints/[YOUR-CHECKPOINT].ckpt --output_file lens-salsa-scores.json
```
