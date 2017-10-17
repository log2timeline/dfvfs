#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to manage code reviews."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import json
import logging
import os
import random
import re
import shlex
import subprocess
import sys
import time

# pylint: disable=import-error
# pylint: disable=no-name-in-module
if sys.version_info[0] < 3:
  # Use urllib2 here since this code should be able to be used by a default
  # Python set up. Otherwise usage of requests is preferred.
  import urllib as  urllib_parse
  import urllib2 as urllib_error
  import urllib2 as urllib_request
else:
  import urllib.error as urllib_error
  import urllib.parse as urllib_parse
  import urllib.request as urllib_request

# Change PYTHONPATH to include utils.
sys.path.insert(0, '.')

import utils.upload  # pylint: disable=wrong-import-position


class CLIHelper(object):
  """Command line interface (CLI) helper."""

  def RunCommand(self, command):
    """Runs a command.

    Args:
      command (str): command to run.

    Returns:
      tuple[int, bytes, bytes]: exit code, stdout and stderr data.
    """
    arguments = shlex.split(command)

    try:
      process = subprocess.Popen(
          arguments, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    except OSError as exception:
      logging.error('Running: "{0:s}" failed with error: {1:s}'.format(
          command, exception))
      return 1, None, None

    output, error = process.communicate()
    if process.returncode != 0:
      logging.error('Running: "{0:s}" failed with error: {1!s}.'.format(
          command, error))

    return process.returncode, output, error


class CodeReviewHelper(CLIHelper):
  """Codereview upload.py command helper."""

  _REVIEWERS_PER_PROJECT = {
      'acstore': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'dfdatetime': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'dfkinds': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'dfvfs': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'dfwinreg': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'dftimewolf': frozenset([
          'jberggren@gmail.com',
          'someguyiknow@google.com',
          'tomchop@gmail.com']),
      'l2tpreg': frozenset([
          'joachim.metz@gmail.com',
          'onager@deerpie.com']),
      'plaso': frozenset([
          'aaronp@gmail.com',
          'jberggren@gmail.com',
          'joachim.metz@gmail.com',
          'onager@deerpie.com',
          'romaing@google.com'])}

  _REVIEWERS_DEFAULT = frozenset([
      'jberggren@gmail.com',
      'joachim.metz@gmail.com',
      'onager@deerpie.com'])

  _REVIEWERS_CC = frozenset([
      'kiddi@kiddaland.net',
      'log2timeline-dev@googlegroups.com'])

  def __init__(self, email_address, no_browser=False):
    """Initializes a codereview helper.

    Args:
      email_address (str): email address.
      no_browser (Optional[bool]): True if the functionality to use the
          webbrowser to get the OAuth token should be disabled.
    """
    super(CodeReviewHelper, self).__init__()
    self._access_token = None
    self._email_address = email_address
    self._no_browser = no_browser
    self._upload_py_path = os.path.join('utils', 'upload.py')
    self._xsrf_token = None

  def _GetReviewer(self, project_name):
    """Determines the reviewer.

    Args:
      project_name (str): name of the project.

    Returns:
      str: email address of the reviewer that is used on codereview.
    """
    reviewers = list(self._REVIEWERS_PER_PROJECT.get(
        project_name, self._REVIEWERS_DEFAULT))

    try:
      reviewers.remove(self._email_address)
    except ValueError:
      pass

    random.shuffle(reviewers)

    return reviewers[0]

  def _GetReviewersOnCC(self, project_name, reviewer):
    """Determines the reviewers on CC.

    Args:
      project_name (str): name of the project.
      reviewer (str): email address of the reviewer that is used on codereview.

    Returns:
      str: comma seperated email addresses.
    """
    reviewers_cc = set(self._REVIEWERS_PER_PROJECT.get(
        project_name, self._REVIEWERS_DEFAULT))
    reviewers_cc.update(self._REVIEWERS_CC)

    reviewers_cc.remove(reviewer)

    try:
      reviewers_cc.remove(self._email_address)
    except KeyError:
      pass

    return ','.join(reviewers_cc)

  def AddMergeMessage(self, issue_number, message):
    """Adds a merge message to the code review issue.

    Where the merge is a commit to the main project git repository.

    Args:
      issue_number (int|str): codereview issue number.
      message (str): message to add to the code review issue.

    Returns:
      bool: merge message was added to the code review issue.
    """
    codereview_access_token = self.GetAccessToken()
    xsrf_token = self.GetXSRFToken()
    if not codereview_access_token or not xsrf_token:
      return False

    codereview_url = b'https://codereview.appspot.com/{0!s}/publish'.format(
        issue_number)

    post_data = urllib_parse.urlencode({
        'add_as_reviewer': 'False',
        'message': message,
        'message_only': 'True',
        'no_redirect': 'True',
        'send_mail': 'True',
        'xsrf_token': xsrf_token})

    request = urllib_request.Request(codereview_url)

    # Add header: Authorization: OAuth <codereview access token>
    request.add_header(
        'Authorization', 'OAuth {0:s}'.format(codereview_access_token))

    # This will change the request into a POST.
    request.add_data(post_data)

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed publish to codereview issue: {0!s} with error: {1!s}'.format(
              issue_number, exception))
      return False

    if url_object.code not in (200, 201):
      logging.error((
          'Failed publish to codereview issue: {0!s} with status code: '
          '{1:d}').format(issue_number, url_object.code))
      return False

    return True

  def CloseIssue(self, issue_number):
    """Closes a code review issue.

    Args:
      issue_number (int|str): codereview issue number.

    Returns:
      bool: True if the code review was closed.
    """
    codereview_access_token = self.GetAccessToken()
    xsrf_token = self.GetXSRFToken()
    if not codereview_access_token or not xsrf_token:
      return False

    codereview_url = b'https://codereview.appspot.com/{0!s}/close'.format(
        issue_number)

    post_data = urllib_parse.urlencode({
        'xsrf_token': xsrf_token})

    request = urllib_request.Request(codereview_url)

    # Add header: Authorization: OAuth <codereview access token>
    request.add_header(
        'Authorization', 'OAuth {0:s}'.format(codereview_access_token))

    # This will change the request into a POST.
    request.add_data(post_data)

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed closing codereview issue: {0!s} with error: {1!s}'.format(
              issue_number, exception))
      return False

    if url_object.code != 200:
      logging.error((
          'Failed closing codereview issue: {0!s} with status code: '
          '{1:d}').format(issue_number, url_object.code))
      return False

    return True

  def CreateIssue(self, project_name, diffbase, description):
    """Creates a new codereview issue.

    Args:
      project_name (str): name of the project.
      diffbase (str): diffbase.
      description (str): description.

    Returns:
      int: codereview issue number or None.
    """
    reviewer = self._GetReviewer(project_name)
    reviewers_cc = self._GetReviewersOnCC(project_name, reviewer)

    command = '{0:s} {1:s} --oauth2'.format(
        sys.executable, self._upload_py_path)

    if self._no_browser:
      command = '{0:s} --no_oauth2_webbrowser'.format(command)

    command = (
        '{0:s} --send_mail -r {1:s} --cc {2:s} -t "{3:s}" -y -- '
        '{4:s}').format(
            command, reviewer, reviewers_cc, description, diffbase)

    if self._no_browser:
      print(
          'Upload server: codereview.appspot.com (change with -s/--server)\n'
          'Go to the following link in your browser:\n'
          '\n'
          '    https://codereview.appspot.com/get-access-token\n'
          '\n'
          'and copy the access token.\n'
          '\n')
      print('Enter access token:', end=' ')

      sys.stdout.flush()

    exit_code, output, _ = self.RunCommand(command)
    print(output)

    if exit_code != 0:
      return

    issue_url_line_start = (
        'Issue created. URL: http://codereview.appspot.com/')
    for line in output.split(b'\n'):
      if issue_url_line_start in line:
        _, _, issue_number = line.rpartition(issue_url_line_start)
        try:
          return int(issue_number, 10)
        except ValueError:
          pass

  def GetAccessToken(self):
    """Retrieves the OAuth access token.

    Returns:
      str: codereview access token.
    """
    if not self._access_token:
      # TODO: add support to get access token directly from user.
      # pylint: disable=no-member
      self._access_token = utils.upload.GetAccessToken()
      if not self._access_token:
        logging.error('Unable to retrieve access token.')

    return self._access_token

  def GetXSRFToken(self):
    """Retrieves the XSRF token.

    Returns:
      str: codereview XSRF token or None if the token could not be obtained.
    """
    if not self._xsrf_token:
      codereview_access_token = self.GetAccessToken()
      if not codereview_access_token:
        return

      codereview_url = b'https://codereview.appspot.com/xsrf_token'

      request = urllib_request.Request(codereview_url)

      # Add header: Authorization: OAuth <codereview access token>
      request.add_header(
          'Authorization', 'OAuth {0:s}'.format(codereview_access_token))
      request.add_header('X-Requesting-XSRF-Token', '1')

      try:
        url_object = urllib_request.urlopen(request)
      except urllib_error.HTTPError as exception:
        logging.error(
            'Failed retrieving codereview XSRF token with error: {0!s}'.format(
                exception))
        return

      if url_object.code != 200:
        logging.error((
            'Failed retrieving codereview XSRF token with status code: '
            '{0:d}').format(url_object.code))
        return

      self._xsrf_token = url_object.read()

    return self._xsrf_token

  def QueryIssue(self, issue_number):
    """Queries the information of a code review issue.

    The query returns JSON data that contains:
    {
      "description":str,
      "cc":[str],
      "reviewers":[str],
      "owner_email":str,
      "private":bool,
      "base_url":str,
      "owner":str,
      "subject":str,
      "created":str,
      "patchsets":[int],
      "modified":str,
      "project":str,
      "closed":bool,
      "issue":int
    }

    Where the "created" and "modified" strings are formatted as:
    "YYYY-MM-DD hh:mm:ss.######"

    Args:
      issue_number (int|str): codereview issue number.

    Returns:
      dict[str,object]: JSON response or None.
    """
    codereview_url = b'https://codereview.appspot.com/api/{0!s}'.format(
        issue_number)

    request = urllib_request.Request(codereview_url)

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed querying codereview issue: {0!s} with error: {1!s}'.format(
              issue_number, exception))
      return

    if url_object.code != 200:
      logging.error((
          'Failed querying codereview issue: {0!s} with status code: '
          '{1:d}').format(issue_number, url_object.code))
      return

    response_data = url_object.read()
    return json.loads(response_data)

  def UpdateIssue(self, issue_number, diffbase, description):
    """Updates a code review issue.

    Args:
      issue_number (int|str): codereview issue number.
      diffbase (str): diffbase.
      description (str): description.

    Returns:
      bool: True if the code review was updated.
    """
    command = '{0:s} {1:s} --oauth2'.format(
        sys.executable, self._upload_py_path)

    if self._no_browser:
      command = '{0:s} --no_oauth2_webbrowser'.format(command)

    command = (
        '{0:s} -i {1!s} -m "Code updated." -t "{2:s}" -y -- '
        '{3:s}').format(command, issue_number, description, diffbase)

    if self._no_browser:
      print(
          'Upload server: codereview.appspot.com (change with -s/--server)\n'
          'Go to the following link in your browser:\n'
          '\n'
          '    https://codereview.appspot.com/get-access-token\n'
          '\n'
          'and copy the access token.\n'
          '\n')
      print('Enter access token:', end=' ')

      sys.stdout.flush()

    exit_code, output, _ = self.RunCommand(command)
    print(output)

    return exit_code == 0


