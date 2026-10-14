#!/usr/bin/env bash
set -euo pipefail

TARGETS=("src")   # только свои каталоги, без "."

isort --settings-path ./.isort.cfg "${TARGETS[@]}"
black --config ./.black "${TARGETS[@]}"