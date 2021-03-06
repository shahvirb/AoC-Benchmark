import cProfile
import pstats
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import prof
import click

@click.command()
@click.option('-ip', '--input_path', type=click.Path(exists=True), required=True)
@click.option('-sp', '--sol_path', type=click.Path(exists=True), required=True)
@click.option('-n', '--num', type=int, default=100)
@click.option('-s', '--func_select', type=int, default=-1)
@click.option('-c', '--cache', type=bool, default=True)
def click_collect_dataframe(*args, **kwargs):
    collect_dataframe(*args, **kwargs)

def collect_dataframe(input_path, sol_path, num, func_select=-1, cache=True):
    sys.path.insert(0, str(sol_path))
    from register import REGISTRATION
    sys.path.pop(0)

    res = collect_stats(
        REGISTRATION[func_select],
        input_path,
        num
    )
    df = pd.DataFrame(res, columns=['Execution Duration [ms]'])
    df.index.name = 'Run #'

    if cache:
        add_to_cache(df, REGISTRATION[func_select][1])

    return df

def collect_stats(solution, input_path, n=1000):
    print('Collecting stats on:\n{}.{}'.format(solution[1].__module__, solution[1].__name__))
    print('{} runs'.format(n))
    input = prof.get_input(solution[0], input_path)
    res = np.empty(n)
    start = datetime.now()
    for i in range(n):
        cProfile.runctx('solution[1](input)', globals=globals(), locals=locals(), filename='cstats')
        stats = pstats.Stats('cstats')
        t = prof.extract_time(stats, solution[1])
        res[i] = t
        print('Run {} {:.1f} ms'.format(i, t))
    end = datetime.now()
    print('Elapsed time: {}'.format(end - start))
    return res

def add_to_cache(df, function):
    cache_path = '{}.{}'.format(function.__module__, function.__name__).replace('.', '-')
    cache_path += '.csv'
    result_folder = Path(os.getcwd()) / 'results'
    if not result_folder.exists():
        result_folder.mkdir(parents=True)
    cache_path =  result_folder / cache_path
    if cache_path.exists():
        df2 = pd.read_csv(cache_path)
        df2 = df2.set_index(df2.columns[0])
        df = pd.concat([df2, df], axis=0)
        df.index = pd.Index([i for i in range(df.count()[0])], name=df.index.name)
    df.to_csv(cache_path)

def pstats_to_df(stats_obj):
    df = pd.DataFrame({
        'paths': [Path(func[0]) for func in stats_obj.stats],
        'lines': [func[1] for func in stats_obj.stats],
        'func names': [func[2] for func in stats_obj.stats],
        # 'func names': [pstats.func_std_string(func) for func in stats_obj.stats],
        'primitive calls': [stats_obj.stats[func][0] for func in stats_obj.stats],
        'total calls': [stats_obj.stats[func][1] for func in stats_obj.stats],
        'total time': [stats_obj.stats[func][2] * 1000 for func in stats_obj.stats],
        'cumulative time': [stats_obj.stats[func][3] * 1000 for func in stats_obj.stats]
    })

    df['percall total'] = df['total time'] / df['total calls']
    df['percall cumulative'] = df['cumulative time'] / df['primitive calls']
    return df

if __name__ == '__main__':
    click_collect_dataframe()