import pathlib

import git

from configs import configs
from utils import exit_with_error


class GitHelper:
    def __init__(self):
        self.repo: str = configs['GIT_REPO']
        self.repo_path: pathlib.Path = configs['LOCAL_REPO']
        self.ref: str = configs['GIT_REF']
        self.user_name: str = configs['GIT_USER']
        self.user_email: str = configs['GIT_EMAIL']

        self.git_repo = git.Repo.init(self.repo_path)
        self.git_remote = self.git_repo.create_remote('origin', self.repo)
        try:
            self.git_remote.fetch()  # git fetch origin
        except git.GitCommandError:
            exit_with_error(f'Invalid git repository: {self.repo}')

    def pull(self):
        """Run `git pull origin GIT_REF`"""
        if self.ref in [r.name.split('/')[-1] for r in self.git_remote.refs]:
            self.git_remote.pull(self.ref)  # git pull origin GIT_REF

    def push(self, comment: str, notes: list[str], *, force: bool = False) -> None:
        author = git.Actor(self.user_name, self.user_email)
        self.git_repo.index.add(notes)  # git add NOTES
        self.git_repo.index.commit(comment, author=author, committer=author)  # git commit -m COMMENT
        # TODO: reuse local repo
        if self.git_repo.refs[0].name == 'master':
            self.git_repo.heads.master.rename(self.ref)  # git branch -m master GIT_REF
        self.git_remote.push(self.ref, force=force).raise_if_error()  # git push origin GIT_REF


git_helper = GitHelper()
