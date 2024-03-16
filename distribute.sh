#!/usr/bin/env bash

PROJECT_TOML="pyproject.toml"

version=$(grep -m1 "^version =" "$PROJECT_TOML" | cut -d'=' -f2 | tr -d ' ' | sed 's/^"//; s/"$//')

version="v$version"

testing=$1

pip install --upgrade build twine
python -m build

if [[ "$testing" == "test" ]]; then
    echo "Uploading to TestPyPI"
    python -m twine upload --repository testpypi dist/*
else
    echo "Uploading to PyPI"
    # python -m twine upload dist/*
fi



# git tag -a "$version" -m "Release $version"