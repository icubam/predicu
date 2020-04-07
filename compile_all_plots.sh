RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

rm /tmp/predicu_cache.h5
for file in `ls plots/*.py`; do
    if python "$file"; then
        echo "${GREEN}compiled plot $file${NC}"
    else
        echo "${RED}FAILED $file${NC}"
    fi
done
