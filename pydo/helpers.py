import pathlib

import sh

def timestamp(filename):
    return pathlib.Path(filename).stat().st_mtime

def timestamp_git_repo(filename):
    p = pathlib.Path(filename)
    files = list(str(p / f) for f in sh.git('-C', filename, 'ls-files', '-mo', '--exclude-standard').split('\n')[:-1])
    files.extend(sh.git('-C', filename, 'rev-parse', '--absolute-git-dir').split('\n')[:-1])
    return max(timestamp(f) for f in files)
