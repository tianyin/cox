import os
import json
import csv
import sys

cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)
sys.path.append(os.path.join(poj_dir, 'python/'))
print sys.path

import cmd_wrapper
cmd_wrapper.compile()

if __name__ == '__main__':
    query = "return default 443 vhost"
    # do squery here

