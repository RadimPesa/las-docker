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


setting() {
    setting="${1}"
    value="${2}"
    file="${3}"

    if [ -n "${value}" ]; then
        if grep --quiet --fixed-strings "${setting}=" conf/"${file}"; then
            sed --in-place "s|.*${setting}=.*|${setting}=${value}|" conf/"${file}"
            echo "setting ${setting}=${value}" 
        else
            echo "${setting}=${value}" >>conf/"${file}"
        fi
    fi
}

setting "node_auto_indexing" "true" neo4j.properties
setting "node_keys_indexable" "identifier,genid,WG" neo4j.properties