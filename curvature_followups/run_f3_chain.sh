#!/bin/bash
cd "$(dirname "$0")"
export GPT2_PATH=${GPT2_PATH:-gpt2}
python3 -u f3_anticipated_ns.py > f3_out.log 2>&1 && python3 -u f3b_anticipated_rt.py > f3b_out.log 2>&1
echo CHAIN_DONE >> f3b_out.log
