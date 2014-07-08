import os
import json
import csv
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)
sys.path.append(os.path.join(poj_dir, 'python/'))
import cmd_wrapper

httpd_dir= os.path.join(poj_dir, 'data/httpd/')
httpd_index_dir = os.path.join(httpd_dir, 'index/')
if not os.path.exists(httpd_index_dir):
    os.mkdir(httpd_index_dir)



cmd_wrapper.compile()


if __name__ == '__main__':
    query = "return default 443 vhost"
    popularity_file = None
    cmd_wrapper.execute_index(httpd_index_dir, os.path.join(httpd_dir, 'parameters/'), popularity_file)
    tmp_in_fp = os.path.join(cur_dir, 'tmp.input')
    open(tmp_in_fp, 'w').write(query)
    tmp_out_fp = os.path.join(cur_dir, 'tmp.output')
    cmd_wrapper.execute_search(httpd_index_dir, tmp_in_fp, tmp_out_fp, True)
    res = cmd_wrapper.extract_search_outputfile(tmp_out_fp)
    print res
