import json
import os
import csv

cur_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(cur_dir, 'data/')
output_data_dir = os.path.join(cur_dir, 'output/')

def normalize(src, output_for_java, rename_file):
    """
    This function normalizes the test cases for benchmarking
    """
    if rename_file:
        rename_map = build_rename_map(rename_file) 
    
    fp = os.path.join(data_dir, src)
    res = {}
    with open(fp, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name = row[0].strip('"')
            s = row[1].replace(',', '\n')
            s = s.replace(';', '\n')
            rs = s.split('\n')
            items = []
            for item in rs:
                item = item.strip()
                if len(item) == 0:
                    continue
                item = item.replace('<', '')
                item = item.replace('>', '')
                if rename_file and item in rename_map:
                    item = rename_map[item]
                items.append(item)
            res[name] = items
     
    #This is the input file of the evaluation
    input_fp = os.path.join(output_data_dir, output_for_java)
    with open(input_fp, 'w') as fh:
        for k, v in res.items():
            fh.write(k + '\n')
   
    #for debugging purpose only
    #json_fp = os.path.join(output_data_dir,output_bm)
    #open(json_fp, 'w').write(json.dumps(res))
    return res

#def normalize_apache():
#    return normalize_general('apache_tc_icon.csv',
#            'n_apache_java_input.txt', 
#            'n_apache_benchmark.csv',
#            #lambda d: d.replace('mod_forensic', 'mod_log_forensic'))
#            lambda d: d)

#def normalize_hadoop():
#    return normalize_general('hadoop_tc_icon.csv',
#            'n_hadoop_java_input.txt',
#            'n_hadoop_benchmark.csv',
#            lambda d: rename_opt_due_to_version(d))

#def normalize_mysql():
#    return normalize_general('mysql_tc_icon.csv',
#            'n_mysql_java_input.txt', 'n_mysql_benchmark.csv',
#            lambda d: d.replace('-', '_'))

def build_rename_maps(rename_file):
    # http://hadoop.apache.org/docs/r2.2.0/hadoop-project-dist/hadoop-common/DeprecatedProperties.html
    """
    Hadoop has a freqent renaming of its configuration parameters,
    so we need to standarize the name in the evaluation.
    This is not need for real usage
    """
    name_fp = os.path.join(data_dir, rename_file) #'hadoop_rename.txt')
    maps = {}
    with open(name_fp, 'r') as fp:
        for line in fp:
            lns = line.replace('\n', '').split('\t')
            maps[lns[0]] = lns[1]
    return maps

class Opt2ModuleMapping:
    """
    In the benchmark, some users are looking for the software module rather than
    a concrete option. So we need to be able to have the mapping information.
    """
    def __init__(self, mapping_file):
        self.opt_to_modules = {}
        self.module_to_opts = {}
        with open(mapping_file, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                opt = row[0].strip().strip("<>")
                mod = row[1].strip()
                self.opt_to_modules[opt]=mod
                if not self.module_to_opts.has_key(mod):
                    self.module_to_opts[mod] = []
                self.module_to_opts[mod].append(opt)

    def get_mod(self, opt_name):
        return self.opt_to_modules[opt_name]

    def get_opts(self, mod_name):
        return self.module_to_opts[mod_name]

    def is_mod(self, name):
        if self.module_to_opts.has_key(name):
            return True
        return False

    def convert_opts_to_modules(self, opts):
        res = []
        for opt in opts:
            if len(opt) == 0:
                continue
            mod = self.get_mod(opt)
            if mod in res:
                continue
            #ignore 'core' module, as they are must be set opts.
            #if mod.find('core') == 0:
            #    continue
            res.append(mod)
        return res
