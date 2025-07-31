#! /bin/bash
dirname=${PWD##*/}
target_dir=$HOME/$dirname

ln -s "$PWD/*" "$target_dir/*"
ln -s $home/.env $target_dir/
cd "$target_dir"

# Docker
docker compose up -d --build