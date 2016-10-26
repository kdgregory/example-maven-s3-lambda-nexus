#!/bin/bash
#
# This script prepares the example Maven projects for use. It should be run from
# the example-maven-s3-deploy project directory.
#
################################################################################

mv Deployed-Project /tmp/Maven-S3-Example-Deployed-Project

pushd /tmp/Maven-S3-Example-Deployed-Project
git init .
git add .gitignore pom.xml src
git commit -m "initial commit"
git config core.bare true
popd

git clone /tmp/Maven-S3-Example-Deployed-Project Deployed-Project
