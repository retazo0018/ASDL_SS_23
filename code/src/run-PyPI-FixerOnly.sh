# exit 0;
################################################################################
# run the following commands one by one in the root directory of the repository
################################################################################
# export PYTHONPATH=.

python -m utils.get_pypibugs "./data/pypibugs/pypi-bugs.jsonl"
python scripts/split_orig_bad_and_good.py
python scripts/generate_paired_data_r0.py

python -m src.c001__train_fixer --round_name round0 --max_epoch 20 --continue_from "./data/round0/model-fixer/checkpoint.pt"
python -m src.c003__run_fixer   --round_name round0 --checkpoint_name "checkpoint20.pt"
python -m src.c005__eval_fixer  --round_name round0
