# -*- coding: utf-8 -*-
"""Function decorators."""

import warnings


def deprecated(function):  # pylint: disable=invalid-name
  """Decorator to mark functions or methods as deprecated."""

  def IssueDeprecationWarning(*args, **kwargs):
    """Issue a deprecation warning."""
    warnings.simplefilter('default', DeprecationWarning)
    warnings.warn(
        f'Call to deprecated function: {function.__name__:s}.',
        category=DeprecationWarning, stacklevel=2)

    return function(*args, **kwargs)

  IssueDeprecationWarning.__name__ = function.__name__
  IssueDeprecationWarning.__doc__ = function.__doc__
  IssueDeprecationWarning.__dict__.update(function.__dict__)
  return IssueDeprecationWarning
