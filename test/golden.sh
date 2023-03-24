#! /usr/bin/env bash

REPO=test_repo
OUTPUT=anonymized
SECRET_FILE=secret_file.txt

# cleanup
rm -rf $REPO

# init git repository
mkdir $REPO
pushd $REPO

# always return back
trap popd 1 2 3 6

git init

# override global git confit that might cause issues
git config commit.gpgsign false

# configure author in git
git config user.name "Tester"
git config user.email "tester@ictunion.cz"

# create commits
git commit --allow-empty -m "initial commit"

# keep committer but set alternative name and email
git config user.name "PublicTester"
git config user.email "very-public@me.com"

# commit again
git commit --allow-empty -m "second commit"

# change committer
git config user.name "Tester2"
git config user.email "tester2@ictunion.cz"

# create commits as 2nd commiter
git commit --allow-empty -m "fixing the mess"

git config user.name "Tester2"
git config user.email "tester2@ictunion.cz"

echo ""
echo "Running assertions:"
echo ""

# Run command
../git-anonymize.py . -c ../test/custom_config.toml -o ../${OUTPUT}

# Asserts

if [ "$?" -ne 0 ]; then
    echo "Command failed"
    exit -1
fi

popd
pushd $OUTPUT

git log --pretty='%cn' | grep 'Tester2'
if [ "$?" == 0 ]; then
    echo "Failed to filter out name of tester2"
    exit 1
fi

git log --pretty='%ce' | grep 'tester2@ictunion.cz'
if [ "$?" == 0 ]; then
    echo "Failed to filter out email of tester2"
    exit 2
fi

git log --pretty='%cn' | grep 'Tester'
if [ "$?" -ne 0 ]; then
    echo "Failed to allow tester name"
    exit 3
fi

git log --pretty='%ce' | grep 'tester@ictunion.cz'
if [ "$?" -ne 0 ]; then
    echo "Failed to allow tester email"
    exit 4
fi