class GitHelper(CLIHelper):
  """Git command helper."""

  def __init__(self, git_repo_url):
    """Initializes a git helper.

    Args:
      git_repo_url (str): git repo URL.
    """
    super(GitHelper, self).__init__()
    self._git_repo_url = git_repo_url
    self._remotes = []

  def _GetRemotes(self):
    """Retrieves the git repository remotes.

    Returns:
      list[str]: git repository remotes or None.
    """
    if not self._remotes:
      exit_code, output, _ = self.RunCommand('git remote -v')
      if exit_code == 0:
        self._remotes = list(filter(None, output.split(b'\n')))

    return self._remotes

  def AddPath(self, path):
    """Adds a specific path to be managed by git.

    Args:
      path (str): path.

    Returns:
      bool: True if the path was added.
    """
    command = 'git add -A {0:s}'.format(path)
    exit_code, _, _ = self.RunCommand(command)
    return exit_code == 0

  def CheckHasBranch(self, branch):
    """Checks if the git repo has a specific branch.

    Args:
      branch (str): name of the feature branch.

    Returns:
      bool: True if git repo has the specific branch.
    """
    exit_code, output, _ = self.RunCommand('git branch')
    if exit_code != 0:
      return False

    # Check for remote entries starting with upstream.
    for line in output.split(b'\n'):
      # Ignore the first 2 characters of the line.
      if line[2:] == branch:
        return True
    return False

  def CheckHasProjectOrigin(self):
    """Checks if the git repo has the project remote origin defined.

    Returns:
      bool: True if the git repo has the project origin defined.
    """
    origin_git_repo_url = self.GetRemoteOrigin()

    is_match = origin_git_repo_url == self._git_repo_url
    if not is_match:
      is_match = origin_git_repo_url == self._git_repo_url[:-4]

    return is_match

  def CheckHasProjectUpstream(self):
    """Checks if the git repo has the project remote upstream defined.

    Returns:
      bool: True if the git repo has the project remote upstream defined.
    """
    # Check for remote entries starting with upstream.
    for remote in self._GetRemotes():
      if remote.startswith(b'upstream\t{0:s}'.format(self._git_repo_url)):
        return True
    return False

  def CheckHasUncommittedChanges(self):
    """Checks if the git repo has uncommitted changes.

    Returns:
      bool: True if the git repo has uncommitted changes.
    """
    exit_code, output, _ = self.RunCommand('git status -s')
    if exit_code != 0:
      return False

    # Check if 'git status -s' yielded any output.
    for line in output.split(b'\n'):
      if line:
        return True
    return False

  def CheckSynchronizedWithUpstream(self):
    """Checks if the git repo is synchronized with upstream.

    Returns:
      bool: True if the git repo is synchronized with upstream.
    """
    # Fetch the entire upstream repo information not only that of
    # the master branch. Otherwise the information about the current
    # upstream HEAD is not updated.
    exit_code, _, _ = self.RunCommand('git fetch upstream')
    if exit_code != 0:
      return False

    # The result of "git log HEAD..upstream/master --oneline" should be empty
    # if the git repo is synchronized with upstream.
    exit_code, output, _ = self.RunCommand(
        'git log HEAD..upstream/master --oneline')
    return exit_code == 0 and not output

  def CommitToOriginInNameOf(
      self, codereview_issue_number, author, description):
    """Commits changes in name of an author to the master branch of origin.

    Args:
      codereview_issue_number (int|str): codereview issue number.
      author (str): full name and email address of the author, formatted as:
          "Full Name <email.address@example.com>".
      description (str): description of the commit.

    Returns:
      bool: True if the changes were committed to the git repository.
    """
    command = (
        'git commit -a --author="{0:s}" '
        '-m "Code review: {1:s}: {2:s}"').format(
            author, codereview_issue_number, description)
    exit_code, _, _ = self.RunCommand(command)
    if exit_code != 0:
      return False

    exit_code, _, _ = self.RunCommand('git push origin master')
    if exit_code != 0:
      return False

    return True

  def DropUncommittedChanges(self):
    """Drops the uncommitted changes."""
    self.RunCommand('git stash')
    self.RunCommand('git stash drop')

  def GetActiveBranch(self):
    """Retrieves the active branch.

    Returns:
      str: name of the active branch or None.
    """
    exit_code, output, _ = self.RunCommand('git branch')
    if exit_code != 0:
      return False

    # Check for remote entries starting with upstream.
    for line in output.split(b'\n'):
      if line.startswith(b'* '):
        # Ignore the first 2 characters of the line.
        return line[2:]
    return

  def GetChangedFiles(self, diffbase=None):
    """Retrieves the changed files.

    Args:
      diffbase (Optional[str]): git diffbase, for example "upstream/master".

    Returns:
      list[str]: names of the changed files.
    """
    if diffbase:
      command = 'git diff --name-only {0:s}'.format(diffbase)
    else:
      command = 'git ls-files'

    exit_code, output, _ = self.RunCommand(command)
    if exit_code != 0:
      return []

    return output.split(b'\n')

  def GetChangedPythonFiles(self, diffbase=None):
    """Retrieves the changed Python files.

    Note that several Python files are excluded:
    * Python files generated by the protobuf compiler (*_pb2.py)
    * Python files used as test data (test_data/*.py)
    * Python files used for sphinx (docs/*.py)
    * setup.py and utils/upload.py

    Args:
      diffbase (Optional[str]): git diffbase, for example "upstream/master".

    Returns:
      list[str]: names of the changed Python files.
    """
    upload_path = os.path.join('utils', 'upload.py')
    python_files = []
    for changed_file in self.GetChangedFiles(diffbase=diffbase):
      if (not changed_file.endswith('.py') or
          changed_file.endswith('_pb2.py') or
          not os.path.exists(changed_file) or
          changed_file.startswith('data') or
          changed_file.startswith('docs') or
          changed_file.startswith('test_data') or
          changed_file in ('setup.py', upload_path)):
        continue

      python_files.append(changed_file)

    return python_files

  def GetEmailAddress(self):
    """Retrieves the email address.

    Returns:
      str: email address or None.
    """
    exit_code, output, _ = self.RunCommand('git config user.email')
    if exit_code != 0:
      return

    output_lines = output.split(b'\n')
    if not output_lines:
      return

    return output_lines[0]

  def GetLastCommitMessage(self):
    """Retrieves the last commit message.

    Returns:
      str: last commit message or None.
    """
    exit_code, output, _ = self.RunCommand('git log -1')
    if exit_code != 0:
      return

    # Expecting 6 lines of output where the 5th line contains
    # the commit message.
    output_lines = output.split(b'\n')
    if len(output_lines) != 6:
      return

    return output_lines[4].strip()

  def GetRemoteOrigin(self):
    """Retrieves the remote origin.

    Returns:
      str: git repository URL or None.
    """
    # Check for remote entries starting with origin.
    for remote in self._GetRemotes():
      if remote.startswith(b'origin\t'):
        values = remote.split()
        if len(values) == 3:
          return values[1]

  def PullFromFork(self, git_repo_url, branch):
    """Pulls changes from a feature branch on a fork.

    Args:
      git_repo_url (str): git repository URL of the fork.
      branch (str): name of the feature branch of the fork.

    Returns:
      bool: True if the pull was successful.
    """
    command = 'git pull --squash {0:s} {1:s}'.format(git_repo_url, branch)
    exit_code, _, _ = self.RunCommand(command)
    return exit_code == 0

  def PushToOrigin(self, branch, force=False):
    """Forces a push of the active branch of the git repo to origin.

    Args:
      branch (str): name of the feature branch.
      force (Optional[bool]): True if the push should be forced.

    Returns:
      bool: True if the push was successful.
    """
    if force:
      command = 'git push --set-upstream origin {0:s}'.format(branch)
    else:
      command = 'git push -f --set-upstream origin {0:s}'.format(branch)

    exit_code, _, _ = self.RunCommand(command)
    return exit_code == 0

  def RemoveFeatureBranch(self, branch):
    """Removes the git feature branch both local and from origin.

    Args:
      branch (str): name of the feature branch.
    """
    if branch == 'master':
      return

    self.RunCommand('git push origin --delete {0:s}'.format(branch))
    self.RunCommand('git branch -D {0:s}'.format(branch))

  def SynchronizeWithOrigin(self):
    """Synchronizes git with origin.

    Returns:
      bool: True if the git repository has synchronized with origin.
    """
    exit_code, _, _ = self.RunCommand('git fetch origin')
    if exit_code != 0:
      return False

    exit_code, _, _ = self.RunCommand(
        'git pull --no-edit origin master')

    return exit_code == 0

  def SynchronizeWithUpstream(self):
    """Synchronizes git with upstream.

    Returns:
      bool: True if the git repository has synchronized with upstream.
    """
    exit_code, _, _ = self.RunCommand('git fetch upstream')
    if exit_code != 0:
      return False

    exit_code, _, _ = self.RunCommand(
        'git pull --no-edit --rebase upstream master')
    if exit_code != 0:
      return False

    exit_code, _, _ = self.RunCommand('git push')

    return exit_code == 0

  def SwitchToMasterBranch(self):
    """Switches git to the master branch.

    Returns:
      bool: True if the git repository has switched to the master branch.
    """
    exit_code, _, _ = self.RunCommand('git checkout master')
    return exit_code == 0


