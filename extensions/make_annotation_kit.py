"""Build the human event-segmentation annotation kit: a per-sentence sheet
with a blank boundary column, one CSV per annotator to fill."""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xlib import GP, load_locked

KIT = f"{GP}/extensions/human_annotation_kit"
S, _ = load_locked()
S = S.sort_values(["story_id", "word_idx"])
rows = []
for (sid, su), g in S.groupby(["story_id", "sent_uid"], sort=True):
    rows.append({"story_id": int(sid), "sent_uid": int(su),
                 "sentence": " ".join(g.word)})
D = pd.DataFrame(rows).sort_values(["story_id", "sent_uid"]) \
    .reset_index(drop=True)
D["boundary_1_if_new_event"] = ""
D.to_csv(f"{KIT}/annotation_sheet.csv", index=False)
print(f"wrote {len(D)} sentences -> annotation_sheet.csv")
