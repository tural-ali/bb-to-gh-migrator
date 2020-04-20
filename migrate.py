import os
import sys

from github.Repository import Repository
from pybitbucket.bitbucket import Client as BbClient, Bitbucket
from github import Github

APP_KEYS = {
    'bitbucket': 'Get it from https://bitbucket.org/account/user/YOUR_USERNAME/app-passwords',
    'github': 'Get it from https://github.com/settings/tokens',
}
GH_USER = 'YOUR_USERNAME'
BB_USER = 'YOUR_USERNAME'

BB_EMAIL = 'YOUR@EMAIL.com'

WORKING_DIR = '~/git/bitbucket-migration'


def bitbucket():
    from pybitbucket.auth import BasicAuthenticator

    return BbClient(
        BasicAuthenticator(
            BB_USER,
            APP_KEYS['bitbucket'],
            BB_EMAIL
        )
    )


def github():
    return Github(APP_KEYS['github'])


def bb_get_repositories(client: BbClient):
    # noinspection PyUnresolvedReferences
    return Bitbucket(client).repositoriesByOwnerAndRole(owner=client.get_username(), role='owner')


def bb_clone_repo(slug: str):
    import subprocess

    dest = os.path.join(WORKING_DIR, '%s.git' % slug)
    if os.path.isdir(dest):
        # Assume we have already cloned the repo.
        return True

    args = [
        'git',
        'clone',
        '--bare',
        'git@bitbucket.org:%s/%s.git' % (BB_USER, slug)
    ]
    process = subprocess.Popen(args, cwd=WORKING_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    stdout, stderr = process.communicate()
    if stderr is not None:
        print(stderr.decode())
        return False

    print('Clone: %s' % stdout.decode())
    return True


def gh_get_repo(repo_slug: str):
    from github import UnknownObjectException

    try:
        return github().get_repo('%s/%s' % (GH_USER, repo_slug))
    except UnknownObjectException:
        return None


def gh_is_repo_empty(repo: Repository):
    from github import GithubException

    try:
        repo.get_file_contents('README.md')
    except GithubException as err:
        if err.status == 404:
            return err.data['message'] == 'This repository is empty.'
        else:
            raise err

    return False


def gh_repo_create(name: str, desc: str, is_private: bool):
    return github().get_user().create_repo(
        name,
        description=desc,
        private=is_private,
        has_issues=False,
        has_wiki=False,
        has_downloads=False,
        has_projects=False,
        auto_init=False,
    )


def gh_repo_push(slug: str):
    import subprocess

    repo_dir = os.path.join(WORKING_DIR, '%s.git' % slug)
    args = [
        'git',
        'push',
        '--mirror',
        'git@github.com:%s/%s.git' % (GH_USER, slug)
    ]
    process = subprocess.Popen(args, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    stdout, stderr = process.communicate()
    if stderr is not None:
        print(stderr.decode())
        return False

    print('Push: %s' % stdout.decode())
    return True


def process_repo(slug: str, desc: str, private: bool):
    gh_repo = gh_get_repo(slug)

    if gh_repo is None:
        print("Must create: %s" % slug)
        gh_repo_create(slug, desc, private)

    bb_clone_repo(slug)
    gh_repo_push(slug)
    return True


if __name__ == '__main__':
    # Create CWD if needed
    WORKING_DIR = os.path.expanduser(WORKING_DIR)
    os.path.exists(WORKING_DIR) or os.mkdir(WORKING_DIR, 0o775)

    gh_client = github()
    for repo in bb_get_repositories(bitbucket()):
        # pprint(repo)
        print('Processing: %s (Priv: %s)' % (repo['slug'], repo['is_private']))
        process_repo(repo['slug'], repo['description'], repo['is_private'])
