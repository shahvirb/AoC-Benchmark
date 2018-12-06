import gitsync
import venvbuild
import os
import yaml
import click
import logging
import subprocess

INPUTS_DIR = 'AoC-Inputs'

def build_env(giturl, git_dir, venv_dir):
    gitsync.sync_repo(giturl, git_dir)
    venvbuild.create_venv(venv_dir)

    user_reqs = os.path.join(git_dir, 'requirements.txt')
    venvbuild.pip_install_requirements(venv_dir, user_reqs)

    profiler_reqs = 'profiler_requirements.txt'
    venvbuild.pip_install_requirements(venv_dir, profiler_reqs)


def run_profiler(venv_dir, user_src_dir, inputs_dir):
    cmd = [os.path.join(venv_dir, 'Scripts', 'python.exe'), 'prof.py', '-rp', user_src_dir, '-ip', inputs_dir]
    subprocess.run(cmd)

@click.command()
@click.option('--users', help='users.yaml file')
def from_users_ini(users):
    cfg = yaml.load(open(users, 'r'))
    working_dir = cfg['working_dir']

    logging.info('Fetching Inputs')
    inputs_dir = os.path.join(working_dir, INPUTS_DIR)
    gitsync.sync_repo(cfg['input']['repo_url'], inputs_dir)

    for u in cfg['users']:
        username = list(u)[0]
        user = u[username]
        logging.info('Building environment for {}'.format(username))
        git_path = os.path.join(working_dir, username + '_repo')
        venv_path = os.path.join(working_dir, username + '_venv')
        build_env(user['repo_url'], git_path, venv_path)

        logging.info('Computing benchmarks for {}'.format(username))
        run_profiler(venv_path, git_path, inputs_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    from_users_ini()