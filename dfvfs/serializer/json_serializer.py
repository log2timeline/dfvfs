#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The JSON serializer object implementation."""

import json

from dfvfs.path import factory as path_spec_factory
from dfvfs.serializer import serializer


class JsonPathSpecSerializer(serializer.PathSpecSerializer):
  """Class that implements a json path specification serializer object."""

  @classmethod
  def ReadSerialized(cls, json_string):
    """Reads a path specification from serialized form.

    Args:
      json_string: a JSON string containing the serialized form.

    Returns:
      A path specification (instance of path.PathSpec).
    """
    json_dict = json.loads(json_string)
    type_indicator = u''

    if 'type_indicator' in json_dict:
      type_indicator = json_dict.get('type_indicator')
      del json_dict['type_indicator']

    if 'parent' in json_dict:
      json_dict['parent'] = cls.ReadSerialized(json_dict.get('parent'))

    return path_spec_factory.Factory.NewPathSpec(type_indicator, **json_dict)

  @classmethod
  def WriteSerialized(cls, path_spec):
    """Writes a path specification to serialized form.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A JSON string containing the serialized form.
    """
    type_indicator = path_spec.type_indicator

    attributes = {}

    # We don't want to set attributes here that are not used.
    for property_name in path_spec_factory.Factory.PROPERTY_NAMES:
      if hasattr(path_spec, property_name):
        property_value = getattr(path_spec, property_name, None)
        if property_value is not None:
          attributes[property_name] = property_value

    if path_spec.HasParent():
      attributes['parent'] = cls.WriteSerialized(path_spec.parent)

    attributes['type_indicator'] = type_indicator
    location = getattr(path_spec, 'location', None)
    if location:
      attributes['location'] = location

    return json.dumps(attributes)
