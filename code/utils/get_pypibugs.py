import json
import logging
import os
from collections import defaultdict
from tempfile import TemporaryDirectory
from typing import Any, Dict
import git
import random
from utils import code_utils
from uuid import UUID
import uuid
from utils import code_error_checker


class PyPiBugsDataVisitor:
    """
    To extract the PyPiBugs dataset, you can use this class as the main scaffold.

    The code automatically, reads in the PyPiBugs dataset definition, clones
    the repos and checkouts out the appropriate commits.

    The `visit_buggy_code` and `visit_fixed_code` need to be implemented:
    * `visit_buggy_code` is called on the version of the code before fixing the bug.
        The full repository and is accessible at the `repo_path` argument.
    * `visit_fixed_code` is called immediately after `visit_buggy_code` and the
        repository is at the version after the bug is fixed.
    """
    def __init__(self):
        self.orig_bad_json = {}
        self.orig_good_json = {}
        self.bifi_dataset_size = 3000

    #@final
    def extract(self, data_path: str) -> None:
        """
        data_path: the path to the PyPiBugs metadata.
        """
        data_per_repo: Dict[str, Any] = defaultdict(list)
        with open(data_path) as f:
            for line in f:
                line = json.loads(line)
                data_per_repo[line["repo"]].append(line)

        for repo_url, data in data_per_repo.items():
            with TemporaryDirectory() as tmp_dir:
                try:
                    logging.info("Cloning %s", repo_url)
                    repo: git.Repo = git.Repo.clone_from(repo_url, tmp_dir)
                    logging.info("Traversing commits in %s", repo_url)
                    # Clone repo

                    for bug_data in data:
                        commit = repo.commit(bug_data["hash"])
                        parents = commit.parents
                        assert len(parents) == 1, "All PyPi bugs should have a single parent"

                        # Checkout
                        parent_commit: git.Commit = parents[0]
                        repo.git.checkout(parent_commit)

                        # Invoke before
                        target_file_path = os.path.join(tmp_dir, bug_data["old_path"])
                        self.visit_buggy_code(tmp_dir, target_file_path, bug_data, commit)

                        # Invoke after
                        repo.git.checkout(commit)
                        for diff in commit.diff(parent_commit):
                            if diff.a_path == bug_data["old_path"]:
                                target_file_path = os.path.join(tmp_dir, diff.b_path)
                                break
                        else:
                            logging.error("Should never reach here. Could not find path of input file")

                        self.visit_fixed_code(tmp_dir, target_file_path, bug_data, commit)
                        self.save_code_for_bifi()
                except:
                    continue

        with open('./data/orig_bad_code/orig.bad.json', 'w') as fp:
            json.dump(self.orig_bad_json, fp, indent=4)
        with open('./data/orig_good_code/orig.good.json', 'w') as fp:
            json.dump(self.orig_good_json, fp, indent=4)    
        

    def get_good_buggy_chunk(self, idx, buggy_code, good_code):
        prev = idx-1
        nex = idx+1
        while True:
            if prev == 0:
                break     
            if buggy_code[prev].strip() == '' or buggy_code[prev][-1] == ':':
                break
            prev -=1
        while True:
            if nex == len(buggy_code):
                break     
            if buggy_code[nex].strip() == '' or buggy_code[nex][-1] == ':':
                break
            nex +=1
        if len(list(' '.join(buggy_code[prev+1:nex]).split(' '))) >= 1024:
            prev, nex = idx-1, idx+1
        buggy_code[prev+1], good_code[prev+1] = buggy_code[prev+1].lstrip(), good_code[prev+1].lstrip()
        return buggy_code[prev+1:nex], good_code[prev+1:nex]

    def visit_buggy_code(
        self, repo_path: str, target_file_path: str, bug_metadata, bug_fixing_commit: git.Commit
    ) -> None:
        """
        Invoked with the repository checked out at the state _before_ the bug-fixing commit.
        """
        with open(target_file_path, 'r') as file:
            file_contents = file.read()
            wf = open('./tmp/buggy.txt', 'w')
            wf.write(file_contents)
            file.close()
            wf.close()
        
    def visit_fixed_code(self, repo_path: str, target_file_path, bug_metadata, bug_fixing_commit: git.Commit) -> None:
        """
        Invoked with the repository checked out at the state _after_ the bug-fixing commit.
        """
        with open(target_file_path, 'r') as file:
            file_contents = file.read()
            wf = open('./tmp/good.txt', 'w')
            wf.write(file_contents)
            file.close()
            wf.close()
    
    def save_code_for_bifi(self):
        # Read code files, identify difference chunks, save as json in bifi
        with open('./tmp/buggy.txt', 'r') as f:
            buggy_code = f.readlines()
        with open('./tmp/good.txt', 'r') as f:
            good_code = f.readlines()
        
        for i in range(len(buggy_code)):
            if buggy_code[i] != good_code[i]:
                buggy_chunk, good_chunk = self.get_good_buggy_chunk(i, buggy_code, good_code)
                
                id = str(uuid.uuid4()).replace('-', '')
                while id in self.orig_bad_json.keys():
                    id = str(uuid.uuid4()).replace('-', '')

                toks_bad_raw, a_dict_bad = code_utils.tokenize_python_code(' '.join(buggy_chunk))
                toks_good_raw, a_dict_good = code_utils.tokenize_python_code(' '.join(good_chunk))
                err_msg = code_error_checker.check_paren_error(toks_bad_raw)
                if not err_msg:
                    err_msg = {'msg': code_error_checker.check_ast_error(' '.join(toks_bad_raw))['msg']}
                self.orig_bad_json[id] = {
                    "code_string": ' '.join(buggy_chunk),
                    "code_toks_joined": ' '.join(toks_bad_raw),
                    "anonymize_dict": a_dict_bad,
                    "err_obj": err_msg
                }
                self.orig_good_json[id] = {
                    "code_string": ' '.join(good_chunk),
                    "code_toks_joined": ' '.join(toks_good_raw),
                    "anonymize_dict": a_dict_good,
                }
                

    def extract_full_file_as_string(self, bug_metadata):
        from git import Repo
        import tempfile
        repo_url = bug_metadata["repo"]
        file_path = bug_metadata["old_path"]
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = Repo.clone_from(repo_url, temp_dir)
            file_contents = repo.git.show(f"HEAD:{file_path}")
            return file_contents             


if __name__ == "__main__":
    import sys
    import time
    
    start = time.time()

    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    extractor = PyPiBugsDataVisitor()
    extractor.extract(sys.argv[1])
    end = time.time()

    print("\n ******Total Time: ", end-start, "******")