class GitHubHelper(object):
  """Github helper."""

  def __init__(self, organization, project):
    """Initializes a github helper.

    Args:
      organization (str): github organization name.
      project (str): github project name.
    """
    super(GitHubHelper, self).__init__()
    self._organization = organization
    self._project = project

  def CreatePullRequest(
      self, access_token, codereview_issue_number, origin, description):
    """Creates a pull request.

    Args:
      access_token (str): github access token.
      codereview_issue_number (int|str): codereview issue number.
      origin (str): origin of the pull request, formatted as:
          "username:feature".
      description (str): description.

    Returns:
      bool: True if the pull request was created.
    """
    title = b'{0!s}: {1:s}'.format(codereview_issue_number, description)
    body = (
        b'[Code review: {0!s}: {1:s}]'
        b'(https://codereview.appspot.com/{0!s}/)').format(
            codereview_issue_number, description)

    post_data = (
        b'{{\n'
        b'  "title": "{0:s}",\n'
        b'  "body": "{1:s}",\n'
        b'  "head": "{2:s}",\n'
        b'  "base": "master"\n'
        b'}}\n').format(title, body, origin)

    github_url = (
        'https://api.github.com/repos/{0:s}/{1:s}/pulls?'
        'access_token={2:s}').format(
            self._organization, self._project, access_token)

    request = urllib_request.Request(github_url)

    # This will change the request into a POST.
    request.add_data(post_data)

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed creating pull request: {0!s} with error: {1!s}'.format(
              codereview_issue_number, exception))
      return False

    if url_object.code not in (200, 201):
      logging.error(
          'Failed creating pull request: {0!s} with status code: {1:d}'.format(
              codereview_issue_number, url_object.code))
      return False

    return True

  def GetForkGitRepoUrl(self, username):
    """Retrieves the git repository URL of a fork.

    Args:
      username (str): github username of the fork.

    Returns:
      str: git repository URL or None.
    """
    return 'https://github.com/{0:s}/{1:s}.git'.format(username, self._project)

  def QueryUser(self, username):
    """Queries a github user.

    Args:
      username (str): github user name.

    Returns:
      dict[str,object]: JSON response or None.
    """
    github_url = b'https://api.github.com/users/{0:s}'.format(username)

    request = urllib_request.Request(github_url)

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed querying github user: {0:s} with error: {1!s}'.format(
              username, exception))
      return

    if url_object.code != 200:
      logging.error(
          'Failed querying github user: {0:d} with status code: {1:d}'.format(
              username, url_object.code))
      return

    response_data = url_object.read()
    return json.loads(response_data)


