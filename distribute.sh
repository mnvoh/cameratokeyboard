#!/usr/bin/env bash

PROJECT_TOML="pyproject.toml"

version=$(grep -m1 "^version =" "$PROJECT_TOML" | cut -d'=' -f2 | tr -d ' ' | sed 's/^"//; s/"$//')

version="v$version"

testing=$1

rm -r dist

pip install --upgrade build twine
python -m build

if [[ "$testing" == "test" ]]; then
    echo "Uploading to TestPyPI"
    python -m twine upload \
        -u "__TOKEN__" \
        -p "${PYPI_TEST_PASSWORD}" \
        --repository testpypi \
        dist/*
else
    echo "Uploading to PyPI"
    python -m twine upload \
        -u "__TOKEN__" \
        -p "${PYPI_PROD_PASSWORD}" \
        dist/*

    git push
    git tag -a "$version" -m "Release $version"
    git push origin "$version"
fi

