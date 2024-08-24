from git import Repo

from configs import configs


class GitRepo:
    def __init__(self) -> None:
        self.repo = Repo(configs['GIT_REPO'])
        # TODO:
        # - check if repo exists
        # - check if repo is initialized (bare)
        # - check if repo is up to date with remote repo
        # - check if user has write access to repo
        # - check if user has read access to remote repo
        # - check if user has push access to remote repo
        # - check if repo has at least one branch
        # - check if branch is not currently checked out
        # - check if branch is not currently merged into master
        # - check if branch is not currently rebased onto another branch
        # - check if branch is not currently ahead of remote branch
        # - check if branch is not currently behind remote branch
        # - check if branch is not currently in conflict
        # - check if branch is not currently a detached HEAD
        # - check if branch is not currently a protected branch
        # - check if branch is not currently a protected branch with write access
        # - check if branch is not currently a protected
        # - check if repo is clean before proceeding
