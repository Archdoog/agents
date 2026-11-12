pre-pr:
    for script in skills/resolve-pr-comments/scripts/*.sh; do bash -n "$script" || exit; done
    shellcheck -x -P SCRIPTDIR skills/resolve-pr-comments/scripts/*.sh
    python3 -m unittest discover -s tests -v
    git diff --check
