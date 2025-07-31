#! /bin/bash
set -x      # echo output
dirname=${PWD##*/}
target_dir=$HOME/$dirname

rm -r "$target_dir"
mkdir "$target_dir"
ln -sr "$PWD/"* "$target_dir"
# ln -s $HOME/.env $target_dir/
cd "$target_dir"
ls -a

# Docker
# docker compose up -d --build