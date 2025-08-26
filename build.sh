#! /bin/bash
set -x      # echo output
dirname=${PWD##*/}
target_dir=/tmp/$dirname

mkdir "$target_dir"
cp -rf "$PWD/"* "$target_dir"
cp -f $HOME/.env $target_dir/
cd "$target_dir"

# Docker
docker compose up -d --build --remove-orphans