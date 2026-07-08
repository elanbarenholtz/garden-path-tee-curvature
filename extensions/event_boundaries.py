"""
Event-boundary annotations for the Natural Stories sentences in the locked
sample. Coarse-grained event/topic segmentation at the sentence grain,
produced by a large language model (this assistant) reading each story in
full, blind to per-sentence ntee values. Instruction analogue (Michelmann
et al. 2023; Zacks event-segmentation paradigm): mark a sentence as a boundary
if, in the reader's judgment, one natural and meaningful unit (scene, episode,
time/location shift for narratives; sub-topic for expository texts) ends and a
new one begins at that sentence. LLM segmentation is used as a stand-in for
human norms, which do not exist for this corpus; treat as an AI-annotation
proxy pending human collection. Boundaries stored as (story_id, sent_uid).
"""
BOUNDARIES = {
    1: {1, 4, 8, 13, 16, 18, 22, 23, 25, 33, 41, 46, 51, 55},
    2: {58, 60, 62, 64, 68, 71, 73, 75, 77, 83, 87, 90, 91, 93},
    3: {95, 99, 100, 108, 109, 112, 115, 122, 125, 126, 131, 133, 136, 141,
        143, 144, 145},
    4: {150, 155, 156, 158, 159, 165, 169, 174, 178, 183, 187, 192, 193, 196,
        198, 202},
    5: {206, 208, 210, 211, 217, 221, 223, 227, 229, 231, 234, 239, 242, 244,
        246, 248},
    6: {251, 252, 255, 257, 260, 264, 266, 271, 274, 277, 287, 295, 296, 300,
        305},
    7: {316, 329, 332, 336, 337, 339, 343, 345, 349, 352, 355, 358, 360},
    8: {362, 364, 367, 368, 370, 371, 373, 376, 377, 379, 381, 383, 385, 386,
        388, 389, 391, 393},
    9: {395, 397, 398, 402, 404, 409, 415, 417, 419, 423, 427, 431, 435, 438,
        441},
    10: {442, 443, 445, 448, 451, 452, 456, 461, 466, 469, 471, 477, 481,
         483},
}
