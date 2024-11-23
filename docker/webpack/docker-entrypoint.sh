#!/usr/bin/env sh
set -euo pipefail

# Do not run if `package.json` is not present.
if [[ ! -f "package.json" ]];
then
    >&2 echo "package.json not found. Make sure mounts are syncing."
    exit
fi

exec "$@"
