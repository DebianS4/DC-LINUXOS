#!/usr/bin/env sh
set -eu

rm -rf dist
mkdir -p dist/assets dist/public
cp index.html styles.css script.js package.json dist/
cp favicon.ico dist/
cp assets/* dist/assets/
cp public/manus-routes.json dist/public/
printf '%s\n' "DC-LINUX static build ready in dist/"
