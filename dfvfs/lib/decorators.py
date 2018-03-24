# -*- coding: utf-8 -*-
"""Function decorators."""

from __future__ import unicode_literals

import warnings


def deprecated(function):  # pylint: disable=invalid-name
  """Decorator to mark functions or methods as deprecated."""

  def IssueDeprecationWarning(*args, **kwargs):
    """Issue a deprecation warning."""
    warnings.simplefilter('default', DeprecationWarning)
    warnings.warn('Call to deprecated function: {0:s}.'.format(
        function.__name__), category=DeprecationWarning, stacklevel=2)

    return function(*args, **kwargs)

  IssueDeprecationWarning.__name__ = function.__name__
  IssueDeprecationWarning.__doc__ = function.__doc__
  IssueDeprecationWarning.__dict__.update(function.__dict__)
  return IssueDeprecationWarning
