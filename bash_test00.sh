#!/bin/bash

#
# Bash script test 00:
# Remove all *.pyc file from testdir recursively
#

die() {
	echo "Error: $@"
}

TEST_DIR="$(dirname "$0")/testdir"

echo " * Working on ${TEST_DIR}"
mkdir -p "${TEST_DIR}" || die "unable to create ${TEST_DIR}"

echo " * Populate test files..."
for test_file in $(seq 10); do
	touch "${TEST_DIR}/tile_${test_file}.pyc" || die "unable to create file: ${TEST_DIR}/tile_${test_file}.pyc"
done

echo " * Test files list: "

ls "${TEST_DIR}"

echo " * Purge, purge, purge!"

find "${TEST_DIR}" -type f -name '*.pyc' -delete

