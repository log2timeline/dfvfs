#!/bin/bash
# Script that runs the linter on all files.

EXIT_FAILURE=1;
EXIT_SUCCESS=0;

if [ ! -f "utils/common.sh" ];
then
  echo "Missing common functions, are you in the wrong directory?";

  exit ${EXIT_FAILURE};
fi

. utils/common.sh

# Determine if we have the master repo as origin.
HAVE_REMOTE_ORIGIN=have_remote_origin;

if ${HAVE_REMOTE_ORIGIN};
then
  HAVE_UNCOMMITTED_CHANGES=1;
else
  if ! have_remote_upstream;
  then
    echo "Review upload aborted - missing upstream.";
    echo "Run: 'git remote add upstream https://github.com/log2timeline/dfvfs.git'";

    exit ${EXIT_FAILURE};
  fi

  HAVE_UNCOMMITTED_CHANGES=have_uncommitted_changes;
fi

if ${HAVE_UNCOMMITTED_CHANGES};
then
  LINTING_IS_CORRECT=linting_is_correct;
else
  LINTING_IS_CORRECT=linter_pass;
fi

if ! ${LINTING_IS_CORRECT};
then
  echo "Aborted - fix the issues reported by the linter.";

  exit ${EXIT_FAILURE};
fi

exit ${EXIT_SUCCESS};

