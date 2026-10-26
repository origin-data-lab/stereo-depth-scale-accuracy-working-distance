"""Figures for Field Notes #09-#12 from the derived CSVs in out/."""
import os, json, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
FIG = os.path.join(OUT, 'figures'); os.makedirs(FIG, exist_ok=True)
C1, C2, GR, INK = '#1f5fbf', '#d9622b', '#8a8f98', '#1d232b'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10.5, 'axes.edgecolor': '#c9ced6', 'axes.labelcolor': INK,
                     'xtick.color': INK, 'ytick.color': INK, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#e7eaee', 'grid.linewidth': 0.8, 'figure.dpi': 150, 'savefig.bbox': 'tight'})
def save(fig, name):
    fig.savefig(f'{FIG}/{name}.png', dpi=170); fig.savefig(f'{FIG}/{name}.svg'); plt.close(fig)

# ---------- #09 depth scale ----------
S = pd.read_csv(f'{OUT}/a1_scale_summary.csv'); cen = S[S.region == 'center_frontal']
fig, ax = plt.subplots(figsize=(7.2, 4.0))
for kind, col, lab, off in [('a4', C1, 'A4 target (29.17 mm squares)', -0.006), ('far', C2, 'Far target (53.4 mm squares)', 0.006)]:
    d = cen[cen.board == kind]
    x = d.median_depth_m + off
    ax.fill_between(x, d.iqr_low_pct, d.iqr_high_pct, color=col, alpha=0.12, lw=0)
    ax.errorbar(x, d.median_scale_err_pct, yerr=[d.median_scale_err_pct - d.boot95_low_pct, d.boot95_high_pct - d.median_scale_err_pct],
                fmt='o-', color=col, ms=5, lw=1.6, capsize=3, label=lab)
ax.axhline(0, color=INK, lw=0.8)
ax.axhspan(-0.19, 0.19, color=GR, alpha=0.15, lw=0, label='Ruler reading tolerance (±0.5 mm / span)')
ax.set_xlabel('Distance from left camera (m)'); ax.set_ylabel('Stereo scale error vs ruler (%)')
ax.set_ylim(-1.5, 0.8); ax.legend(frameon=False, fontsize=9, loc='lower left')
ax.set_title('Stereo scale error, board near image centre and near-frontal', loc='left', fontsize=11, color=INK)
save(fig, 'fn09_scale_error_vs_distance')

H = pd.read_csv(f'{OUT}/a1_tape_holds.csv')
fig, ax = plt.subplots(figsize=(6.2, 4.2))
for rec, col, lab in [('145446_00000', C2, 'Far target session'), ('145221_00000', C1, 'A4 target session')]:
    h = H[H.recording == rec]
    ax.plot(h.tape_cm, h.stereo_plane_cm, 'o', color=col, ms=6, label=lab)
    xx = np.array([28, 92]); ax.plot(xx, h.fit_slope.iloc[0] * xx + h.fit_offset_cm.iloc[0], '-', color=col, lw=1.2, alpha=0.8)
ax.plot([25, 95], [25, 95], '--', color=GR, lw=1, label='tape = stereo')
ax.set_xlabel('Tape reading, zero at wall (cm)'); ax.set_ylabel('Stereo distance to board plane (cm)')
ax.legend(frameon=False, fontsize=9); ax.set_title('Tape vs stereo: constant offset, consistent steps', loc='left', fontsize=11)
save(fig, 'fn09_tape_vs_stereo')

ed = S[S.region != 'center_frontal']
fig, ax = plt.subplots(figsize=(8.4, 3.9))
labels = []; vals = []; lo = []; hi = []; cols = []
for kind, col in [('a4', C1), ('far', C2)]:
    c = cen[cen.board == kind]
    labels.append(f'{kind.upper()}\ncentre\n<0.5 m'); v = c[c.median_depth_m < 0.5]
    vals.append(v.median_scale_err_pct.median()); lo.append(v.iqr_low_pct.median()); hi.append(v.iqr_high_pct.median()); cols.append(col)
    for side in ['left_edge', 'right_edge']:
        e = ed[(ed.board == kind) & (ed.region == side)].iloc[0]
        labels.append(f'{kind.upper()}\n{side.split("_")[0]} edge\ntilt ~{e.median_tilt_deg:.0f}°'); vals.append(e.median_scale_err_pct)
        lo.append(e.iqr_low_pct); hi.append(e.iqr_high_pct); cols.append(col)
