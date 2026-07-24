#!/bin/bash
cd /opt/buildtools/OmniStream/cpp
echo '=== any "using namespace omniruntime" (broad) ==='
grep -rnE 'using +namespace +(::)?omniruntime *;' --include=*.h --include=*.cpp .
echo '=== "using namespace omniruntime::" sub-namespace directives ==='
grep -rnE 'using +namespace +omniruntime::' --include=*.h --include=*.cpp . | head -n 60
