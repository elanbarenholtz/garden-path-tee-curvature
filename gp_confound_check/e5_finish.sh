#!/bin/zsh
# E5 finisher: wait for all rungs, avoid duplicate CPU v2b, analyze, commit.
GP=~/Projects/garden-path-tee-curvature
GPC=$GP/gp_confound_check
PY=/Users/elanbarenholtz/Projects/ZuCo_TEE_Analysis/venv/bin/python

# wait for the CPU chain to produce all remaining rungs
while [[ ! -f $GPC/e5_positions_v2c.csv || ! -f $GPC/e5_positions_v1c.csv \
      || ! -f $GPC/e5_positions_v2b.csv ]]; do
  sleep 60
done
sleep 15

cd $GP
$PY gp_confound_check/e5_rank_test.py analyze v2a v1b v2b v2c v1c \
  > gp_confound_check/e5_summary.txt 2>&1
grep -E "VALID" gp_confound_check/e5_run_*.log \
  >> gp_confound_check/e5_summary.txt
git add gp_confound_check/e5_rank_test.py gp_confound_check/e5_probe.py \
  gp_confound_check/e5_probe2.py gp_confound_check/e5_positions_*.csv \
  gp_confound_check/e5_summary.txt gp_confound_check/e5_run_*.log \
  gp_confound_check/e5_finish.sh
git commit -m "E5 run: all five rungs (v2a v1b v2b v2c v1c), summary, logs" \
  > /dev/null 2>&1
echo "E5 FINISHED $(date)" >> gp_confound_check/e5_summary.txt
