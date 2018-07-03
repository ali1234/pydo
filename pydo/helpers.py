import itertools
import pathlib

import sh


def timestamp(filename):
    ts = pathlib.Path(filename).stat().st_mtime
    return ts


def repo_files(filename):
    p = pathlib.Path(filename)
    yield from (str(p / f) for f in sh.git('-C', filename, 'ls-files', '-mo', '--exclude-standard').split('\n')[:-1])
    yield sh.git('-C', filename, 'rev-parse', '--absolute-git-dir').split('\n')[0]+'/logs/HEAD'


def check_timestamps(sources, targets, verbose=True):
    try:
        target_timestamps = list(timestamp(f) for f in targets)
        source_timestamps = list(timestamp(f) for f in sources)
        if verbose:
            for t, s in itertools.product(zip(target_timestamps, targets), zip(source_timestamps, sources)):
                if t < s:
                    print(t[1], '<', s[1])
        return min(target_timestamps) < max(source_timestamps)
    except FileNotFoundError:
        return True
