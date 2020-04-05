rm /tmp/predicu_cache.h5
for file in `ls plots/*.py`; do
    python "$file"
done
