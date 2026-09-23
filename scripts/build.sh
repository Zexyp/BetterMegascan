#!/bin/bash
set -e

mkdir -p dist
blender --command extension build --source-dir BetterMegascan --output-dir dist
