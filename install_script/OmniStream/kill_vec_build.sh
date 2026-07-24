#!/bin/bash
TARGET=210452
OURMAKE=236113
PGID=$(ps -o pgid= -p "$TARGET" | tr -d ' ')
OURPGID=$(ps -o pgid= -p "$OURMAKE" | tr -d ' ')
echo "target_pgid=$PGID our_pgid=$OURPGID"
if [ -z "$PGID" ]; then
    echo "target process $TARGET not running"
    exit 0
fi
if [ "$PGID" = "$OURPGID" ]; then
    echo "REFUSING: target shares our build's process group"
    exit 1
fi
kill -TERM -"$PGID" 2>/dev/null
sleep 4
kill -KILL -"$PGID" 2>/dev/null
sleep 2
if pgrep -f 'build_scripts/build.sh release:java' >/dev/null; then
    echo "WARN: vec build still present"
    pgrep -af 'build_scripts/build.sh release:java'
else
    echo "vec build terminated"
fi
echo "--- remaining cc1plus count ---"
pgrep -c cc1plus || echo 0
