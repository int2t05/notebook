#!/bin/bash
cd /opt/buildtools/OmniStream/cpp
echo '=== files with global "using namespace omniruntime;" ==='
grep -rlE '^using namespace omniruntime;' --include=*.h --include=*.cpp . | head -n 60
echo '=== includes of third_party date ==='
grep -rnE 'third_party/date|date/date.h' --include=*.h --include=*.cpp . | head -n 40
echo '=== OmniStream (non third_party) files using date:: ==='
grep -rlE 'date::' --include=*.h --include=*.cpp . | grep -v third_party | head -n 40
echo '=== top of third_party/date/date.h namespace ==='
grep -nE 'namespace date' third_party/date/date.h | head
echo '=== vec tzdb/date.h namespace ==='
grep -nE 'namespace ' /opt/buildtools/OmniOperatorVec/core/src/type/tzdb/date.h | head
