#!/usr/bin/env sh
set -eu

rm -rf dist
mkdir -p dist/assets
cp index.html styles.css script.js dist/
cp favicon.ico dist/
cp favicon.svg dist/
cp assets/* dist/assets/
printf '%s\n' "DC-LINUX static build ready in dist/"
