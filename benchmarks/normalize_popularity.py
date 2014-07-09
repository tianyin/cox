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

def normalize_apache():
    fp = os.path.join(data_dir, 'apache_popularity.csv')
    nf = lambda d: d[0]
    vf = lambda d: float(d[1])/100
    res = normalize_popularity(fp, nf, vf)
    fh = open(os.path.join(output_data_dir, 'n_apache_popularity.txt'), 'w')
    for k, v in sorted(res.items(), key=lambda d: d[1], reverse=True):
        fh.write(k + ':' + str(v) + '\n')
    fh.close()

def normalize_mysql():
    fp = os.path.join(data_dir, 'mysql_popularity.csv')
    nf = lambda d: d[0]
    vf = lambda d: float(d[1])/ 100
    res = normalize_popularity(fp, nf, vf)
    fh = open(os.path.join(output_data_dir, 'n_mysql_popularity.txt'), 'w')
    for k, v in sorted(res.items(), key=lambda d: d[1], reverse=True):
        fh.write(k + ':' + str(v) + '\n')
    fh.close()

def normalize_hadoop():
    fp = os.path.join(data_dir, 'hadoop_popularity.csv')
    nf = lambda d : d[0]
    vf = lambda d : float(d[1])
    res = normalize_popularity(fp, nf, vf)
    fh = open(os.path.join(output_data_dir, 'n_hadoop_popularity.txt'), 'w')
    for k, v in sorted(res.items(), key=lambda d: d[1], reverse=True):
        fh.write(k + ':' + str(v) + '\n')
    fh.close()

if __name__ == '__main__':
    normalize_apache()
    normalize_mysql()
    normalize_hadoop()
