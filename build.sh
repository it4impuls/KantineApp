#! /bin/bash
set -x
dirname=${PWD##*/}
target_dir=$HOME/$dirname

mkdir "$target_dir"
ln -s "$PWD/*" "$target_dir/*"
ln -s $HOME/.env $target_dir/
cd "$target_dir"

# Docker
docker compose up -d --build