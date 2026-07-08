#!/bin/zsh
cd ~/Projects/garden-path-tee-curvature
PY=.venv/bin/python
echo "medium: states"
$PY extensions/x9a_xl_states.py gpt2-medium > extensions/x9a_med.log 2>&1 || exit 1
echo "medium: measures"
$PY extensions/x9c_xl_measures.py gpt2_medium > extensions/x9c_med.log 2>&1 || exit 1
echo "medium: wake"
$PY extensions/x9b_xl_wake.py 12 gpt2-medium > extensions/x9b_med.log 2>&1 || exit 1
echo "medium: wake analysis"
$PY extensions/x9d_xl_wake_analysis.py gpt2_medium 12 > extensions/x9d_med.log 2>&1
echo "MED CHAIN DONE"
