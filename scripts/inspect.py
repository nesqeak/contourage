import sys,glob,os,nibabel as nib,numpy as np
fs=sorted(glob.glob(os.path.join(sys.argv[1],'*.nii.gz')),key=lambda p:int(os.path.basename(p).split('.')[0]))
shapes={}
for f in fs:
    im=nib.load(f); k=(im.shape,tuple(np.round(im.header.get_zooms(),2)))
    shapes.setdefault(k,[]).append(os.path.basename(f))
for k,v in shapes.items(): print(k,len(v))
for f in fs[:3]:
    d=nib.load(f).get_fdata(); print(os.path.basename(f),d.dtype,d.min(),d.max(),np.percentile(d,[1,50,99]))
print(nib.aff2axcodes(nib.load(fs[0]).affine))
