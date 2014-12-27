import os
import json
import csv
import sys

#To import cmd_wrapper. 
#Cox is a java library; here we use the cmd_wrapper to call it in python
cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)
sys.path.append(os.path.join(poj_dir, 'python-wrapper/'))
import cmd_wrapper

#set up the dir
#you can also try out Hadoop using 'dataset/hadoop'
httpd_dir = os.path.join(poj_dir, 'dataset/httpd/')
param_dir = os.path.join(httpd_dir, 'parameters/')
httpd_index_dir = os.path.join(httpd_dir, 'index/')

#cmd_wrapper.compile()

if __name__ == '__main__':
    #assume this is the query for which you want to find related parameters
    #query = "How do I configure the proxy to forward all requests"
    query = "remove the server header from the response"
    """
    Cox works in two stages.
    1. Generates indices based on the manuals (this is a one-time effort)
    2. Navigate the configuration parameters related to the query
    """
    #1. GENERATE THE INDICES
    #we purely rely on the manuals
    if not os.path.exists(httpd_index_dir):
        print 'buiding index at', httpd_index_dir
        os.mkdir(httpd_index_dir)
        popularity_file = None
        #popularity_file = '/home/tixu/Cox/benchmarks/data/hadoop/hadoop_popularity.txt'
        #popularity_file = '/home/tianyin/Cox/benchmarks/dataset/hadoop/hadoop_popularity.txt'
        #first we need to generate the indices
        cmd_wrapper.execute_index(httpd_index_dir, param_dir, popularity_file)
    
    #put input and output
    tmp_in_fp = os.path.join(cur_dir, 'tmp.input')
    open(tmp_in_fp, 'w').write(query)
    tmp_out_fp = os.path.join(cur_dir, 'tmp.output')

    #2. NAVIGATION
    cmd_wrapper.execute_search(httpd_index_dir, tmp_in_fp, tmp_out_fp, None)
    res = cmd_wrapper.extract_search_outputfile(tmp_out_fp)
    print res
