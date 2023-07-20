import json

with open('./data/orig_bad_code/orig.bad.json') as json_file:
    bad_codes = json.load(json_file)


#with open('./data/orig_good_code/orig.good.json') as json_file:
#    good_codes = json.load(json_file)

for i in bad_codes:
    cs = bad_codes[i]["code_toks_joined"]
    li = list(cs.split(' '))
    if len(li) > 1024:
        print(i, len(cs))



