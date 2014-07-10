import os
import json
import csv
import sys
from config import EvalConfig
from evaluator import eval_wrap

if __name__ == '__main__':
    appname  = 'httpd'
    parpath  = '/home/tixu/Cox/data/httpd/parameters'
    poppath  = '/home/tixu/Cox/benchmarks/data/apache_popularity.csv' 
    p2mmaps  = '/home/tixu/Cox/benchmarks/data/apache_modules.csv'
    testcase = '/home/tixu/Cox/benchmarks/data/apache_tc_icon.csv' 
    base_dir = '/home/tixu/Cox/benchmarks/data/' + appname
    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
    eval_wrap(config)