x = np.arange(len(vals))
ax.bar(x, vals, color=[c for c in cols], alpha=0.85, width=0.62)
ax.errorbar(x, vals, yerr=[np.array(vals) - np.array(lo), np.array(hi) - np.array(vals)], fmt='none', ecolor=INK, capsize=3, lw=1)
ax.axhline(0, color=INK, lw=0.8); ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8.5)
for xi, v in zip(x, vals): ax.text(xi + 0.33, v + (0.25 if v >= 0 else -0.6), f'{v:+.1f}%', fontsize=8.5, color=INK)
ax.set_ylabel('Scale error (%) — median, IQR'); ax.set_title('Image centre vs image edges', loc='left', fontsize=11)
save(fig, 'fn09_centre_vs_edges')

# ---------- #10 sync / IMU ----------
TS = pd.read_csv(f'{OUT}/a2_timestamp_integrity.csv')
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from odl_calib import DATA
d_all = []
for rec in TS.recording:
    L = np.load(f'{DATA}/svh_20261026_{rec}_left.npy'); R = np.load(f'{DATA}/svh_20261026_{rec}_right.npy'); k = min(len(L), len(R))
    d_all.append((R[:k, 1] + R[:k, 2] / 2) - (L[:k, 1] + L[:k, 2] / 2))
d_all = np.concatenate(d_all)
fig, ax = plt.subplots(figsize=(6.4, 3.4))
ax.hist(np.clip(d_all, 0, 80), bins=np.arange(0, 81, 1), color=C1, alpha=0.85)
ax.set_yscale('log'); ax.set_xlabel('Right − left exposure-centre time (µs), clipped at 80 µs'); ax.set_ylabel('Frames (log)')
ax.set_title(f'Stereo exposure alignment, {len(d_all):,} frame pairs', loc='left', fontsize=11)
ax.text(0.98, 0.92, f'median {np.median(d_all):.1f} µs\n>80 µs: {np.mean(np.abs(d_all)>80)*100:.1f}% of pairs\nmax {np.abs(d_all).max()/1000:.2f} ms', transform=ax.transAxes, ha='right', va='top', fontsize=9, color=INK)
save(fig, 'fn10_stereo_sync_histogram')

C = pd.read_csv(f'{OUT}/a2_camimu_offset_curve.csv'); res = json.load(open(f'{OUT}/a2_camimu_result.json'))['145719_00000']
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.plot(C.offset_ms, C.residual_median_deg, 'o-', color=C1, ms=3.5, lw=1.5)
ax.axvline(res['factory_timeshift_cam0_ms'], color=C2, ls='--', lw=1.2, label=f"factory time shift {res['factory_timeshift_cam0_ms']:.2f} ms")
ax.axvspan(*res['offset_within_10pct_ms'], color=C1, alpha=0.10, lw=0, label='within 10% of minimum')
ax.set_xlabel('Camera→IMU time offset tested (ms)'); ax.set_ylabel('Median rotation residual (deg)')
ax.legend(frameon=False, fontsize=9); ax.set_title('Gyro vs camera rotation agreement over time offset', loc='left', fontsize=11)
save(fig, 'fn10_camimu_offset_curve')

# ---------- #11 calibration validation ----------
G = pd.read_csv(f'{OUT}/a3_residual_grid.csv')
fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
for ax, model, ttl in [(axs[0], 'factory', 'Factory calibration'), (axs[1], 'odl_recalibration', 'ODL recalibration (our frames)')]:
    g = G[G.model == model].pivot(index='cell_row', columns='cell_col', values='epi_median_px').values
    im = ax.imshow(np.clip(g, 0, 3), cmap='viridis', vmin=0, vmax=3, extent=[0, 1600, 1200, 0])
    for i in range(6):
        for j in range(8):
            if not np.isnan(g[i, j]): ax.text(j * 200 + 100, i * 200 + 100, f'{g[i,j]:.1f}' if g[i, j] < 10 else '>10', ha='center', va='center', fontsize=7.5, color='white' if g[i, j] < 2 else INK)
    ax.set_title(ttl, loc='left', fontsize=10.5); ax.set_xticks([0, 400, 800, 1200, 1600]); ax.set_yticks([0, 300, 600, 900, 1200]); ax.grid(False)
