#!/bin/bash

if [ -z $1 ] ; then
  echo "[1mUsage:[0m update.sh [4mCOMMIT_MSG[0m"
  exit 1
fi

# Switch to code branch for version controlling tutorial.py
git checkout code

# Commit and push changes to tutorial.py, using supplied commit message.
git add tutorial.py requirements.txt README.md update.sh
git commit -m "$1"
git push origin code

# Rebase demo_code on top of new tutorial.py commit.
git checkout demo_code
git rebase code

# Move main head to resulting merged history.
git checkout main
git reset --hard demo_code

# Renew step_back tag to match altered history.
git checkout HEAD~1
git tag -f step_back

# Force push changed history and tag.
git push -f origin main
git push -f origin step_back

# Reset demo_code branch to original for future rebases.
git checkout demo_code
git reset --hard origin/demo_code

# Checkout main branch afterwards.
git checkout main
