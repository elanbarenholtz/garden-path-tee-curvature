"""
Anticipated curvature (F3 core).

At token position t the model holds a next-token distribution p(v | x_<=t).
For each candidate v in the top-k of that distribution, append v, run ONE
cached forward step, and read the layer-L state h_v at position t+1. The
curvature v would produce on arrival is the angle between successive steps:

    a(v) = angle( h_v - h[t],  h[t] - h[t-1] )          in [0, pi]

This is exactly curvature_1 as defined in tee_vs_curvature/compute_curvature.py,
evaluated at t+1 under the hypothesis that v is the next token.
Weighting by p(v) (renormalised over the top-k) gives a distribution over
curvatures:

    ac_mean = E_p[a(v)]      path displacement the model anticipates
    ac_var  = Var_p[a(v)]    uncertainty about where the trajectory is heading
    ac_sd   = sqrt(ac_var)

ac_var is not entropy: two equally likely continuations that bend the path the
same way give ac_var ~ 0 at maximal two-way entropy; two that bend it in
opposite directions give large ac_var at the same entropy.
(Note: a(v) is an unsigned angle, so "opposite directions" registers only in
so far as the two continuations produce different turning angles. A direction-
sensitive companion is ac_disp: the probability-weighted mean pairwise angle
between candidate step vectors, which does see opposite headings. Reported as
a secondary column.)

curvature_3 counterpart: curvature_3 at t+1 is mean(angle(t-1), angle(t), a(v)),
the first two fixed given the context, so ac_mean3 = (angle(t-1)+angle(t)+ac_mean)/3
and ac_var3 = ac_var/9. These are affine in ac_mean/ac_var, so they carry no
new information and are provided only so the anticipated quantity is on the same
scale as the realised curvature_3.

Also returned, from the SAME distribution, so the entropy comparison is exact:
    ent_full   entropy of the full next-token distribution (nats)
    ent_topk   entropy of the renormalised top-k
    mass_topk  probability mass captured by the top-k

k-stability: every k in K_LIST is computed from the same candidate pass
(the top-kmax set, nested prefixes), so stability is checked at no extra cost.

Cache handling uses only DynamicCache.update(), which is stable across
transformers 4.4x-5.x.
"""
import numpy as np
import torch
from transformers import DynamicCache


def _angle_rows(A, b):
    """angles between each row of A (n,d) and vector b (d,)"""
    na = np.linalg.norm(A, axis=1); nb = np.linalg.norm(b)
    out = np.full(len(A), np.nan)
    ok = (na > 1e-8) & (nb > 1e-8)
    c = (A[ok] @ b) / (na[ok] * nb)
    out[ok] = np.arccos(np.clip(c, -1.0, 1.0))
    return out


def _legacy(pkv):
    """per-layer list of (key, value) tensors from any cache object"""
    if isinstance(pkv, (tuple, list)):
        return [(k, v) for k, v in pkv]
    if hasattr(pkv, "layers"):                      # transformers >= 4.56 / 5.x
        return [(l.keys, l.values) for l in pkv.layers]
    if hasattr(pkv, "key_cache"):                   # 4.4x-4.55
        return list(zip(pkv.key_cache, pkv.value_cache))
    raise TypeError(f"unknown cache type {type(pkv)}")


def _sliced_cache(legacy, upto, batch):
    """cache for context [0, upto) expanded to `batch` rows"""
    c = DynamicCache()
    for li, (k, v) in enumerate(legacy):
        c.update(k[:, :, :upto].expand(batch, -1, -1, -1).contiguous(),
                 v[:, :, :upto].expand(batch, -1, -1, -1).contiguous(), li)
    return c


@torch.no_grad()
def chunk_anticipated(model, chunk_ids, local_positions, layer, k_list,
                      check_positions=()):
    """
    chunk_ids: 1D LongTensor, one context window (<= model max length).
    local_positions: indices t within the chunk to evaluate (need t >= 1).
    Returns (rows, checks). rows: dict per t. checks: max |h_v - h_full[t+1]|
    for the realised next token at each t in check_positions (cache sanity).
    """
    out = model(chunk_ids.unsqueeze(0), output_hidden_states=True,
                use_cache=True)
    H = out.hidden_states[layer][0].float().cpu().numpy()      # (L, d)
    logp_all = torch.log_softmax(out.logits[0].float(), -1)     # (L, V)
    legacy = _legacy(out.past_key_values)
    kmax = max(k_list)
    rows, checks = {}, {}
    for t in local_positions:
        if t < 1:
            continue
        lp = logp_all[t]
        p = lp.exp()
        ent_full = float(-(p * lp).sum())
        top_lp, top_ix = torch.topk(lp, kmax)
        # realised next token appended when a sanity check is requested here
        cand = top_ix
        want_check = t in check_positions and t + 1 < len(chunk_ids)
        if want_check:
            cand = torch.cat([top_ix, chunk_ids[t + 1:t + 2]])
        cache = _sliced_cache(legacy, t + 1, len(cand))
        o = model(cand.view(-1, 1), past_key_values=cache,
                  output_hidden_states=True, use_cache=False)
        Hv = o.hidden_states[layer][:, 0].float().cpu().numpy()
        if want_check:
            checks[t] = float(np.abs(Hv[-1] - H[t + 1]).max())
            Hv = Hv[:-1]
        prev_step = H[t] - H[t - 1]
        steps = Hv - H[t]                                       # (kmax, d)
        a = _angle_rows(steps, prev_step)
        w_all = top_lp.exp().cpu().numpy()
        r = dict(ent_full=ent_full)
        for k in k_list:
            w = w_all[:k]; m = np.isfinite(a[:k]); w = w * m
            mass = float(w_all[:k].sum()); w = w / w.sum()
            ak = np.where(m, a[:k], 0.0)
            mu = float((w * ak).sum())
            var = float((w * (ak - mu) ** 2).sum())
            # direction-sensitive dispersion: weighted mean pairwise angle
            S = steps[:k]
            Sn = S / (np.linalg.norm(S, axis=1, keepdims=True) + 1e-12)
            G = np.arccos(np.clip(Sn @ Sn.T, -1.0, 1.0))
            disp = float(w @ G @ w)
            pk = w_all[:k] / w_all[:k].sum()
            r.update({f"ac_mean_k{k}": mu, f"ac_var_k{k}": var,
                      f"ac_disp_k{k}": disp, f"mass_k{k}": mass,
                      f"ent_topk_k{k}": float(-(pk * np.log(pk)).sum())})
        rows[t] = r
    return rows, checks
