import sys, os, json, numpy as np, nibabel as nib
from scipy import ndimage as ndi
from skimage.draw import polygon as skpoly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from structs import STRUCTS

ct_path, out_dir = sys.argv[1], sys.argv[2]
img = nib.load(ct_path); d = img.get_fdata(); X, Y, Z = d.shape
AIR, BONE = 60, 100

def raster(poly):
    m = np.zeros((X, Y), bool)
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    rr, cc = skpoly(np.array(xs), np.array(ys), shape=(X, Y))
    m[rr, cc] = True
    return m

def sdf(m):
    return ndi.distance_transform_edt(~m) - ndi.distance_transform_edt(m)

# os plein (corticale + médullaire) pour exclure la moelle osseuse des structures molles
solid = np.zeros(d.shape, bool)
for z in range(Z):
    solid[:, :, z] = ndi.binary_fill_holes(ndi.binary_closing(d[:, :, z] > BONE, iterations=2))
labels = np.zeros(d.shape, np.uint8)
masks = {}
for i, s in enumerate(STRUCTS, 1):
    M = np.zeros(d.shape, bool)
    if s.get('auto') == 'sphenoid':
        z0, z1 = s['z']
        box = np.zeros(d.shape, bool); box[96:142, 84:118, z0:z1 + 1] = True
        air = (d < AIR) & box
        lab, n = ndi.label(air)
        seed = lab[118, 100, 45]
        M = lab == seed if seed else air
        for z in range(Z):
            if M[:, :, z].any():
                M[:, :, z] = ndi.binary_fill_holes(ndi.binary_closing(M[:, :, z], iterations=2))
    else:
        keys = sorted(s['keys'])
        sd = {k: sdf(raster(s['keys'][k])) for k in keys}
        for z in range(keys[0], keys[-1] + 1):
            if z in sd:
                m = sd[z] <= 0
            else:
                k0 = max(k for k in keys if k < z); k1 = min(k for k in keys if k > z)
                t = (z - k0) / (k1 - k0)
                m = ((1 - t) * sd[k0] + t * sd[k1]) <= 0
            sl = d[:, :, z]
            mode = s.get('mode', 'soft')
            if mode == 'soft':
                m &= (sl >= AIR) & ~solid[:, :, z]
            elif mode == 'tissue':
                m &= sl >= AIR
            if mode != 'all':
                m = ndi.binary_opening(m, iterations=1) if m.sum() > 30 else m
            M[:, :, z] = m
    masks[s['id']] = M
    labels[M & (labels == 0)] = i
    zs = np.where(M.any((0, 1)))[0]
    print(f"{s['id']:18s} vox={M.sum():6d} vol={M.sum()*3/1000:6.1f} mL z={zs.min() if len(zs) else '-'}-{zs.max() if len(zs) else '-'}")

# exclusions entre niveaux (limites partagées)
for i, s in enumerate(STRUCTS, 1):
    for o in s.get('minus', []):
        masks[s['id']] &= ~masks[o]
labels[:] = 0
for i, s in enumerate(STRUCTS, 1):
    labels[masks[s['id']] & (labels == 0)] = i
np.savez_compressed(os.path.join(out_dir, 'masks.npz'), **masks)
nib.save(nib.Nifti1Image(labels, img.affine), os.path.join(out_dir, 'ctv_labels.nii.gz'))
json.dump([{'label': i, 'id': s['id'], 'name': s['name'], 'color': s['color'], 'g': s['g']} for i, s in enumerate(STRUCTS, 1)],
          open(os.path.join(out_dir, 'labels.json'), 'w'), ensure_ascii=False, indent=1)
