# exit 0;
################################################################################
# run the following commands one by one in the root directory of the repository
################################################################################
# export PYTHONPATH=.

#Prepare Data
python -m utils.get_pypibugs "./data/pypibugs/pypi-bugs.jsonl"
python scripts/split_orig_bad_and_good.py
python scripts/generate_paired_data_r0.py

#Round0
python -m src.c001__train_fixer --round_name round0 --max_epoch 3 --continue_from "./data/round0/model-fixer/checkpoint_vb.pt"
python -m src.c003__run_fixer   --round_name round0 --checkpoint_name "checkpoint_best.pt"
python -m src.c005__eval_fixer  --round_name round0

#Round1
python -m src.c006__generate_paired_data_from_fixer --round_name round0 --out_round_name round1-FixerOnly
python -m src.c001__train_fixer --round_name round1-FixerOnly --max_epoch 1 --continue_from 'data/round0/model-fixer/checkpoint_best.pt'
python -m src.c003__run_fixer   --round_name round1-FixerOnly --checkpoint_name "checkpoint_best.pt"
python -m src.c005__eval_fixer --round_name round1-FixerOnly
