import os
import json
import csv
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
poj_dir = os.path.dirname(cur_dir)
data_dir = os.path.join(cur_dir, 'data/')
output_data_dir = os.path.join(cur_dir, 'output/')
if not os.path.exists(output_data_dir):
    os.mkdir(output_data_dir)
sys.path.append(os.path.join(poj_dir, 'python-wrapper/'))
import cmd_wrapper
import normalize_cases
import normalize_popularity

do_compile = True
do_popularity = True
do_normal = True
base_path = os.path.join(poj_dir, 'data/')
if do_compile:
    cmd_wrapper.compile()


class ApacheEval:
    index_path = os.path.join(base_path, 'httpd/index/')
    dst_dir = os.path.join(base_path, 'httpd/parameters/')
    input_file = os.path.join(output_data_dir, 'n_apache_java_input.txt')
    output_file = os.path.join(output_data_dir, 'n_apache_java_output.txt')
    index_path_with_popularity = os.path.join(base_path, 'httpd/index_with_popularity/')
    output_file_with_popularity = output_file + '.with_popularity'
    popularity_file = os.path.join(output_data_dir, 'n_apache_popularity.txt')
    modules = normalize_cases.ApacheModules(os.path.join(data_dir, 'apache_modules.csv'))
    std_res = staticmethod(lambda : normalize_cases.normalize_apache())
    std_pop = staticmethod(lambda : normalize_popularity.normalize_apache())
    rename_opt = lambda n : n
    name = 'apache'

class HadoopEval:
    index_path = os.path.join(base_path, 'index/hadoop/')
    dst_dir = os.path.join(base_path, 'raw/hadoop/')
    input_file = os.path.join(data_dir, 'n_hadoop_java_input.txt')
    output_file = os.path.join(data_dir, 'n_hadoop_java_output.txt')
    index_path_with_popularity = os.path.join(base_path, 'index_with_popularity/hadoop/')
    output_file_with_popularity = output_file + '.with_popularity'
    popularity_file = os.path.join(data_dir, 'n_hadoop_popularity.txt')
    modules = None
    std_res = staticmethod(lambda : normalize_cases.normalize_hadoop())
    std_pop = staticmethod(lambda : normalize_popularity.normalize_hadoop())
    rename_opt = lambda n : rename_opt_due_to_version(n)
    name = 'hadoop'

class MysqlEval:
    index_path = os.path.join(base_path, 'index/mysql/')
    dst_dir = os.path.join(base_path, 'raw/mysql/')
    input_file = os.path.join(data_dir, 'n_mysql_java_input.txt')
    output_file = os.path.join(data_dir, 'n_mysql_java_output.txt')
    index_path_with_popularity = os.path.join(base_path, 'index_with_popularity/mysql/')
    output_file_with_popularity = output_file + '.with_popularity'
    popularity_file = os.path.join(data_dir, 'n_mysql_popularity.txt')
    modules = None
    std_res = staticmethod(lambda : normalize_cases.normalize_mysql())
    std_pop = staticmethod(lambda : normalize_popularity.normalize_mysql())
    rename_opt = lambda n : n
    name = 'mysql'


def eval(config):
    if not os.path.exists(config.index_path):
        os.mkdir(config.index_path)

    if not os.path.exists(config.index_path_with_popularity):
        os.mkdir(config.index_path_with_popularity)

    if do_normal:
        cmd_wrapper.execute_index(config.index_path,
                config.dst_dir,
                None)
        res = cmd_wrapper.execute_search(config.index_path,
                config.input_file,
                config.output_file, False)
        #for (k, v) in res.items():
        #    print str(k) + ' : ' + str(v)

    if do_popularity:
        if not os.path.exists(config.popularity_file):
            config.std_pop()
        cmd_wrapper.execute_index(config.index_path_with_popularity,
                config.dst_dir,
                config.popularity_file)
        res = cmd_wrapper.execute_search(config.index_path_with_popularity,
                config.input_file,
                config.output_file_with_popularity, True)
        #for (k, v) in res.items():
        #    print str(k) + ' : ' + str(v)

