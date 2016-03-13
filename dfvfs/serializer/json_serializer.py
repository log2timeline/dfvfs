# -*- coding: utf-8 -*-
"""The JSON serializer object implementation."""

import json

from dfvfs.path import factory as path_spec_factory
from dfvfs.path import path_spec
from dfvfs.serializer import serializer

class _PathSpecJsonDecoder(json.JSONDecoder):
  """A class that implements a path specification JSON decoder."""

  _CLASS_TYPES = frozenset([u'PathSpec'])

  def __init__(self, *args, **kargs):
    """Initializes the path specification JSON decoder object."""
    super(_PathSpecJsonDecoder, self).__init__(
        *args, object_hook=self._ConvertDictToObject, **kargs)

  def _ConvertDictToObject(self, json_dict):
    """Converts a JSON dict into a path specification object.

    The dictionary of the JSON serialized objects consists of:
    {
        '__type__': 'PathSpec'
        'type_indicator': 'OS'
        'parent': { ... }
        ...
    }

    Here '__type__' indicates the object base type in this case this should
    be 'PathSpec'. The rest of the elements of the dictionary make up the
    path specification object properties. Note that json_dict is a dict of
    dicts and the _ConvertDictToObject method will be called for every dict.
    That is how the path specification parent objects are created.

    Args:
      json_dict: a dictionary of the JSON serialized objects.

    Returns:
      A path specification (instance of PathSpec).

    Raises:
      TypeError: if the JSON serialized object does not contain a '__type__'
                 attribute that contains 'PathSpec'.
    """
    # Use __type__ to indicate the object class type.
    class_type = json_dict.get(u'__type__', None)

    if class_type not in self._CLASS_TYPES:
      raise TypeError(u'Missing path specification object type.')

    # Remove the class type from the JSON dict since we cannot pass it.
    del json_dict[u'__type__']

    type_indicator = json_dict.get(u'type_indicator', None)
    if type_indicator:
      del json_dict[u'type_indicator']

    # Convert row_condition back to a tuple.
    if u'row_condition' in json_dict:
      json_dict[u'row_condition'] = tuple(json_dict[u'row_condition'])

    return path_spec_factory.Factory.NewPathSpec(type_indicator, **json_dict)


class _PathSpecJsonEncoder(json.JSONEncoder):
  """A class that implements a path specification object JSON encoder."""

  # Note: that the following functions do not follow the style guide
  # because they are part of the json.JSONEncoder object interface.

  # pylint: disable=method-hidden
  def default(self, path_spec_object):
    """Converts a path specification object into a JSON dictionary.

    The resulting dictionary of the JSON serialized objects consists of:
    {
        '__type__': 'PathSpec'
        'type_indicator': 'OS'
        'parent': { ... }
        ...
    }

    Here '__type__' indicates the object base type in this case this should
    be 'PathSpec'. The rest of the elements of the dictionary make up the
    path specification object properties. The supported property names are
    defined in path_spec_factory.Factory.PROPERTY_NAMES. Note that this method
    is called recursively for every path specification object and creates
    a dict of dicts in the process that is transformed into a JSON string
    by the JSON encoder.

    Args:
      path_spec_object: a path specification (instance of PathSpec).

    Returns:
      A dictionary of the JSON serialized objects.

    Raises:
      TypeError: if not an instance of PathSpec.
    """
    if not isinstance(path_spec_object, path_spec.PathSpec):
      raise TypeError

    json_dict = {u'__type__': u'PathSpec'}
    for property_name in path_spec_factory.Factory.PROPERTY_NAMES:
      property_value = getattr(path_spec_object, property_name, None)
      if property_value is not None:
        # Convert row_condition tuple to a list
        if property_name == u'row_condition':
          json_dict[property_name] = list(property_value)
        else:
          json_dict[property_name] = property_value

    if path_spec_object.HasParent():
      json_dict[u'parent'] = self.default(path_spec_object.parent)

    json_dict[u'type_indicator'] = path_spec_object.type_indicator
    location = getattr(path_spec_object, u'location', None)
    if location:
      json_dict[u'location'] = location

    return json_dict


class JsonPathSpecSerializer(serializer.PathSpecSerializer):
  """Class that implements a json path specification serializer object."""

  @classmethod
  def ReadSerialized(cls, json_string):
    """Reads a path specification from serialized form.

    Args:
      json_string: a JSON string containing the serialized path specification.

    Returns:
      A path specification (instance of PathSpec).
    """
    json_decoder = _PathSpecJsonDecoder()
    return json_decoder.decode(json_string)

  @classmethod
  def WriteSerialized(cls, path_spec_object):
    """Writes a path specification to serialized form.

    Args:
      path_spec_object: a path specification (instance of PathSpec).

    Returns:
      A JSON string containing the serialized path specification.
    """
    return json.dumps(path_spec_object, cls=_PathSpecJsonEncoder)
