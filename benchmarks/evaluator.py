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

from config import EvalConfig

do_popularity = True
do_normal = True
base_path = os.path.join(poj_dir, 'dataset/')

def eval_wrap(config):
    """
    config is a EvalConfig instance
    """
    print '\n~~~~~~~~~~~~~~~~~~evaluating ' + config.sw_name + ' start ~~~~~~'
    eval(config)
    compare_result(config)
    print   '~~~~~~~~~~~~~~~~~~evaluating ' + config.sw_name + ' end ~~~~~~'

def eval(config):
    if not os.path.exists(config.index_path):
        os.mkdir(config.index_path)

    if not os.path.exists(config.index_pop_path):
        os.mkdir(config.index_pop_path)

    if do_normal:
        print 'evaluating Cox purely on manuals'
        cmd_wrapper.execute_index(config.index_path,
                config.parameter_dir,
                None)
        res = cmd_wrapper.execute_search(config.index_path,
                config.input_file,
                config.output_file, 
                config.filter_path,
                True, True)
        #for (k, v) in res.items():
        #    print str(k) + ' : ' + str(v)

    if do_popularity:
        print 'evaluating Cox with popularity information'
        if not os.path.exists(config.pop_file_path):
             print 'no popularity file exists, return'
             return
        #    config.std_pop()
        cmd_wrapper.execute_index(config.index_pop_path,
                config.parameter_dir,
                config.pop_file_path)
        res = cmd_wrapper.execute_search(config.index_pop_path,
                config.input_file,
                config.output_w_pop,
                config.filter_path,
                 True, False)

        #for (k, v) in res.items():
        #    print str(k) + ' : ' + str(v)

def compare_result(config):
    print 'start to compare the results'
    #standard result
    std_res = config.std_res
    if do_normal:
        nml_res = cmd_wrapper.extract_search_outputfile(config.output_file)
        print '*********Normal Search Results:'
        s = generate_result_comp_report(std_res, nml_res, None)
        print s['brief']
        open(os.path.join(output_data_dir, 'r_' + config.sw_name + 'nml_res.txt'), 'w').write(s['detail'])
        open(os.path.join(output_data_dir, 'res_nml_' + config.sw_name + '.json'), 'w').write(s['structure'])

    if do_popularity:
        pop_res = cmd_wrapper.extract_search_outputfile(config.output_w_pop)
        print '**********Popularity Search Results:'
        s = generate_result_comp_report(std_res, pop_res, config.opt2mod_map)
        print s['brief']
        open(os.path.join(output_data_dir, 'r_' + config.sw_name + 'pop_res.txt'), 'w').write(s['detail'])
        open(os.path.join(output_data_dir, 'res_pop_' + config.sw_name + '.json'), 'w').write(s['structure'])

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

#if __name__ == '__main__':
#    appname  = 'httpd'
#    parpath  = '/home/tixu/Cox/data/httpd/parameters'
#    poppath  = '/home/tixu/Cox/benchmarks/data/apache_popularity.csv' 
#    p2mmaps  = '/home/tixu/Cox/benchmarks/data/apache_modules.csv'
#    testcase = '/home/tixu/Cox/benchmarks/data/apache_tc_icon.csv' 
#    base_dir = '/home/tixu/Cox/benchmarks/data/' + appname
#    config = EvalConfig(appname, parpath, poppath, p2mmaps, None, testcase, base_dir)
#    eval_wrap(config)
