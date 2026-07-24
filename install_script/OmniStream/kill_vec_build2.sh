#!/bin/bash
# Kill the OmniOperatorVec self-build precisely (by cwd + orchestrator),
# while sparing the OmniStream build (cwd under /opt/buildtools/OmniStream).
for round in 1 2 3; do
    # 1) kill all vec build orchestrators
    pkill -KILL -f 'build_scripts/build.sh' 2>/dev/null
    pkill -KILL -f 'OmniOperatorVec/build' 2>/dev/null
    # 2) kill any process whose cwd is under OmniOperatorVec
    for pid in $(ls /proc | grep -E '^[0-9]+$'); do
        cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null)
        case "$cwd" in
            /opt/buildtools/OmniOperatorVec*) kill -KILL "$pid" 2>/dev/null ;;
        esac
    done
    sleep 3
done
echo "--- remaining vec orchestrators ---"
pgrep -af 'build_scripts/build.sh' | grep -v grep || echo none
echo "--- remaining cc1plus total ---"
pgrep -c cc1plus || echo 0
echo "--- our OmniStream make alive? ---"
pgrep -af 'make install' | grep -v grep || echo 'our make NOT running'
