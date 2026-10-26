"""A1 — Stereo depth-scale accuracy against ruler-measured ChArUco squares.

For every stereo frame in the depth sessions (B), triangulate the detected
ChArUco corners with the factory stereo calibration, then compare the 3D
distance between neighbouring corners with the ruler-measured square size.
Outputs per-frame CSV, per-distance summary CSV and per-hold (tape) CSV.

Run:  PYTHONPATH=. python3 a1_depth_scale.py out_dir
Requires: OpenCV 4.10 (cv2.fisheye), numpy, pandas, pyyaml
"""
import sys, os
import numpy as np, pandas as pd, cv2
from odl_calib import load, best, device_calib, triang, BOARDS

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
os.makedirs(OUT, exist_ok=True)

# Ruler (steel rule, user-measured 2026-10-26): full span / number of squares
RULER = {'a4': dict(x=262.5 / 9, y=175.0 / 6, span_x=262.5, span_y=175.0),
         'far': dict(x=267.0 / 5, y=160.0 / 3, span_x=267.0, span_y=160.0)}
RULER_TOL_MM = 0.5  # assumed reading tolerance of the steel rule per span

dc = device_calib(); T = dc['T_c1_c0']
cal = dict(KL=dc['cam0']['K'], DL=dc['cam0']['D'], KR=dc['cam1']['K'], DR=dc['cam1']['D'], R=T[:3, :3], T=T[:3, 3])
CX, CY = cal['KL'][0, 2], cal['KL'][1, 2]

SESS = [('145221_00000', 'a4', 'B-distance'), ('145446_00000', 'far', 'B-distance'),
        ('145935_00000', 'far', 'B-lateral'), ('150437_00000', 'a4', 'B-lateral')]
rows = []
for rec, kind, sess in SESS:
    L = load(rec, 'left'); R = load(rec, 'right')
    n = BOARDS[kind]['nx'] - 1
    for a, b in zip(L, R):
        th = 8 if kind == 'far' else 12
        bl = best(a, th); br = best(b, th)
        if bl is None or br is None: continue
        X, c = triang(cal, bl, br, kind)
        if X is None or len(c) < th: continue
        m = dict(zip(c, X))
        dx = [np.linalg.norm(m[i + 1] - m[i]) for i in c if i % n < n - 1 and i + 1 in m]
        dy = [np.linalg.norm(m[i + n] - m[i]) for i in c if i + n in m]
        if not dx or not dy: continue
        cen = X.mean(0); nrm = np.linalg.svd(X - cen)[2][2]
        tilt = np.degrees(np.arccos(abs(nrm[2])))
        plane = abs(cen @ nrm)
        planarity = np.sqrt(np.mean(((X - cen) @ nrm) ** 2))
        u, v = np.mean(bl['pts'], 0)
        sx = np.median(dx) * 1000; sy = np.median(dy) * 1000
        rows.append(dict(recording=rec, session=sess, board=kind, frame=a['f'], t_s=a['f'] / 30,
                         corners=len(c), u_px=u, v_px=v, r_px=np.hypot(u - CX, v - CY),
                         depth_z_m=cen[2], plane_dist_m=plane, tilt_deg=tilt, planarity_rms_mm=planarity * 1000,
                         square_x_mm=sx, square_y_mm=sy,
                         scale_err_x_pct=(sx / RULER[kind]['x'] - 1) * 100,
                         scale_err_y_pct=(sy / RULER[kind]['y'] - 1) * 100))
df = pd.DataFrame(rows)
df['scale_err_pct'] = (df.scale_err_x_pct + df.scale_err_y_pct) / 2
df.round(4).to_csv(f'{OUT}/a1_per_frame.csv', index=False)

# central, near-frontal subset: board centre within 300 px of principal point, tilt < 15 deg
cen = df[(df.r_px < 300) & (df.tilt_deg < 15)]
bins = np.arange(0.20, 1.00, 0.10)
summ = []
for kind in ['a4', 'far']:
    d = cen[cen.board == kind]
    for lo in bins:
        s = d[(d.depth_z_m >= lo) & (d.depth_z_m < lo + 0.10)]
        if len(s) < 20: continue
        e = s.scale_err_pct.values
        boot = [np.median(np.random.default_rng(k).choice(e, len(e))) for k in range(500)]
        summ.append(dict(board=kind, region='center_frontal', depth_bin_m=f'{lo:.1f}-{lo+0.1:.1f}', n_frames=len(s),
                         median_depth_m=s.depth_z_m.median(), median_scale_err_pct=np.median(e),
                         iqr_low_pct=np.percentile(e, 25), iqr_high_pct=np.percentile(e, 75),
                         boot95_low_pct=np.percentile(boot, 2.5), boot95_high_pct=np.percentile(boot, 97.5),
                         median_planarity_mm=s.planarity_rms_mm.median()))
# edge subset: board centre beyond 450 px from principal point horizontally
edge = df[(abs(df.u_px - CX) > 450)]
for kind in ['a4', 'far']:
    for side, s in [('left_edge', edge[(edge.board == kind) & (edge.u_px < CX)]), ('right_edge', edge[(edge.board == kind) & (edge.u_px > CX)])]:
        if len(s) < 20: continue
        e = s.scale_err_pct.values
        summ.append(dict(board=kind, region=side, depth_bin_m='all', n_frames=len(s), median_depth_m=s.depth_z_m.median(),
                         median_scale_err_pct=np.median(e), iqr_low_pct=np.percentile(e, 25), iqr_high_pct=np.percentile(e, 75),
                         boot95_low_pct=np.nan, boot95_high_pct=np.nan, median_planarity_mm=s.planarity_rms_mm.median(),
                         median_tilt_deg=s.tilt_deg.median(), median_u_px=s.u_px.median()))
pd.DataFrame(summ).round(4).to_csv(f'{OUT}/a1_scale_summary.csv', index=False)

# tape holds (manually set windows from the 1.5 s timeline; tape zero on the wall, rig hand-held)
HOLDS = {'145446_00000': [(30, 3, 6), (40, 7.5, 10.5), (50, 12, 15), (60, 17.5, 19.5), (70, 21, 24), (80, 26, 30), (90, 32.5, 34.5)],
         '145221_00000': [(30, 4, 12), (40, 24, 30), (50, 33, 39)]}
hold_rows = []
for rec, hl in HOLDS.items():
    d = df[df.recording == rec]
    for tape, t0, t1 in hl:
        s = d[(d.t_s >= t0) & (d.t_s < t1)]
        hold_rows.append(dict(recording=rec, board=s.board.iloc[0], tape_cm=tape, t_start_s=t0, t_end_s=t1, n_frames=len(s),
                              stereo_plane_cm=s.plane_dist_m.median() * 100, stereo_plane_sd_mm=s.plane_dist_m.std() * 1000,
                              tape_minus_stereo_cm=tape - s.plane_dist_m.median() * 100, median_tilt_deg=s.tilt_deg.median()))
H = pd.DataFrame(hold_rows)
for rec in H.recording.unique():
    h = H[H.recording == rec]
    a, b = np.polyfit(h.tape_cm, h.stereo_plane_cm, 1)
    H.loc[H.recording == rec, 'fit_slope'] = a; H.loc[H.recording == rec, 'fit_offset_cm'] = b
    H.loc[H.recording == rec, 'fit_residual_cm'] = h.stereo_plane_cm - (a * h.tape_cm + b)
H.round(3).to_csv(f'{OUT}/a1_tape_holds.csv', index=False)
print(pd.DataFrame(summ).round(3).to_string()); print(H.round(2).to_string())
print('frames total', len(df), 'central-frontal', len(cen))
