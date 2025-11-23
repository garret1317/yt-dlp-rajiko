#!/bin/bash
version="$(uv tool run hatch version)"
mkdir bundle/
uv pip install --python-version 3.9 --python-platform linux --requirements pyproject.toml --target bundle/yt_dlp_plugins/
uv pip install --python-version 3.9 --python-platform linux --no-deps --target bundle/ .

mkdir bundle/licenses/
for lib_distinfo in bundle/yt_dlp_plugins/*.dist-info bundle/*.dist-info; do
	lib=$(basename "$lib_distinfo" .dist-info)
	cp -r "${lib_distinfo}/licenses" "bundle/licenses/${lib}"
done

rm -rf bundle/yt_dlp_plugins/*.dist-info bundle/*.dist-info bundle/yt_dlp_plugins/bin

mkdir -p dist/
(cd bundle/ && zip -9 --recurse-paths ../dist/yt_dlp_rajiko-"${version}".bundle.zip .)
