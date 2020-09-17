from sklearn.model_selection import ParameterGrid
import argparse
import os
import json
import subprocess
import logging

from modules.file_utils import FileUtils
from HPC.A.modules.logging_utils import LoggingUtils

max_process_count = 20

parser = argparse.ArgumentParser(description='task generator HPC')

parser.add_argument('-main_script',
                    default='main.py',
                    type=str)

parser.add_argument(
    '-report',
    help='csv report of all tasks combined',
    default='tasks',
    type=str)

parser.add_argument(
    '-conda_env',
    help='name of conda environment',
    default='conda_env_01',
    type=str)

parser.add_argument(
    '-hpc_feautre_gpu',
    help='k40 v100',
    default='v100',
    type=str)

parser.add_argument(
    '-params_grid_json',
    default='params.json',
    help='parameters for grid search',
    required=False)

parser.add_argument(
    '-params_report',
    help='csv columns, parameters for summary',
    default=['id', 'name', 'repeat_id'],
    nargs='*',
    required=False)

parser.add_argument(
    '-repeat',
    help='how many times each set of parameters should be repeated for testing stability',
    default=1,
    type=int)

parser.add_argument(
    '-hpc_gpu_count',
    help='HPC - how many GPUs used per task',
    default=2,
    type=int)

parser.add_argument(
    '-hpc_cpu_count_for_gpu',
    help='HPC - how many CPUs used per GPU task',
    default=16,
    type=int)

parser.add_argument(
    '-hpc_cpu_count',
    help='HPC - how many CPUs used per task',
    default=12,
    type=int)

parser.add_argument(
    '-hpc_mem',
    help='HPC - override mem GB',
    default=0,
    type=int)

parser.add_argument(
    '-is_hpc',
    help='is HPC qsub tasks or local tasks',
    default=True,
    type=lambda x: (str(x).lower() == 'true'))

parser.add_argument(
    '-hpc_queue',
    help='hpc queue',
    default='batch',
    type=str)

args, args_other = parser.parse_known_args()

FileUtils.createDir('./reports')
FileUtils.createDir('./tasks')
#FileUtils.createDir('./tasks/' + args.report)

if args.is_hpc:
    FileUtils.createDir(os.path.expanduser('~') + '/tmp')

logging_utils = LoggingUtils(name=os.path.join('reports', args.report + '.txt'))

task_settings = {
    'id': 0,
    'repeat_id': 0
}

hpc_settings_path = os.path.join('tasks', 'tasks.json')
if os.path.exists(hpc_settings_path):
    with open(hpc_settings_path, 'r') as outfile:
        hpc_settings_loaded = json.load(outfile)
        for key in hpc_settings_loaded:
            task_settings[key] = hpc_settings_loaded[key]

def save_hpc_settings():
    with open(hpc_settings_path, 'w') as outfile:
        json.dump(task_settings, outfile)

with open(args.params_grid_json) as json_file:
    param_grid = json.load(json_file)

all_combinations = list(ParameterGrid(param_grid))
all_comb_dict = {}
for index, comb in enumerate(all_combinations):
    all_comb_dict[index] = comb

path_base = os.path.dirname(os.path.abspath(__file__))

logging_utils.my_logger.info(' All Combinations of Hyper-Param')
logging_utils.my_logger.info(json.dumps(all_comb_dict, indent=4))
logging_utils.my_logger.info('Number of all combinations {}'.format(len(all_combinations)))

print('Number of all combinations', len(all_combinations))



for combination in range(len(all_combinations)):

    if combination > max_process_count:
        print('Maximum Number of Processes Exceeded')
        break

    single_task_dir = './tasks/' + str(combination)
    FileUtils.createDir(single_task_dir)
    script_path = single_task_dir + '/' + str(combination)+'.sh'

    with open(script_path, 'w') as fp:
        if args.is_hpc:
            fp.write(f'#!/bin/sh -v\n')
            fp.write(f'#PBS -e {path_base}/tasks/{combination}\n')
            fp.write(f'#PBS -o {path_base}/tasks/{combination}\n')

            walltime = 96
            mem = 60

            que = args.hpc_queue
            if args.hpc_queue == 'fast':
                walltime = 8
                mem = 40
            elif args.hpc_queue == 'batch':
                walltime = 96
                mem = 5

            fp.write(f'#PBS -q {que}\n')

            fp.write(f'#PBS -p 1000\n')

            if args.hpc_queue == 'fast':
                fp.write(f'#PBS -l nodes=1:ppn=8:gpus=1,feature=v100\n')
            elif args.hpc_queue == 'batch':
                fp.write(f'#PBS -l nodes=1:ppn=1\n')

            fp.write(f'#PBS -l mem={mem}gb\n')
            fp.write(f'#PBS -l walltime={walltime}:00:00\n\n')
            fp.write(f'eval "$(conda shell.bash hook)"\n')
            fp.write(f'source activate {args.conda_env}\n\n')
            fp.write(f'cd {path_base}/tasks/{combination}\n')

            single_param = all_combinations[0]
            keys = list(single_param.keys())
            kvpairs = ''
            for key in keys:
                value = single_param.get(key)
                kvpairs += '-' + str(key) + ' ' + str(value) + ' '
            fp.write(f'python {path_base}/{args.main_script}.py {kvpairs} \n')
            fp.close()

            #submit processes
            cmd = f'chmod +x {script_path}'
            stdout = subprocess.check_output(cmd, shell=True, encoding='utf-8')
            cmd = 'qsub -N ' + 'nm-'+str(combination) + ' ' + script_path
            stdout = subprocess.check_output(cmd, shell=True, encoding='utf-8')

            print('submitting Process', stdout)