def generate_result_comp_report(std_res, eval_res, modules):

    res = {'total':0, 'can-help': 0, 'ratio %': 0}
    d = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
    import cStringIO
    r = cStringIO.StringIO()
    detail = cStringIO.StringIO()
    total_match = 0
    partial_match = 0
    no_match = 0
    for q, vs in std_res.items():
        hit = 0
        hit_index = sys.maxint
        for v in vs:
            v = v.lower()
            if modules is not None and modules.is_mod(v):
                mods = modules.convert_opts_to_modules(eval_res[q])
                ts = mods
            else:
                ts = [x.lower() for x in eval_res[q]]
            if v in ts:
                index = ts.index(v)
                hit_index = min(hit_index, index)
                if index <5: #only check top 5 search results
                    hit += 1
                detail.write('"' + str(q) + '"' + '\t' + str(index) + '\t' + v + '\t' + str(ts) + '\n')
            else:
                hit_index = min(hit_index, sys.maxint)
                detail.write('"' + str(q) + '"\t' + 'NotFound\t' + v + '\t' + str(ts) + '\n')

        if hit_index is sys.maxint:
            hit_index = -1
        if hit_index > 5:
            hit_index = 5
        hit_index += 1
        d[hit_index] += 1
        if hit_index <6 and hit_index != 0:
            res['can-help'] += 1
        if hit == 0:
            no_match += 1
        elif hit < len(vs):
            partial_match += 1
        else:
            total_match += 1

    res['total'] = len(std_res)
    res['ratio'] = round(100.0*res['can-help'] / res['total'], 2)
    #res['detail'] = {x[0]: round(100.0 * x[1]/res['total'], 1) for x in d.items()}
    res['detail'] = {x[0] : x[1] for x in d.items()}

    r.write('we have ' + str(len(std_res)) + ' test cases!\n')
    r.write(str(total_match) + ' (' + str(round(100.0 * total_match / len(std_res), 2)) + '%) for total match!\n')
    r.write(str(partial_match) + ' (' + str(round(100.0 * partial_match / len(std_res), 2)) + '%) for partial match!\n')
    r.write(str(no_match) + ' (' + str(round(100.0 * no_match / len(std_res), 2)) + '%) for no match!\n')
    s = r.getvalue()
    d = detail.getvalue()
    detail.close()
    r.close()
    return {'brief': s, 'detail': d, 'structure': json.dumps(res)}


def compare_result(config):
    #standard result
    std_res = config.std_res()
    if do_normal:
        nml_res = cmd_wrapper.extract_search_outputfile(config.output_file)
        print '*********Normal Search Results:'
        s = generate_result_comp_report(std_res, nml_res, None)
        print s['brief']
        open(os.path.join(output_data_dir, 'r_' + config.name + 'nml_res.txt'), 'w').write(s['detail'])
        open(os.path.join(output_data_dir, 'res_nml_' + config.name + '.json'), 'w').write(s['structure'])

    if do_popularity:
        pop_res = cmd_wrapper.extract_search_outputfile(config.output_file_with_popularity )
        print '**********Popularity Search Results:'
        s = generate_result_comp_report(std_res, pop_res, config.modules)
        print s['brief']
        open(os.path.join(output_data_dir, 'r_' + config.name + 'pop_res.txt'), 'w').write(s['detail'])
        open(os.path.join(output_data_dir, 'res_pop_' + config.name + '.json'), 'w').write(s['structure'])


    pass

def eval_wrap(config):
    print '\n~~~~~~~~~~~~~~~~~~evaluating ' + config.name + '   start ~~~~~~'
    config.std_res()
    eval(config)
    compare_result(config)
    print '~~~~~~~~~~~~~~evaluating ' + config.name + '   end ~~~~~~'


def collect_results_and_dump_to_csv():
    rfs = [ApacheEval, HadoopEval, MysqlEval]
    overall_res = [('software-name', 'total', 'nml-can-help', 'nml-can-help-ratio', 'pop-can-help', 'pop-can-help-ration')]
    nml_overall = [('software-name', 'number of hit')]
    pop_overall = [('software-name', 'number of hit')]

    for cfg in rfs:
        nml_res_fp = os.path.join(data_dir, 'res_nml_' + cfg.name + '.json')
        nml_res = json.loads(open(nml_res_fp, 'r').read())
        pop_res_fp = os.path.join(data_dir, 'res_pop_' + cfg.name + '.json')
        pop_res = json.loads(open(pop_res_fp, 'r').read())
        overall_res.append((cfg.name, nml_res['total'], nml_res['can-help'], nml_res['ratio'], pop_res['can-help'], pop_res['ratio']))
        nml_overall.append((cfg.name, nml_res['detail']))
        pop_overall.append((cfg.name, pop_res['detail']))

    overall_res_fp = os.path.join(data_dir, 'overall_res.csv')
    with open(overall_res_fp, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for item in overall_res:
            writer.writerow(item)
    nml_overall_fp = os.path.join(data_dir, 'nml_overall.csv')
    with open(nml_overall_fp, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                quotechar = '|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('software-name', 0, 1, 2, 3, 4, 5, '>5'))
        for item in nml_overall[1:]:
            writer.writerow((item[0], item[1]['0'],item[1]['1'],item[1]['2'],item[1]['3'],item[1]['4'],item[1]['5'],item[1]['6']))

    pop_overall_fp = os.path.join(data_dir, 'pop_overall.csv')
    with open(pop_overall_fp, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                quotechar = '|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('software-name', 0, 1, 2, 3, 4, 5, '>5'))
        for item in pop_overall[1:]:
            writer.writerow((item[0], item[1]['0'],item[1]['1'],item[1]['2'],item[1]['3'],item[1]['4'],item[1]['5'],item[1]['6']))


if __name__ == '__main__':
    eval_wrap(ApacheEval)
    #eval_wrap(HadoopEval)
    #eval_wrap(MysqlEval)
    #collect_results_and_dump_to_csv()