class ProjectHelper(CLIHelper):
  """Class that defines project helper functions.

  Attributes:
    project_name (str): name of the project.
  """

  _AUTHORS_FILE_HEADER = [
      '# Names should be added to this file with this pattern:',
      '#',
      '# For individuals:',
      '#   Name (email address)',
      '#',
      '# For organizations:',
      '#   Organization (fnmatch pattern)',
      '#',
      '# See python fnmatch module documentation for more information.',
      '',
      'Google Inc. (*@google.com)']

  SUPPORTED_PROJECTS = frozenset([
      'acstore',
      'artifacts',
      'dfdatetime',
      'dfkinds',
      'dfvfs',
      'dfwinreg',
      'dftimewolf',
      'eccemotus',
      'l2tdevtools',
      'l2tdocs',
      'l2tpreg',
      'plaso'])

  def __init__(self, script_path):
    """Initializes a project helper.

    Args:
      script_path (str): path to the script.

    Raises:
      ValueError: if the project name is not supported.
    """
    super(ProjectHelper, self).__init__()
    self.project_name = self._GetProjectName(script_path)

  @property
  def version_file_path(self):
    """str: path of the version file."""
    return os.path.join(self.project_name, '__init__.py')

  def _GetProjectName(self, script_path):
    """Retrieves the project name from the script path.

    Args:
      script_path (str): path to the script.

    Returns:
      str: project name.

    Raises:
      ValueError: if the project name is not supported.
    """
    project_name = os.path.abspath(script_path)
    project_name = os.path.dirname(project_name)
    project_name = os.path.dirname(project_name)
    project_name = os.path.basename(project_name)

    for supported_project_name in self.SUPPORTED_PROJECTS:
      if supported_project_name in project_name:
        return supported_project_name

    raise ValueError(
        'Unsupported project name: {0:s}.'.format(project_name))

  def _ReadFileContents(self, path):
    """Reads the contents of a file.

    Args:
      filename (str): path of the file.

    Returns:
      bytes: file content or None.
    """
    if not os.path.exists(path):
      logging.error('Missing file: {0:s}'.format(path))
      return

    try:
      with open(path, 'rb') as file_object:
        file_contents = file_object.read()

    except IOError as exception:
      logging.error('Unable to read file with error: {0!s}'.format(exception))
      return

    try:
      file_contents = file_contents.decode('utf-8')
    except UnicodeDecodeError as exception:
      logging.error(
          'Unable to read file with error: {0!s}'.format(exception))
      return

    return file_contents

  def GetVersion(self):
    """Retrieves the project version from the version file.

    Returns:
      str: project version or None.
    """
    version_file_contents = self._ReadFileContents(self.version_file_path)
    if not version_file_contents:
      return

    # The version is formatted as:
    # __version__ = 'VERSION'
    version_line_prefix = '__version__ = \''

    lines = version_file_contents.split('\n')
    for line in lines:
      if line.startswith(version_line_prefix):
        return line[len(version_line_prefix):-1]

    return

  def UpdateDpkgChangelogFile(self):
    """Updates the dpkg changelog file.

    Returns:
      bool: True if the dpkg changelog file was updated or if the dpkg
          changelog file does not exists.
    """
    project_version = self.GetVersion()

    dpkg_changelog_path = os.path.join('config', 'dpkg', 'changelog')
    if not os.path.exists(dpkg_changelog_path):
      return True

    dpkg_maintainter = 'Log2Timeline <log2timeline-dev@googlegroups.com>'
    dpkg_date = time.strftime('%a, %d %b %Y %H:%M:%S %z')
    dpkg_changelog_content = '\n'.join([
        '{0:s} ({1:s}-1) unstable; urgency=low'.format(
            self.project_name, project_version),
        '',
        '  * Auto-generated',
        '',
        ' -- {0:s}  {1:s}'.format(dpkg_maintainter, dpkg_date)])

    try:
      dpkg_changelog_content = dpkg_changelog_content.encode('utf-8')
    except UnicodeEncodeError as exception:
      logging.error(
          'Unable to write dpkg changelog file with error: {0!s}'.format(
              exception))
      return False

    try:
      with open(dpkg_changelog_path, 'wb') as file_object:
        file_object.write(dpkg_changelog_content)
    except IOError as exception:
      logging.error(
          'Unable to write dpkg changelog file with error: {0!s}'.format(
              exception))
      return False

    return True

  def UpdateAuthorsFile(self):
    """Updates the AUTHORS file.

    Returns:
      bool: True if the AUTHORS file update was successful.
    """
    exit_code, output, _ = self.RunCommand('git log --format="%aN (%aE)"')
    if exit_code != 0:
      return False

    lines = output.split(b'\n')

    # Reverse the lines since we want the oldest commits first.
    lines.reverse()

    authors_by_commit = []
    authors = {}
    for author in lines:
      name, _, email_address = author[:-1].rpartition('(')
      if email_address in authors:
        if name != authors[email_address]:
          logging.warning('Detected name mismatch for author: {0:d}.'.format(
              email_address))
        continue

      authors[email_address] = name
      authors_by_commit.append(author)

    file_content = []
    file_content.extend(self._AUTHORS_FILE_HEADER)
    file_content.extend(authors_by_commit)

    file_content = '\n'.join(file_content)
    file_content = file_content.encode('utf-8')

    with open('AUTHORS', 'wb') as file_object:
      file_object.write(file_content)

    return True

  def UpdateVersionFile(self):
    """Updates the version file.

    Returns:
      bool: True if the file was updated.
    """
    version_file_contents = self._ReadFileContents(self.version_file_path)
    if not version_file_contents:
      logging.error('Unable to read version file.')
      return False

    date_version = time.strftime('%Y%m%d')
    lines = version_file_contents.split('\n')
    for line_index, line in enumerate(lines):
      if line.startswith('__version__ = '):
        version_string = '__version__ = \'{0:s}\''.format(date_version)
        lines[line_index] = version_string

    version_file_contents = '\n'.join(lines)

    try:
      version_file_contents = version_file_contents.encode('utf-8')
    except UnicodeEncodeError as exception:
      logging.error(
          'Unable to write version file with error: {0!s}'.format(exception))
      return False

    try:
      with open(self.version_file_path, 'wb') as file_object:
        file_object.write(version_file_contents)

    except IOError as exception:
      logging.error(
          'Unable to write version file with error: {0!s}'.format(exception))
      return False

    return True


