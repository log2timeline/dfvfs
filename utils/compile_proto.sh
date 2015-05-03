#!/bin/bash
# Script to compile protobufs.

compile()
{
  protoc -I=. --python_out=. dfvfs/proto/$1
}

compile transmission.proto
