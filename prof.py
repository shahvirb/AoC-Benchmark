from pathlib import Path
import pandas as pd
from memory_profiler import memory_usage
import cProfile
import pstats

from register import REGISTRATION

def profile_repo(repo_path):
    res = {}
    for day in REGISTRATION:
        print('Profiling {}'.format(day))
        res[day] = {}

        DUT = REGISTRATION[day]

        input = get_input(1)

        res[day]['Memory'] = memory_usage((DUT,(),{'input': input}), max_usage=True)[0]
        print('Memory used: {}'.format(res[day]['Memory']))

        cProfile.runctx('DUT(input)', globals=globals(), locals=locals(), filename='cstats')
        stats = pstats.Stats('cstats')
        stats.print_stats()
        parse_pstats(stats)

    return res

def get_input(day):
    glob = 'day{}*.txt'.format(day)
    file = [f for f in Path(r'C:\Users\lanca_000\Documents\Software\Python\Practice\Advent of Code\2017').glob(glob)][0]
    with open(file, 'r') as f:
        return f.read()

def extract_time(pstats, func):
    for func in pstats.stats:
        if func.__name__ == func[2]:
            return pstats.stats[func][3] * 1000

def parse_pstats(stats_obj):
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
    prof = profile_repo(Path(r'C:\Users\lanca_000\Documents\Software\Python\Practice\Advent of Code'))
    print(prof)