class PylintHelper(CLIHelper):
  """Class that defines pylint helper functions."""

  _MINIMUM_VERSION_TUPLE = (1, 5, 0)

  def CheckFiles(self, filenames):
    """Checks if the linting of the files is correct using pylint.

    Args:
      filenames (list[str]): names of the files to lint.

    Returns:
      bool: True if the files were linted without errors.
    """
    print('Running linter on changed files.')
    failed_filenames = []
    for filename in filenames:
      print('Checking: {0:s}'.format(filename))

      command = 'pylint --rcfile=.pylintrc {0:s}'.format(filename)
      exit_code = subprocess.call(command, shell=True)
      if exit_code != 0:
        failed_filenames.append(filename)

    if failed_filenames:
      print('\nFiles with linter errors:\n{0:s}\n'.format(
          '\n'.join(failed_filenames)))
      return False

    return True

  def CheckUpToDateVersion(self):
    """Checks if the pylint version is up to date.

    Returns:
      bool: True if the pylint version is up to date.
    """
    exit_code, output, _ = self.RunCommand('pylint --version')
    if exit_code != 0:
      return False

    version_tuple = (0, 0, 0)
    for line in output.split(b'\n'):
      if line.startswith(b'pylint '):
        _, _, version = line.partition(b' ')
        # Remove a trailing comma.
        version, _, _ = version.partition(b',')

        version_tuple = tuple([int(digit) for digit in version.split(b'.')])

    return version_tuple >= self._MINIMUM_VERSION_TUPLE


class ReadTheDocsHelper(object):
  """Class that defines readthedocs helper functions."""

  def __init__(self, project):
    """Initializes a readthedocs helper.

    Args:
      project (str): github project name.
    """
    super(ReadTheDocsHelper, self).__init__()
    self._project = project

  def TriggerBuild(self):
    """Triggers readthedocs to build the docs of the project.

    Returns:
      bool: True if the build was triggered.
    """
    readthedocs_url = 'https://readthedocs.org/build/{0:s}'.format(
        self._project)

    request = urllib_request.Request(readthedocs_url)

    # This will change the request into a POST.
    request.add_data(b'')

    try:
      url_object = urllib_request.urlopen(request)
    except urllib_error.HTTPError as exception:
      logging.error(
          'Failed triggering build with error: {0!s}'.format(
              exception))
      return False

    if url_object.code != 200:
      logging.error(
          'Failed triggering build with status code: {1:d}'.format(
              url_object.code))
      return False

    return True


class SphinxAPIDocHelper(CLIHelper):
  """Class that defines sphinx-apidoc helper functions."""

  _MINIMUM_VERSION_TUPLE = (1, 2, 0)

  def __init__(self, project):
    """Initializes a sphinx-apidoc helper.

    Args:
      project (str): github project name.
    """
    super(SphinxAPIDocHelper, self).__init__()
    self._project = project

  def CheckUpToDateVersion(self):
    """Checks if the sphinx-apidoc version is up to date.

    Returns:
      bool: True if the sphinx-apidoc version is up to date.
    """
    exit_code, output, _ = self.RunCommand('sphinx-apidoc --version')
    if exit_code != 0:
      return False

    version_tuple = (0, 0, 0)
    for line in output.split(b'\n'):
      if line.startswith(b'Sphinx (sphinx-apidoc) '):
        _, _, version = line.rpartition(b' ')

        version_tuple = tuple([int(digit) for digit in version.split(b'.')])

    return version_tuple >= self._MINIMUM_VERSION_TUPLE

  def UpdateAPIDocs(self):
    """Updates the API docs.

    Returns:
      bool: True if the API docs have been updated.
    """
    command = 'sphinx-apidoc -f -o docs {0:s}'.format(self._project)
    exit_code, output, _ = self.RunCommand(command)
    print(output)

    return exit_code == 0


class NetRCFile(object):
  """Class that defines a .netrc file."""

  _NETRC_SEPARATOR_RE = re.compile(r'[^ \t\n]+')

  def __init__(self):
    """Initializes a .netrc file."""
    super(NetRCFile, self).__init__()
    self._contents = None
    self._values = None

    home_path = os.path.expanduser('~')
    self._path = os.path.join(home_path, '.netrc')
    if not os.path.exists(self._path):
      return

    with open(self._path, 'r') as file_object:
      self._contents = file_object.read()

  def _GetGitHubValues(self):
    """Retrieves the github values.

    Returns:
      list[str]: .netrc values for github.com or None.
    """
    if not self._contents:
      return

    # Note that according to GNU's manual on .netrc file, the credential
    # tokens "may be separated by spaces, tabs, or new-lines".
    if not self._values:
      self._values = self._NETRC_SEPARATOR_RE.findall(self._contents)

    for value_index, value in enumerate(self._values):
      if value == 'github.com' and self._values[value_index - 1] == 'machine':
        return self._values[value_index + 1:]

  def GetGitHubAccessToken(self):
    """Retrieves the github access token.

    Returns:
      str: github access token or None.
    """
    values = self._GetGitHubValues()
    if not values:
      return

    for value_index, value in enumerate(values):
      if value == 'password':
        return values[value_index + 1]

  def GetGitHubUsername(self):
    """Retrieves the github username.

    Returns:
      str: github username or None.
    """
    values = self._GetGitHubValues()
    if not values:
      return

    login_value = None
    for value_index, value in enumerate(values):
      if value == 'login':
        login_value = values[value_index + 1]

      # If the next field is 'password' we assume the login field is empty.
      if login_value != 'password':
        return login_value


class ReviewFile(object):
  """Class that defines a review file.

  A review file is use to track code review relevant information like the
  codereview issue number. It is stored in the .review subdirectory and
  named after the feature branch e.g. ".review/feature".
  """

  def __init__(self, branch_name):
    """Initializes a review file.

    Args:
      branch_name (str): name of the feature branch of the review.
    """
    super(ReviewFile, self).__init__()
    self._contents = None
    self._path = os.path.join('.review', branch_name)

    if os.path.exists(self._path):
      with open(self._path, 'r') as file_object:
        self._contents = file_object.read()

  def Create(self, codereview_issue_number):
    """Creates a new review file.

    If the .review directory does not exist, it will be created.

    Args:
      codereview_issue_number (int|str): codereview issue number.

    Returns:
      bool: True if the review file was created.
    """
    if not os.path.exists('.review'):
      os.mkdir('.review')
    with open(self._path, 'w') as file_object:
      file_object.write('{0!s}'.format(codereview_issue_number))

  def Exists(self):
    """Determines if the review file exists.

    Returns:
      bool: True if review file exists.
    """
    return os.path.exists(self._path)

  def GetCodeReviewIssueNumber(self):
    """Retrieves the codereview issue number.

    Returns:
      int: codereview issue number.
    """
    if not self._contents:
      return

    try:
      return int(self._contents, 10)
    except ValueError:
      pass

  def Remove(self):
    """Removes the review file."""
    if not os.path.exists(self._path):
      return

    os.remove(self._path)


