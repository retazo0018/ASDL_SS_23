from pathlib import Path
import os

ROOT = Path('data')
ROOT.mkdir(exist_ok=True)

code_strings_bad = []
code_ids = []
code_strings_good = []

os.makedirs(str(ROOT/'round0/data_paired'))

for c in range(5):
    with open(str(ROOT/f'orig_bad_code/orig.{c}.bad'), 'r') as f:
        code_strings_bad.extend(f.readlines())
    
    with open(str(ROOT/f'orig_bad_code/orig.{c}.id'), 'r') as f:
        code_ids.extend(f.readlines())
    
for c in range(10):
    with open(str(ROOT/f'orig_good_code/orig.{c}.good'), 'r') as f:
        code_strings_good.extend(f.readlines())

_len = len(code_strings_bad)
dsize = int(_len * 0.2)

with open(str(ROOT/f'round0/data_paired/dev.bad'), 'w') as f:
    f.writelines(code_strings_bad[:dsize])

with open(str(ROOT/f'round0/data_paired/dev.good'), 'w') as f:
    f.writelines(code_strings_good[:dsize])

with open(str(ROOT/f'round0/data_paired/dev.id'), 'w') as f:
    f.writelines(code_ids[:dsize])

with open(str(ROOT/f'round0/data_paired/train.bad'), 'w') as f:
    f.writelines(code_strings_bad[dsize:])

with open(str(ROOT/f'round0/data_paired/train.good'), 'w') as f:
    f.writelines(code_strings_good[dsize:])

with open(str(ROOT/f'round0/data_paired/train.id'), 'w') as f:
    f.writelines(code_ids[:dsize])

