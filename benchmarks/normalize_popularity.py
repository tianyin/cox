import os

cur_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(cur_dir, 'data/')
output_data_dir = os.path.join(cur_dir, 'output/')

def normalize_popularity(fp, name_functor, value_functor):
    fh = open(fp, 'r')
    res = {}
    for line in fh:
        lns = line.split(',')
        name = name_functor(lns)
        value = value_functor(lns)
        res[name] = value
    return res

def normalize_apache(org_pop_file, norm_pop_file):
    #TODO: we should generate the pop files in this format so we can get rid of these functions
    fp = os.path.join(data_dir, org_pop_file)
    nf = lambda d: d[0]
    vf = lambda d: float(d[1])/100
    res = normalize_popularity(fp, nf, vf)
    fh = open(os.path.join(output_data_dir, norm_pop_file), 'w')
    for k, v in sorted(res.items(), key=lambda d: d[1], reverse=True):
        fh.write(k + ':' + str(v) + '\n')
    fh.close()

#if __name__ == '__main__':
#    normalize_apache()
#    normalize_mysql()
#    normalize_hadoop()
