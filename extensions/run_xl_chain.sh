#!/bin/zsh
# Chain: wait for x9a (states) then run x9c (measures) -> x9b (wake) -> x9d.
cd ~/Projects/garden-path-tee-curvature
PY=.venv/bin/python
while ! grep -q "DONE gpt2-xl" extensions/x9a_xl.log 2>/dev/null; do
  if ! pgrep -f x9a_xl_states.py > /dev/null; then
    echo "x9a died without DONE" ; exit 1
  fi
  sleep 30
done
echo "x9a complete; running x9c"
$PY extensions/x9c_xl_measures.py gpt2_xl > extensions/x9c_xl.log 2>&1 \
  || exit 1
echo "x9c complete; running x9b (wake)"
$PY extensions/x9b_xl_wake.py 12 gpt2-xl > extensions/x9b_xl.log 2>&1 \
  || exit 1
echo "x9b complete; running x9d"
$PY extensions/x9d_xl_wake_analysis.py gpt2_xl 12 > extensions/x9d_xl.log 2>&1
echo "CHAIN DONE"
