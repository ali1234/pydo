import pathlib
import subprocess

def git(repo, *cmd):
    return subprocess.check_output(['git', '-C', str(repo)] + list(cmd))

def git_repo_scan_inner(*repos):
    for r in repos:
        yield from git(r, 'ls-files', '-mo', '--exclude-standard').split(b'\n')[:-1]
        yield git(r, 'rev-parse', '--absolute-git-dir').split(b'\n')[0] + b'/logs/HEAD'

def git_repo_scan(*repos):
    return list(pathlib.Path(f.decode('utf-8')) for f in git_repo_scan_inner(*repos))


def dir_scan_inner(*dirs):
    for d in dirs:
        yield from d.rglob('*')

def dir_scan(*dirs):
    return list(dir_scan_inner(*dirs))