#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""End-to-end test launcher."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import configparser
import difflib
import logging
import os
import shutil
import subprocess
import sys
import tempfile


# Since os.path.abspath() uses the current working directory (cwd)
# os.path.abspath(__file__) will point to a different location if
# cwd has been changed. Hence we preserve the absolute location of __file__.
__file__ = os.path.abspath(__file__)


class TempDirectory(object):
  """Temporary directory."""

  def __init__(self):
    """Initializes a temporary directory."""
    super(TempDirectory, self).__init__()
    self.name = ''

  def __enter__(self):
    """Make this work with the 'with' statement."""
    self.name = tempfile.mkdtemp()
    return self.name

  def __exit__(self, unused_type, unused_value, unused_traceback):
    """Make this work with the 'with' statement."""
    shutil.rmtree(self.name, True)


class TestCase(object):
  """Test case interface.

  The test case defines what aspect of dfvfs example scripts to test. A test
  definition is used to provide parameters for the test case so it can be
  easily run on different input files.
  """

  # pylint: disable=redundant-returns-doc

  NAME = None

  def __init__(
      self, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Initializes a test case.

    Args:
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.
    """
    super(TestCase, self).__init__()
    self._debug_output = debug_output
    self._scripts_path = scripts_path
    self._test_references_path = test_references_path
    self._test_results_path = test_results_path
    self._test_sources_path = test_sources_path

  def _RunCommand(self, command, stdout=None, stderr=None):
    """Runs a command.

    Args:
      command (list[str]): full command to run, as expected by the Popen()
        constructor (see the documentation:
        https://docs.python.org/2/library/subprocess.html#popen-constructor)
      stdout (Optional[str]): path to file to send stdout to.
      stderr (Optional[str]): path to file to send stderr to.

    Returns:
      bool: True if the command ran successfully.
    """
    if command[0].endswith('py'):
      command.insert(0, sys.executable)
    logging.info('Running: {0:s}'.format(' '.join(command)))
    child = subprocess.Popen(command, stdout=stdout, stderr=stderr)
    child.communicate()
    exit_code = child.returncode

    if exit_code != 0:
      logging.error('Running: "{0:s}" failed (exit code {1:d}).'.format(
          command, exit_code))
      return False

    return True

  @abc.abstractmethod
  def ReadAttributes(self, test_definition_reader, test_definition):
    """Reads the test definition attributes into to the test definition.

    Args:
      test_definition_reader (TestDefinitionReader): test definition reader.
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the read was successful.
    """

  @abc.abstractmethod
  def Run(self, test_definition):
    """Runs the test case with the parameters specified by the test definition.

    Args:
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the test ran successfully.
    """


class TestCasesManager(object):
  """Test cases manager."""

  _test_case_classes = {}
  _test_case_objects = {}

  @classmethod
  def DeregisterTestCase(cls, test_case_class):
    """Deregisters a test case class.

    The test case classes are identified based on their lower case name.

    Args:
      test_case_class (type): test case class.

    Raises:
      KeyError: if test case class is not set for the corresponding name.
    """
    test_case_name = test_case_class.NAME.lower()
    if test_case_name not in cls._test_case_classes:
      raise KeyError(
          'Formatter class not set for name: {0:s}.'.format(
              test_case_class.NAME))

    del cls._test_case_classes[test_case_name]

  @classmethod
  def GetTestCaseObject(
      cls, name, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Retrieves the test case object for a specific name.

    Args:
      name (str): name of the test case.
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.

    Returns:
      TestCase: test case or None if not available.
    """
    name = name.lower()
    if name not in cls._test_case_objects:
      test_case_object = None

      if name in cls._test_case_classes:
        test_case_class = cls._test_case_classes[name]
        test_case_object = test_case_class(
            scripts_path, test_sources_path, test_references_path,
            test_results_path, debug_output=debug_output)

      if not test_case_object:
        return None

      cls._test_case_objects[name] = test_case_object

    return cls._test_case_objects[name]

  @classmethod
  def RegisterTestCase(cls, test_case_class):
    """Registers a test case class.

    The test case classes are identified based on their lower case name.

    Args:
      test_case_class (type): test case class.

    Raises:
      KeyError: if test case class is already set for the corresponding
          name.
    """
    test_case_name = test_case_class.NAME.lower()
    if test_case_name in cls._test_case_classes:
      raise KeyError((
          'Formatter class already set for name: {0:s}.').format(
              test_case_class.NAME))

    cls._test_case_classes[test_case_name] = test_case_class

  @classmethod
  def RegisterTestCases(cls, test_case_classes):
    """Registers test case classes.

    The test case classes are identified based on their lower case name.

    Args:
      test_case_classes (list[type]): test case classes.

    Raises:
      KeyError: if test case class is already set for the corresponding
          name.
    """
    for test_case_class in test_case_classes:
      cls.RegisterTestCase(test_case_class)


class TestDefinition(object):
  """Test definition.

  Attributes:
    case (str): name of test case.
    name (str): name of the test.
  """

  def __init__(self, name):
    """Initializes a test definition.

    Args:
      name (str): name of the test.
    """
    super(TestDefinition, self).__init__()
    self.case = ''
    self.name = name


class TestDefinitionReader(object):
  """Test definition reader.

  The test definition reader reads tests definitions from a configuration
  file.
  """

  def __init__(
      self, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Initializes a test definition reader.

    Args:
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.
    """
    super(TestDefinitionReader, self).__init__()
    self._config_parser = None
    self._debug_output = debug_output
    self._scripts_path = scripts_path
    self._test_references_path = test_references_path
    self._test_results_path = test_results_path
    self._test_sources_path = test_sources_path

  def GetConfigValue(
      self, section_name, value_name, default=None, split_string=False):
    """Retrieves a value from the config parser.

    Args:
      section_name (str): name of the section that contains the value.
      value_name (str): the name of the value.
      default (Optional[object]): default value to return if no value is set
          in the config parser.
      split_string (Optional[bool]): if True, the value will be split into a
          list of strings, suitable for passing to subprocess.Popen().

    Returns:
      object: value or the default if the value does not exist.

    Raises:
      RuntimeError: if the configuration parser is not set.
    """
    if not self._config_parser:
      raise RuntimeError('Missing configuration parser.')

    try:
      value = self._config_parser.get(section_name, value_name)
    except configparser.NoOptionError:
      value = None

    if isinstance(value, bytes):
      value = value.decode('utf-8')

    if split_string and value:
      options = []
      for flag_and_setting in value.split(' '):
        if flag_and_setting.find('=') > 0:
          options.extend(flag_and_setting.split('='))
        else:
          options.append(flag_and_setting)
      value = options

    if value is None:
      value = default

    return value

  def Read(self, file_object):
    """Reads test definitions.

    Args:
      file_object (file): a file-like object to read from.

    Yields:
      TestDefinition: end-to-end test definition.
    """
    self._config_parser = configparser.ConfigParser(interpolation=None)

    try:
      self._config_parser.read_file(file_object)

      for section_name in self._config_parser.sections():
        test_definition = TestDefinition(section_name)

        test_definition.case = self.GetConfigValue(section_name, 'case')
        if not test_definition.case:
          logging.warning(
              'Test case missing in test definition: {0:s}.'.format(
                  section_name))
          continue

        test_case = TestCasesManager.GetTestCaseObject(
            test_definition.case, self._scripts_path, self._test_sources_path,
            self._test_references_path, self._test_results_path,
            debug_output=self._debug_output)
        if not test_case:
          logging.warning('Undefined test case: {0:s}'.format(
              test_definition.case))
          continue

        if not test_case.ReadAttributes(self, test_definition):
          logging.warning(
              'Unable to read attributes of test case: {0:s}'.format(
                  test_definition.case))
          continue

        yield test_definition

    finally:
      self._config_parser = None


class TestLauncher(object):
  """Test launcher.

  The test launcher reads the test definitions from a file, looks up
  the corresponding test cases in the test case manager and then runs
  the test case with the parameters specified in the test definition.
  """

  def __init__(
      self, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Initializes a test launcher.

    Args:
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.
    """
    super(TestLauncher, self).__init__()
    self._debug_output = debug_output
    self._scripts_path = scripts_path
    self._test_definitions = []
    self._test_references_path = test_references_path
    self._test_results_path = test_results_path
    self._test_sources_path = test_sources_path

  def _RunTest(self, test_definition):
    """Runs the test.

    Args:
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the test ran successfully.
    """
    test_case = TestCasesManager.GetTestCaseObject(
        test_definition.case, self._scripts_path, self._test_sources_path,
        self._test_references_path, self._test_results_path)
    if not test_case:
      logging.error('Unsupported test case: {0:s}'.format(
          test_definition.case))
      return False

    return test_case.Run(test_definition)

  def ReadDefinitions(self, configuration_file):
    """Reads the test definitions from the configuration file.

    Args:
      configuration_file (str): path of the configuration file.
    """
    self._test_definitions = []
    with open(configuration_file) as file_object:
      test_definition_reader = TestDefinitionReader(
          self._scripts_path, self._test_sources_path,
          self._test_references_path, self._test_results_path)
      for test_definition in test_definition_reader.Read(file_object):
        self._test_definitions.append(test_definition)

  def RunTests(self):
    """Runs the tests.

    Returns:
      list[str]: names of the failed tests.
    """
    # TODO: set up test environment

    failed_tests = []
    for test_definition in self._test_definitions:
      if not self._RunTest(test_definition):
        failed_tests.append(test_definition.name)

    return failed_tests


class ExampleScriptTestCase(TestCase):
  """Common functionality for example script-based test cases."""

  # pylint: disable=redundant-returns-doc

  def _CompareOutputFile(self, test_definition, temp_directory):
    """Compares the output file with a reference output file.

    Args:
      test_definition (TestDefinition): test definition.
      temp_directory (str): name of a temporary directory.

    Returns:
      bool: True if he output files are identical.
    """
    output_file_path = os.path.join(temp_directory, test_definition.output_file)

    result = False
    if test_definition.reference_output_file:
      reference_output_file_path = test_definition.reference_output_file
      if self._test_references_path:
        reference_output_file_path = os.path.join(
            self._test_references_path, reference_output_file_path)

      if not os.path.exists(reference_output_file_path):
        logging.error('No such reference output file: {0:s}'.format(
            reference_output_file_path))
        return False

      with open(reference_output_file_path, 'r') as reference_output_file:
        with open(output_file_path, 'r') as output_file:
          reference_output_list = reference_output_file.readlines()
          output_list = output_file.readlines()
          differences = list(difflib.unified_diff(
              reference_output_list, output_list,
              fromfile=reference_output_file_path, tofile=output_file_path))

      if differences:
        differences_output = []
        for difference in differences:
          differences_output.append(difference)
        differences_output = '\n'.join(differences_output)
        logging.error('Differences: {0:s}'.format(differences_output))

      if not differences:
        result = True

    return result

  def ReadAttributes(self, test_definition_reader, test_definition):
    """Reads the test definition attributes into to the test definition.

    Args:
      test_definition_reader (TestDefinitionReader): test definition reader.
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the read was successful.
    """
    test_definition.output_file = test_definition_reader.GetConfigValue(
        test_definition.name, 'output_file')

    test_definition.reference_output_file = (
        test_definition_reader.GetConfigValue(
            test_definition.name, 'reference_output_file'))

    test_definition.source = test_definition_reader.GetConfigValue(
        test_definition.name, 'source')

    return True

  @abc.abstractmethod
  def Run(self, test_definition):
    """Runs the test case with the parameters specified by the test definition.

    Args:
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the test ran successfully.
    """


class ListFileEntriesTestCase(ExampleScriptTestCase):
  """List file entries test case.

  The list file entries test case runs the list_file_entries.py example script
  on a storage media image, specified by the test definition.
  """

  NAME = 'list_file_entries'

  def __init__(
      self, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Initializes a test case.

    Args:
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.
    """
    super(ListFileEntriesTestCase, self).__init__(
        scripts_path, test_sources_path, test_references_path,
        test_results_path, debug_output=debug_output)
    self._list_file_entries_path = None
    self._InitializeListFileEntriesPath()

  def _InitializeListFileEntriesPath(self):
    """Initializes the location of list_file_entries.py."""
    for filename in (
        'list_file_entries.exe', 'list_file_entries.sh',
        'list_file_entries.py'):
      self._list_file_entries_path = os.path.join(self._scripts_path, filename)
      if os.path.exists(self._list_file_entries_path):
        break

  def _RunListFileEntries(self, test_definition, temp_directory, source_path):
    """Runs list_file_entries on a storage media image.

    Args:
      test_definition (TestDefinition): test definition.
      temp_directory (str): name of a temporary directory.
      source_path (str): path of the source.

    Returns:
      bool: True if list_file_entries ran successfully.
    """
    output_file_path = None
    if test_definition.output_file:
      output_file_path = os.path.join(
          temp_directory, test_definition.output_file)
    output_options = ['--output-file', output_file_path]

    stdout_file = os.path.join(
        temp_directory, '{0:s}-list_file_entries.out'.format(
            test_definition.name))
    stderr_file = os.path.join(
        temp_directory, '{0:s}-list_file_entries.err'.format(
            test_definition.name))

    command = [self._list_file_entries_path]
    command.extend(output_options)
    command.append(source_path)

    with open(stdout_file, 'w') as stdout:
      with open(stderr_file, 'w') as stderr:
        result = self._RunCommand(command, stdout=stdout, stderr=stderr)

    if self._debug_output:
      with open(stderr_file, 'rb') as file_object:
        output_data = file_object.read()
        print(output_data)

    if output_file_path and os.path.exists(output_file_path):
      shutil.copy(output_file_path, self._test_results_path)

    if os.path.exists(stdout_file):
      shutil.copy(stdout_file, self._test_results_path)
    if os.path.exists(stderr_file):
      shutil.copy(stderr_file, self._test_results_path)

    return result

  def Run(self, test_definition):
    """Runs the test case with the parameters specified by the test definition.

    Args:
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the test ran successfully.
    """
    source_path = test_definition.source
    if self._test_sources_path:
      source_path = os.path.join(self._test_sources_path, source_path)

    if not os.path.exists(source_path):
      logging.error('No such source: {0:s}'.format(source_path))
      return False

    with TempDirectory() as temp_directory:
      # List file entries with list_file_entries.
      if not self._RunListFileEntries(
          test_definition, temp_directory, source_path):
        return False

      # Compare output file with a reference output file.
      if test_definition.output_file and test_definition.reference_output_file:
        if not self._CompareOutputFile(test_definition, temp_directory):
          return False

    return True


class RecursiveHasherTestCase(ExampleScriptTestCase):
  """Recursive hasher test case.

  The recursive hasher test case runs the recursive_hasher.py example script
  on a storage media image, specified by the test definition.
  """

  NAME = 'recursive_hasher'

  def __init__(
      self, scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=False):
    """Initializes a test case.

    Args:
      scripts_path (str): path to the example scripts.
      test_sources_path (str): path to the test sources.
      test_references_path (str): path to the test references.
      test_results_path (str): path to store test results.
      debug_output (Optional[bool]): True if debug output should be generated.
    """
    super(RecursiveHasherTestCase, self).__init__(
        scripts_path, test_sources_path, test_references_path,
        test_results_path, debug_output=debug_output)
    self._recursive_hasher_path = None
    self._InitializeRecursiveHasherPath()

  def _InitializeRecursiveHasherPath(self):
    """Initializes the location of recursive_hasher.py."""
    for filename in (
        'recursive_hasher.exe', 'recursive_hasher.sh', 'recursive_hasher.py'):
      self._recursive_hasher_path = os.path.join(self._scripts_path, filename)
      if os.path.exists(self._recursive_hasher_path):
        break

  def _RunRecursiveHasher(self, test_definition, temp_directory, source_path):
    """Runs recursive_hasher on a storage media image.

    Args:
      test_definition (TestDefinition): test definition.
      temp_directory (str): name of a temporary directory.
      source_path (str): path of the source.

    Returns:
      bool: True if recursive_hasher ran successfully.
    """
    output_file_path = None
    if test_definition.output_file:
      output_file_path = os.path.join(
          temp_directory, test_definition.output_file)
    output_options = ['--output-file', output_file_path]

    stdout_file = os.path.join(
        temp_directory, '{0:s}-recursive_hasher.out'.format(
            test_definition.name))
    stderr_file = os.path.join(
        temp_directory, '{0:s}-recursive_hasher.err'.format(
            test_definition.name))

    command = [self._recursive_hasher_path]
    command.extend(output_options)
    command.append(source_path)

    with open(stdout_file, 'w') as stdout:
      with open(stderr_file, 'w') as stderr:
        result = self._RunCommand(command, stdout=stdout, stderr=stderr)

    if self._debug_output:
      with open(stderr_file, 'rb') as file_object:
        output_data = file_object.read()
        print(output_data)

    if output_file_path and os.path.exists(output_file_path):
      shutil.copy(output_file_path, self._test_results_path)

    if os.path.exists(stdout_file):
      shutil.copy(stdout_file, self._test_results_path)
    if os.path.exists(stderr_file):
      shutil.copy(stderr_file, self._test_results_path)

    return result

  def Run(self, test_definition):
    """Runs the test case with the parameters specified by the test definition.

    Args:
      test_definition (TestDefinition): test definition.

    Returns:
      bool: True if the test ran successfully.
    """
    source_path = test_definition.source
    if self._test_sources_path:
      source_path = os.path.join(self._test_sources_path, source_path)

    if not os.path.exists(source_path):
      logging.error('No such source: {0:s}'.format(source_path))
      return False

    with TempDirectory() as temp_directory:
      # Recursively hash data streams with recursive_hasher.
      if not self._RunRecursiveHasher(
          test_definition, temp_directory, source_path):
        return False

      # Compare output file with a reference output file.
      if test_definition.output_file and test_definition.reference_output_file:
        if not self._CompareOutputFile(test_definition, temp_directory):
          return False

    return True


TestCasesManager.RegisterTestCases([
    ListFileEntriesTestCase, RecursiveHasherTestCase])


def Main():
  """The main function."""
  argument_parser = argparse.ArgumentParser(
      description='End-to-end test launcher.', add_help=False,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  argument_parser.add_argument(
      '-c', '--config', dest='config_file', action='store',
      metavar='CONFIG_FILE', default=None,
      help='path of the test configuration file.')

  argument_parser.add_argument(
      '--debug', dest='debug_output', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-h', '--help', action='help',
      help='show this help message and exit.')

  argument_parser.add_argument(
      '--references-directory', '--references_directory', action='store',
      metavar='DIRECTORY', dest='references_directory', type=str,
      default=None, help=(
          'The location of the directory where the test references are '
          'stored.'))

  argument_parser.add_argument(
      '--results-directory', '--results_directory', action='store',
      metavar='DIRECTORY', dest='results_directory', type=str,
      default=None, help=(
          'The location of the directory where to store the test results.'))

  argument_parser.add_argument(
      '--scripts-directory', '--scripts_directory', action='store',
      metavar='DIRECTORY', dest='scripts_directory', type=str,
      default=None, help='The location of the dfvfs example scripts directory.')

  argument_parser.add_argument(
      '--sources-directory', '--sources_directory', action='store',
      metavar='DIRECTORY', dest='sources_directory', type=str,
      default=None, help=(
          'The location of the directory where the test sources are stored.'))

  options = argument_parser.parse_args()

  if not options.config_file:
    options.config_file = os.path.dirname(__file__)
    options.config_file = os.path.dirname(options.config_file)
    options.config_file = os.path.join(
        options.config_file, 'config', 'end-to-end.ini')

  if not os.path.exists(options.config_file):
    print('No such config file: {0:s}.'.format(options.config_file))
    print('')
    return False

  logging.basicConfig(
      format='[%(levelname)s] %(message)s', level=logging.INFO)

  scripts_path = options.scripts_directory
  if not scripts_path:
    scripts_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'examples')

  test_sources_path = options.sources_directory
  if test_sources_path and not os.path.isdir(test_sources_path):
    print('No such sources directory: {0:s}.'.format(test_sources_path))
    print('')
    return False

  test_references_path = options.references_directory
  if test_references_path and not os.path.isdir(test_references_path):
    print('No such references directory: {0:s}.'.format(test_references_path))
    print('')
    return False

  test_results_path = options.results_directory
  if not test_results_path:
    test_results_path = os.getcwd()

  if not os.path.isdir(test_results_path):
    print('No such results directory: {0:s}.'.format(test_results_path))
    print('')
    return False

  tests = []
  with open(options.config_file) as file_object:
    test_definition_reader = TestDefinitionReader(
        scripts_path, test_sources_path, test_references_path,
        test_results_path, debug_output=options.debug_output)
    for test_definition in test_definition_reader.Read(file_object):
      tests.append(test_definition)

  test_launcher = TestLauncher(
      scripts_path, test_sources_path, test_references_path,
      test_results_path, debug_output=options.debug_output)
  test_launcher.ReadDefinitions(options.config_file)

  failed_tests = test_launcher.RunTests()
  if failed_tests:
    print('Failed tests:')
    for failed_test in failed_tests:
      print(' {0:s}'.format(failed_test))

    print('')
    return False

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
