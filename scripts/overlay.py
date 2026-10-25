import sys, os, json, numpy as np, nibabel as nib, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
ct, outd, png, zs = sys.argv[1], sys.argv[2], sys.argv[3], [int(z) for z in sys.argv[4].split(',')]
d = nib.load(ct).get_fdata(); masks = np.load(os.path.join(outd, 'masks.npz'))
meta = json.load(open(os.path.join(outd, 'labels.json')))
if len(sys.argv) > 5: meta = [m for m in meta if m['g'] == sys.argv[5]]
x0, x1, y0, y1 = [int(v) for v in (sys.argv[6] if len(sys.argv) > 6 else '85,190,25,145').split(',')]
c = 2; r = (len(zs) + 1) // 2
fig, ax = plt.subplots(r, c, figsize=(9 * c, 9 * r * (y1 - y0) / (x1 - x0)))
for a in np.ravel(ax): a.axis('off')
for a, z in zip(np.ravel(ax), zs):
    a.imshow(d[x0:x1, y0:y1, z].T, cmap='gray', vmin=68.7, vmax=83.9, extent=[x0, x1, y1, y0], interpolation='nearest')
    for m in meta:
        M = masks[m['id']][x0:x1, y0:y1, z]
        if M.any():
            a.contour(np.arange(x0, x1) + .5, np.arange(y0, y1) + .5, M.T.astype(float), [.5], colors=[m['color']], linewidths=1.6)
            yy, xx = np.nonzero(M.T); a.text(xx.mean() + x0, yy.mean() + y0, m['id'][:10], color=m['color'], fontsize=8, ha='center')
    a.set_title(f'z={z}', fontsize=15); a.axis('on'); a.tick_params(labelsize=8)
plt.tight_layout(); plt.savefig(png, dpi=55)
