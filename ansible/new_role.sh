#! /usr/bin/env bash

if [ -z "$1" ]; then
    echo "need a role name"
    exit 1
fi
echo "new role '$1'"
if [ -d "./playbooks/roles/$1" ]; then
    echo "the role '$1' already exists."
    exit 1
fi
mkdir -p ./playbooks/roles/"$1"/{defaults,handlers,tasks,templates,vars}
touch ./playbooks/roles/"$1"/{defaults,handlers,tasks,vars}/main.yml
echo "role created"
tree "./playbooks/roles/$1"