#!/bin/bash
version="$(uv tool run hatch version)"
mkdir bundle/
uv pip install --python-version 3.9 --python-platform linux --requirements pyproject.toml --target bundle/yt_dlp_plugins/
rm -rf bundle/yt_dlp_plugins/*.dist-info bundle/yt_dlp_plugins/bin
uv pip install --python-version 3.9 --python-platform linux --no-deps --target bundle/ .
mkdir -p dist/
(cd bundle/ && zip -9 --recurse-paths ../dist/yt_dlp_rajiko-${version}.bundle.zip yt_dlp_plugins)