cb = fig.colorbar(im, ax=axs, shrink=0.85); cb.set_label('Median epipolar distance (px), clipped at 3')
fig.suptitle('Stereo epipolar residual by image region (1600×1200, blank = <30 points)', x=0.06, ha='left', fontsize=11)
save(fig, 'fn11_epipolar_residual_map')

Rr = pd.read_csv(f'{OUT}/a3_residual_by_radius.csv')
fig, ax = plt.subplots(figsize=(6.6, 3.8)); xs = np.arange(5)
for model, col, lab in [('factory', C1, 'Factory'), ('odl_recalibration', C2, 'ODL recalibration')]:
    r = Rr[Rr.model == model]
    ax.plot(xs, r.epi_median_px, 'o-', color=col, lw=1.6, label=f'{lab} — epipolar')
    ax.plot(xs, r.rep_median_px, 's--', color=col, lw=1.2, alpha=0.7, label=f'{lab} — reprojection (left)')
ax.set_xticks(xs); ax.set_xticklabels([f'{x} px' for x in Rr.radius_px.unique()]); ax.set_yscale('log')
ax.set_xlabel('Radius from principal point'); ax.set_ylabel('Median residual (px, log)'); ax.legend(frameon=False, fontsize=8.5)
ax.set_title('Residuals grow toward the fisheye periphery', loc='left', fontsize=11)
save(fig, 'fn11_residual_by_radius')

# ---------- #12 detection limits ----------
CP = pd.read_csv(f'{OUT}/a4_completeness_vs_marker_px.csv')
fig, ax = plt.subplots(figsize=(6.6, 3.8))
for kind, col, lab, full in [('a4', C1, 'A4 target (9×6, 40 corners)', 40), ('far', C2, 'Far target (5×3, 8 corners)', 8)]:
    c = CP[(CP.board == kind) & (CP.n >= 50)]
    mids = [np.mean([float(v) for v in b.strip('(]').split(',')]) for b in c.marker_px_bin]
    ax.plot(mids, c.median_corners / full * 100, 'o-', color=col, lw=1.6, label=lab)
ax.set_xscale('log'); ax.set_xticks([10, 14, 18, 22, 27, 35, 50, 90]); ax.set_xticklabels(['10', '14', '18', '22', '27', '35', '50', '90'])
ax.set_xlabel('Marker side in image (px, left camera)'); ax.set_ylabel('Median corners found (% of board)')
ax.axvspan(8, 16, color=GR, alpha=0.15, lw=0); ax.text(9, 50, 'decode\nfails', fontsize=8.5, color=INK)
ax.legend(frameon=False, fontsize=9, loc='lower right'); ax.set_title('Corner yield vs marker size in pixels', loc='left', fontsize=11)
save(fig, 'fn12_corners_vs_marker_px')

TL = pd.read_csv(f'{OUT}/a4_distance_timeline.csv')
fig, axs = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=False); fig.subplots_adjust(hspace=0.55)
for ax, rec, col, ttl, full in [(axs[0], '145221_00000', C1, 'A4 target, tape 30→90 cm', 40), (axs[1], '145446_00000', C2, 'Far target, tape 30→90 cm', 8)]:
    t = TL[TL.recording == rec]
    ax.bar(t.t_start_s + 0.75, t.mean_corners / full * 100, width=1.4, color=col, alpha=0.85)
    for _, r in t.iterrows():
        if not np.isnan(r.stereo_dist_m) and r.mean_corners > 0.5 and int(r.t_start_s / 1.5) % 3 == 0:
            ax.text(r.t_start_s + 0.75, min(r.mean_corners / full * 100, 100) + 4, f'{r.stereo_dist_m*100:.0f}', ha='center', fontsize=7, color=INK)
    ax.set_ylim(0, 118); ax.set_ylabel('corners %'); ax.set_title(ttl + ' (labels: stereo cm)', loc='left', fontsize=10)
axs[1].set_xlabel('Recording time (s)')
save(fig, 'fn12_distance_timeline')
print('figures written to', FIG)
