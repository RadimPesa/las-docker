#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

# do not run init script at each container strat but only at the first start
if [ ! -f /tmp/neo4j-import-done.flag ]; then
    echo "Import database."
    cp -r /neo4j-data/graph.db /data/
    touch /tmp/neo4j-import-done.flag
else
    echo "The import has already been made."
fi