#! /bin/bash
dirname=${PWD##*/}
target_dir=$HOME/$dirname

echo mkdir "$target_dir"
echo ln -s "$PWD/*" "$target_dir/*"
echo ln -s $HOME/.env $target_dir/
echo cd "$target_dir"

# Docker
echo docker compose up -d --build