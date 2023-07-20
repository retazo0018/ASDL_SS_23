# exit 0;
################################################################################
# run the following commands one by one in the root directory of the repository
################################################################################
# export PYTHONPATH=.

#Round1
python -m src.c006__generate_paired_data_from_fixer --round_name round0 --out_round_name round1-FixerOnly
python -m src.c001__train_fixer --round_name round1-FixerOnly --max_epoch 1 --continue_from 'data/round0/model-fixer/checkpoint1.pt'
python -m src.c003__run_fixer   --round_name round1-FixerOnly --checkpoint_name "checkpoint10.pt"
python -m src.c005__eval_fixer --round_name round1-FixerOnly


#Round2
python -m src.c006__generate_paired_data_from_fixer --round_name round1-FixerOnly --out_round_name round2-FixerOnly
python -m src.c001__train_fixer --round_name round2-FixerOnly --max_epoch 5 --continue_from 'data/round1-FixerOnly/model-fixer/checkpoint10.pt'
python -m src.c003__run_fixer   --round_name round2-FixerOnly --checkpoint_name "checkpoint5.pt"
python -m src.c005__eval_fixer  --round_name round2-FixerOnly