class ReviewHelper(object):
  """Class that defines review helper functions."""

  _PROJECT_NAME_PREFIX_REGEX = re.compile(
      r'\[({0:s})\] '.format('|'.join(ProjectHelper.SUPPORTED_PROJECTS)))

  def __init__(
      self, command, github_origin, feature_branch, diffbase, all_files=False,
      no_browser=False, no_confirm=False):
    """Initializes a review helper.

    Args:
      command (str): user provided command, for example "create", "lint".
      github_origin (str): github origin.
      feature_branch (str): feature branch.
      diffbase (str): diffbase.
      all_files (Optional[bool]): True if the command should apply to all
          files. Currently this only affects the lint command.
      no_browser (Optional[bool]): True if the functionality to use the
          webbrowser to get the OAuth token should be disabled.
      no_confirm (Optional[bool]): True if the defaults should be applied
          without confirmation.
    """
    super(ReviewHelper, self).__init__()
    self._active_branch = None
    self._all_files = all_files
    self._codereview_helper = None
    self._command = command
    self._diffbase = diffbase
    self._feature_branch = feature_branch
    self._git_helper = None
    self._git_repo_url = None
    self._github_helper = None
    self._github_origin = github_origin
    self._fork_feature_branch = None
    self._fork_username = None
    self._merge_author = None
    self._merge_description = None
    self._no_browser = no_browser
    self._no_confirm = no_confirm
    self._project_helper = None
    self._project_name = None
    self._sphinxapidoc_helper = None

    if self._github_origin:
      self._fork_username, _, self._fork_feature_branch = (
          self._github_origin.partition(':'))

  def CheckLocalGitState(self):
    """Checks the state of the local git repository.

    Returns:
      bool: True if the state of the local git repository is sane.
    """
    if self._command in (
        'close', 'create', 'lint', 'lint-test', 'lint_test', 'update'):
      if not self._git_helper.CheckHasProjectUpstream():
        print('{0:s} aborted - missing project upstream.'.format(
            self._command.title()))
        print('Run: git remote add upstream {0:s}'.format(self._git_repo_url))
        return False

    elif self._command == 'merge':
      if not self._git_helper.CheckHasProjectOrigin():
        print('{0:s} aborted - missing project origin.'.format(
            self._command.title()))
        return False

    if self._command not in (
        'lint', 'lint-test', 'lint_test', 'test', 'update-version',
        'update_version'):
      if self._git_helper.CheckHasUncommittedChanges():
        print('{0:s} aborted - detected uncommitted changes.'.format(
            self._command.title()))
        print('Run: git commit')
        return False

    self._active_branch = self._git_helper.GetActiveBranch()
    if self._command in ('create', 'update'):
      if self._active_branch == 'master':
        print('{0:s} aborted - active branch is master.'.format(
            self._command.title()))
        return False

    elif self._command == 'close':
      if self._feature_branch == 'master':
        print('{0:s} aborted - feature branch cannot be master.'.format(
            self._command.title()))
        return False

      if self._active_branch != 'master':
        self._git_helper.SwitchToMasterBranch()
        self._active_branch = 'master'

    return True

  def CheckRemoteGitState(self):
    """Checks the state of the remote git repository.

    Returns:
      bool: True if the state of the remote git repository is sane.
    """
    if self._command == 'close':
      if not self._git_helper.SynchronizeWithUpstream():
        print((
            '{0:s} aborted - unable to synchronize with '
            'upstream/master.').format(self._command.title()))
        return False

    elif self._command in ('create', 'update'):
      if not self._git_helper.CheckSynchronizedWithUpstream():
        if not self._git_helper.SynchronizeWithUpstream():
          print((
              '{0:s} aborted - unable to synchronize with '
              'upstream/master.').format(self._command.title()))
          return False

        force_push = True
      else:
        force_push = False

      if not self._git_helper.PushToOrigin(
          self._active_branch, force=force_push):
        print('{0:s} aborted - unable to push updates to origin/{1:s}.'.format(
            self._command.title(), self._active_branch))
        return False

    elif self._command in ('lint', 'lint-test', 'lint_test'):
      self._git_helper.CheckSynchronizedWithUpstream()

    elif self._command == 'merge':
      if not self._git_helper.SynchronizeWithOrigin():
        print((
            '{0:s} aborted - unable to synchronize with '
            'origin/master.').format(self._command.title()))
        return False

    return True

  def Close(self):
    """Closes a review.

    Returns:
      bool: True if the close was successful.
    """
    if not self._git_helper.CheckHasBranch(self._feature_branch):
      print('No such feature branch: {0:s}'.format(self._feature_branch))
    else:
      self._git_helper.RemoveFeatureBranch(self._feature_branch)

    review_file = ReviewFile(self._feature_branch)
    if not review_file.Exists():
      print('Review file missing for branch: {0:s}'.format(
          self._feature_branch))

    else:
      codereview_issue_number = review_file.GetCodeReviewIssueNumber()

      review_file.Remove()

      if codereview_issue_number:
        if not self._codereview_helper.CloseIssue(codereview_issue_number):
          print('Unable to close code review: {0!s}'.format(
              codereview_issue_number))
          print((
              'Close it manually on: https://codereview.appspot.com/'
              '{0!s}').format(codereview_issue_number))

    return True

  def Create(self):
    """Creates a review.

    Returns:
      bool: True if the create was successful.
    """
    review_file = ReviewFile(self._active_branch)
    if review_file.Exists():
      print('Review file already exists for branch: {0:s}'.format(
          self._active_branch))
      return False

    git_origin = self._git_helper.GetRemoteOrigin()
    if not git_origin.startswith('https://github.com/'):
      print('{0:s} aborted - unsupported git remote origin: {1:s}'.format(
          self._command.title(), git_origin))
      print('Make sure the git remote origin is hosted on github.com')
      return False

    git_origin, _, _ = git_origin[len('https://github.com/'):].rpartition('/')

    netrc_file = NetRCFile()
    github_access_token = netrc_file.GetGitHubAccessToken()
    if not github_access_token:
      print('{0:s} aborted - unable to determine github access token.'.format(
          self._command.title()))
      print('Make sure .netrc is configured with a github access token.')
      return False

    last_commit_message = self._git_helper.GetLastCommitMessage()
    print('Automatic generated description of code review:')
    print(last_commit_message)
    print('')

    if self._no_confirm:
      user_input = None
    else:
      print('Enter a description for the code review or hit enter to use the')
      print('automatic generated one:')
      user_input = sys.stdin.readline()
      user_input = user_input.strip()

    if not user_input:
      description = last_commit_message
    else:
      description = user_input

    # Prefix the description with the project name for code review to make it
    # easier to distinguish between projects.
    code_review_description = '[{0:s}] {1:s}'.format(
        self._project_name, description)

    codereview_issue_number = self._codereview_helper.CreateIssue(
        self._project_name, self._diffbase, code_review_description)
    if not codereview_issue_number:
      print('{0:s} aborted - unable to create codereview issue.'.format(
          self._command.title()))
      return False

    if not os.path.isdir('.review'):
      os.mkdir('.review')

    review_file.Create(codereview_issue_number)

    create_github_origin = '{0:s}:{1:s}'.format(
        git_origin, self._active_branch)
    if not self._github_helper.CreatePullRequest(
        github_access_token, codereview_issue_number, create_github_origin,
        description):
      print('Unable to create pull request.')

    return True

  def InitializeHelpers(self):
    """Initializes the helper.

    Returns:
      bool: True if the helper initialization was successful.
    """
    script_path = os.path.abspath(__file__)

    self._project_helper = ProjectHelper(script_path)

    self._project_name = self._project_helper.project_name
    if not self._project_name:
      print('{0:s} aborted - unable to determine project name.'.format(
          self._command.title()))
      return False

    self._git_repo_url = b'https://github.com/log2timeline/{0:s}.git'.format(
        self._project_name)

    self._git_helper = GitHelper(self._git_repo_url)

    self._github_helper = GitHubHelper('log2timeline', self._project_name)

    if self._command in ('close', 'create', 'merge', 'update'):
      email_address = self._git_helper.GetEmailAddress()
      self._codereview_helper = CodeReviewHelper(
          email_address, no_browser=self._no_browser)

    if self._command == 'merge':
      self._sphinxapidoc_helper = SphinxAPIDocHelper(
          self._project_name)
      # TODO: disable the version check for now since sphinx-apidoc 1.2.2
      # on Unbuntu 14.04 does not have the --version option. Re-enable when
      # sphinx-apidoc 1.2.3 or later is introduced.
      # if not self._sphinxapidoc_helper.CheckUpToDateVersion():
      #   print((
      #       '{0:s} aborted - sphinx-apidoc verion 1.2.0 or later '
      #       'required.').format(self._command.title()))
      #   return False

    return True

  def Lint(self):
    """Lints a review.

    Returns:
      bool: True if linting was successful.
    """
    if self._project_name == 'l2tdocs':
      return True

    if self._command not in (
        'create', 'merge', 'lint', 'lint-test', 'lint_test', 'update'):
      return True

    pylint_helper = PylintHelper()
    if not pylint_helper.CheckUpToDateVersion():
      print('{0:s} aborted - pylint verion 1.5.0 or later required.'.format(
          self._command.title()))
      return False

    if self._all_files:
      diffbase = None
    elif self._command == 'merge':
      diffbase = 'origin/master'
    else:
      diffbase = self._diffbase

    changed_python_files = self._git_helper.GetChangedPythonFiles(
        diffbase=diffbase)

    if not pylint_helper.CheckFiles(changed_python_files):
      print('{0:s} aborted - unable to pass linter.'.format(
          self._command.title()))

      if self._command == 'merge':
        self._git_helper.DropUncommittedChanges()
      return False

    return True

  def Merge(self, codereview_issue_number):
    """Merges a review.

    Args:
      codereview_issue_number (int|str): codereview issue number.

    Returns:
      bool: True if the merge was successful.
    """
    if not self._project_helper.UpdateVersionFile():
      print('Unable to update version file.')
      self._git_helper.DropUncommittedChanges()
      return False

    if not self._project_helper.UpdateDpkgChangelogFile():
      print('Unable to update dpkg changelog file.')
      self._git_helper.DropUncommittedChanges()
      return False

    apidoc_config_path = os.path.join('docs', 'conf.py')
    if os.path.exists(apidoc_config_path):
      self._sphinxapidoc_helper.UpdateAPIDocs()
      self._git_helper.AddPath('docs')

      readthedocs_helper = ReadTheDocsHelper(self._project_name)

      # The project wiki repo contains the documentation and
      # has no trigger on update webhook for readthedocs.
      # So we trigger readthedocs directly to build the docs.
      readthedocs_helper.TriggerBuild()

    if not self._git_helper.CommitToOriginInNameOf(
        codereview_issue_number, self._merge_author, self._merge_description):
      print('Unable to commit changes.')
      self._git_helper.DropUncommittedChanges()
      return False

    commit_message = (
        'Changes have been merged with master branch. '
        'To close the review and clean up the feature branch you can run: '
        'python ./utils/review.py close {0:s}').format(
            self._fork_feature_branch)
    self._codereview_helper.AddMergeMessage(
        codereview_issue_number, commit_message)

    return True

  def Open(self, codereview_issue_number):
    """Opens a review.

    Args:
      codereview_issue_number (int|str): codereview issue number.

    Returns:
      bool: True if the open was successful.
    """
    # TODO: implement.
    # * check if feature branch exists
    # * check if review file exists
    # * check if issue number corresponds to branch by checking PR?
    # * create feature branch and pull changes from origin
    # * create review file
    _ = codereview_issue_number

    return False

  def PrepareMerge(self, codereview_issue_number):
    """Prepares a merge.

    Args:
      codereview_issue_number (int|str): codereview issue number.

    Returns:
      bool: True if the prepare were successful.
    """
    codereview_information = self._codereview_helper.QueryIssue(
        codereview_issue_number)
    if not codereview_information:
      print((
          '{0:s} aborted - unable to retrieve code review: {1!s} '
          'information.').format(
              self._command.title(), codereview_issue_number))
      return False

    self._merge_description = codereview_information.get('subject', None)
    if not self._merge_description:
      print((
          '{0:s} aborted - unable to determine description of code review: '
          '{1!s}.').format(
              self._command.title(), codereview_issue_number))
      return False

    # When merging remove the project name ("[project]") prefix from
    # the code review description.
    self._merge_description = self._PROJECT_NAME_PREFIX_REGEX.sub(
        '', self._merge_description)

    merge_email_address = codereview_information.get('owner_email', None)
    if not merge_email_address:
      print((
          '{0:s} aborted - unable to determine email address of owner of '
          'code review: {1!s}.').format(
              self._command.title(), codereview_issue_number))
      return False

    github_user_information = self._github_helper.QueryUser(
        self._fork_username)
    if not github_user_information:
      print((
          '{0:s} aborted - unable to retrieve github user: {1:s} '
          'information.').format(
              self._command.title(), self._fork_username))
      return False

    merge_fullname = github_user_information.get('name', None)
    if not merge_fullname:
      merge_fullname = codereview_information.get('owner', None)
    if not merge_fullname:
      merge_fullname = github_user_information.get('company', None)
    if not merge_fullname:
      print((
          '{0:s} aborted - unable to determine full name.').format(
              self._command.title()))
      return False

    self._merge_author = '{0:s} <{1:s}>'.format(
        merge_fullname, merge_email_address)

    return True

  def PullChangesFromFork(self):
    """Pulls changes from a feature branch on a fork.

    Returns:
      bool: True if the pull was successful.
    """
    fork_git_repo_url = self._github_helper.GetForkGitRepoUrl(
        self._fork_username)

    if not self._git_helper.PullFromFork(
        fork_git_repo_url, self._fork_feature_branch):
      print('{0:s} aborted - unable to pull changes from fork.'.format(
          self._command.title()))
      return False

    return True

  def Test(self):
    """Tests a review.

    Returns:
      bool: True if the tests were successful.
    """
    if self._project_name == 'l2tdocs':
      return True

    if self._command not in (
        'create', 'lint-test', 'lint_test', 'merge', 'test', 'update'):
      return True

    # TODO: determine why this alters the behavior of argparse.
    # Currently affects this script being used in plaso.
    command = '{0:s} run_tests.py'.format(sys.executable)
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      print('{0:s} aborted - unable to pass tests.'.format(
          self._command.title()))

      if self._command == 'merge':
        self._git_helper.DropUncommittedChanges()
      return False

    return True

  def Update(self):
    """Updates a review.

    Returns:
      bool: True if the update was successful.
    """
    review_file = ReviewFile(self._active_branch)
    if not review_file.Exists():
      print('Review file missing for branch: {0:s}'.format(
          self._active_branch))
      return False

    codereview_issue_number = review_file.GetCodeReviewIssueNumber()

    last_commit_message = self._git_helper.GetLastCommitMessage()
    print('Automatic generated description of the update:')
    print(last_commit_message)
    print('')

    if self._no_confirm:
      user_input = None
    else:
      print('Enter a description for the update or hit enter to use the')
      print('automatic generated one:')
      user_input = sys.stdin.readline()
      user_input = user_input.strip()

    if not user_input:
      description = last_commit_message
    else:
      description = user_input

    if not self._codereview_helper.UpdateIssue(
        codereview_issue_number, self._diffbase, description):
      print('Unable to update code review: {0!s}'.format(
          codereview_issue_number))
      return False

    return True

  def UpdateAuthors(self):
    """Updates the authors.

    Returns:
      bool: True if the authors update was successful.
    """
    if self._project_name == 'l2tdocs':
      return True

    if not self._project_helper.UpdateAuthorsFile():
      print('Unable to update authors file.')
      return False

    return True

  def UpdateVersion(self):
    """Updates the version.

    Returns:
      bool: True if the version update was successful.
    """
    if self._project_name == 'l2tdocs':
      return True

    if not self._project_helper.UpdateVersionFile():
      print('Unable to update version file.')
      return False

    if not self._project_helper.UpdateDpkgChangelogFile():
      print('Unable to update dpkg changelog file.')
      return False

    return True


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description='Script to manage code reviews.')

  # TODO: add option to directly pass code review issue number.

  argument_parser.add_argument(
      '--allfiles', '--all-files', '--all_files', dest='all_files',
      action='store_true', default=False, help=(
          'Apply command to all files, currently only affects the lint '
          'command.'))

  argument_parser.add_argument(
      '--diffbase', dest='diffbase', action='store', type=str,
      metavar='DIFFBASE', default='upstream/master', help=(
          'The diffbase the default is upstream/master. This options is used '
          'to indicate to what "base" the code changes are relative to and '
          'can be used to "chain" code reviews.'))

  argument_parser.add_argument(
      '--nobrowser', '--no-browser', '--no_browser', dest='no_browser',
      action='store_true', default=False, help=(
          'Disable the functionality to use the webbrowser to get the OAuth '
          'token should be disabled.'))

  argument_parser.add_argument(
      '--noconfirm', '--no-confirm', '--no_confirm', dest='no_confirm',
      action='store_true', default=False, help=(
          'Do not ask for confirmation apply defaults.\n'
          'WARNING: only use this when you are familiar with the defaults.'))

  argument_parser.add_argument(
      '--offline', dest='offline', action='store_true', default=False, help=(
          'The review script is running offline and any online check is '
          'skipped.'))

  commands_parser = argument_parser.add_subparsers(dest='command')

  close_command_parser = commands_parser.add_parser('close')

  # TODO: add this to help output.
  close_command_parser.add_argument(
      'branch', action='store', metavar='BRANCH', default=None,
      help='name of the corresponding feature branch.')

  commands_parser.add_parser('create')

  merge_command_parser = commands_parser.add_parser('merge')

  # TODO: add this to help output.
  merge_command_parser.add_argument(
      'codereview_issue_number', action='store',
      metavar='CODEREVIEW_ISSUE_NUMBER', default=None,
      help='the codereview issue number to be merged.')

  # TODO: add this to help output.
  merge_command_parser.add_argument(
      'github_origin', action='store',
      metavar='GITHUB_ORIGIN', default=None,
      help='the github origin to merged e.g. username:feature.')

  merge_edit_command_parser = commands_parser.add_parser('merge-edit')

  # TODO: add this to help output.
  merge_edit_command_parser.add_argument(
      'github_origin', action='store',
      metavar='GITHUB_ORIGIN', default=None,
      help='the github origin to merged e.g. username:feature.')

  merge_edit_command_parser = commands_parser.add_parser('merge_edit')

  # TODO: add this to help output.
  merge_edit_command_parser.add_argument(
      'github_origin', action='store',
      metavar='GITHUB_ORIGIN', default=None,
      help='the github origin to merged e.g. username:feature.')

  commands_parser.add_parser('lint')

  commands_parser.add_parser('lint-test')
  commands_parser.add_parser('lint_test')

  open_command_parser = commands_parser.add_parser('open')

  # TODO: add this to help output.
  open_command_parser.add_argument(
      'codereview_issue_number', action='store',
      metavar='CODEREVIEW_ISSUE_NUMBER', default=None,
      help='the codereview issue number to be opened.')

  # TODO: add this to help output.
  open_command_parser.add_argument(
      'branch', action='store', metavar='BRANCH', default=None,
      help='name of the corresponding feature branch.')

  # TODO: add submit option?

  commands_parser.add_parser('test')

  # TODO: add dry-run option to run merge without commit.
  # useful to test pending CLs.

  commands_parser.add_parser('update')

  commands_parser.add_parser('update-authors')
  commands_parser.add_parser('update_authors')

  commands_parser.add_parser('update-version')
  commands_parser.add_parser('update_version')

  options = argument_parser.parse_args()

  codereview_issue_number = None
  feature_branch = None
  github_origin = None

  print_help_on_error = False
  if options.command in ('close', 'open'):
    feature_branch = getattr(options, 'branch', None)
    if not feature_branch:
      print('Feature branch value is missing.')
      print_help_on_error = True

      # Support "username:branch" notation.
      if ':' in feature_branch:
        _, _, feature_branch = feature_branch.rpartition(':')

  if options.command in ('merge', 'open'):
    codereview_issue_number = getattr(
        options, 'codereview_issue_number', None)
    if not codereview_issue_number:
      print('Codereview issue number value is missing.')
      print_help_on_error = True

  if options.command in ('merge', 'merge-edit', 'merge_edit'):
    github_origin = getattr(options, 'github_origin', None)
    if not github_origin:
      print('Github origin value is missing.')
      print_help_on_error = True

  if options.offline and options.command not in (
      'lint', 'lint-test', 'lint_test', 'test'):
    print('Cannot run: {0:s} in offline mode.'.format(options.command))
    print_help_on_error = True

  if print_help_on_error:
    print('')
    argument_parser.print_help()
    print('')
    return False

  home_path = os.path.expanduser('~')
  netrc_path = os.path.join(home_path, '.netrc')
  if not os.path.exists(netrc_path):
    print('{0:s} aborted - unable to find .netrc.'.format(
        options.command.title()))
    return False

  review_helper = ReviewHelper(
      options.command, github_origin, feature_branch,
      options.diffbase, all_files=options.all_files,
      no_browser=options.no_browser, no_confirm=options.no_confirm)

  if not review_helper.InitializeHelpers():
    return False

  if not review_helper.CheckLocalGitState():
    return False

  if not options.offline and not review_helper.CheckRemoteGitState():
    return False

  if options.command == 'merge':
    if not review_helper.PrepareMerge(codereview_issue_number):
      return False

  if options.command in ('merge', 'merge-edit', 'merge_edit'):
    if not review_helper.PullChangesFromFork():
      return False

  if not review_helper.Lint():
    return False

  if not review_helper.Test():
    return False

  result = False
  if options.command == 'create':
    result = review_helper.Create()

  elif options.command == 'close':
    result = review_helper.Close()

  elif options.command in ('lint', 'lint-test', 'lint_test', 'test'):
    result = True

  elif options.command == 'merge':
    result = review_helper.Merge(codereview_issue_number)

  elif options.command == 'open':
    result = review_helper.Open(codereview_issue_number)

  elif options.command == 'update':
    result = review_helper.Update()

  elif options.command in ('update-authors', 'update_authors'):
    result = review_helper.UpdateAuthors()

  elif options.command in ('update-version', 'update_version'):
    result = review_helper.UpdateVersion()

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
