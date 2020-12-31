# -*- coding: utf-8 -*-
"""Glob to regular expression conversion.

Also see: https://en.wikipedia.org/wiki/Glob_(programming)
"""

import re
import sys


PY_3_7_AND_LATER = bool(tuple(sys.version_info[0:2]) >= (3, 7))


def Glob2Regex(glob_pattern):
  """Converts a glob pattern to a regular expression.

  This function supports basic glob patterns that consist of:
  *       matches everything
  ?       matches any single character
  [seq]   matches any character in sequence
  [!seq]  matches any character not in sequence

  Args:
    glob_pattern (str): glob pattern.

  Returns:
    str: regular expression pattern.

  Raises:
    ValueError: if the glob pattern cannot be converted.
  """
  if not glob_pattern:
    raise ValueError('Missing glob pattern.')

  regex_pattern = []

  glob_pattern_index = 0
  glob_pattern_length = len(glob_pattern)
  while glob_pattern_index < glob_pattern_length:
    character = glob_pattern[glob_pattern_index]
    glob_pattern_index += 1

    if character == '*':
      regex_pattern.append('.*')

    elif character == '?':
      regex_pattern.append('.')

    elif character != '[':
      regex_character = re.escape(character)
      regex_pattern.append(regex_character)

    else:
      glob_group_index = glob_pattern_index

      if (glob_group_index < glob_pattern_length and
          glob_pattern[glob_group_index] == '!'):
        glob_group_index += 1

      if (glob_group_index < glob_pattern_length and
          glob_pattern[glob_group_index] == ']'):
        glob_group_index += 1

      while (glob_group_index < glob_pattern_length and
             glob_pattern[glob_group_index] != ']'):
        glob_group_index += 1

      if glob_group_index >= glob_pattern_length:
        regex_pattern.append('\\[')
        continue

      glob_group = glob_pattern[glob_pattern_index:glob_group_index]
      glob_pattern_index = glob_group_index + 1

      glob_group = glob_group.replace('\\', '\\\\')
      if PY_3_7_AND_LATER:
        glob_group = glob_group.replace('|', '\\|')

      regex_pattern.append('[')

      if glob_group[0] == '!':
        regex_pattern.append('^')
        glob_group = glob_group[1:]

      elif glob_group[0] == '^':
        regex_pattern.append('\\')

      regex_pattern.append(glob_group)
      regex_pattern.append(']')

  return ''.join(regex_pattern)
