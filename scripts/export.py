import sys,os,json,base64,numpy as np,nibabel as nib
ct,outd,site=sys.argv[1:4]
d=nib.load(ct).get_fdata();m=np.load(os.path.join(outd,'masks.npz'));meta=json.load(open(os.path.join(outd,'labels.json')))
body=(d>0).any(2);xs=np.where(body.any(1))[0];ys=np.where(body.any(0))[0]
X0,X1,Y0,Y1=max(xs[0]-2,0),min(xs[-1]+3,d.shape[0]),max(ys[0]-2,0),min(ys[-1]+3,d.shape[1])
c=np.clip(np.round(d[X0:X1,Y0:Y1,:]),0,255).astype(np.uint8)
# order: x fastest, then y, then z
open(os.path.join(site,'ct.bin'),'wb').write(np.ascontiguousarray(c.transpose(2,1,0)).tobytes())
structs=[]
for s in meta:
    M=m[s['id']][X0:X1,Y0:Y1,:]
    if not M.any(): continue
    ix=np.where(M.any((1,2)))[0];iy=np.where(M.any((0,2)))[0];iz=np.where(M.any((0,1)))[0]
    b=M[ix[0]:ix[-1]+1,iy[0]:iy[-1]+1,iz[0]:iz[-1]+1].transpose(2,1,0)
    bits=np.packbits(b.ravel(),bitorder='little')
    cen=[int(np.round(v.mean())) for v in np.nonzero(M)]
    structs.append(dict(g=s['g'],id=s['id'],name=s['name'],color=s['color'],bbox=[int(ix[0]),int(ix[-1]),int(iy[0]),int(iy[-1]),int(iz[0]),int(iz[-1])],
      center=cen,vol=round(float(M.sum())*3/1000,1),bits=base64.b64encode(bits.tobytes()).decode()))
json.dump(dict(dims=list(c.shape),spacing=[1,1,3],structs=structs),open(os.path.join(site,'ctv.json'),'w'),ensure_ascii=False)
print(c.shape,os.path.getsize(os.path.join(site,'ct.bin')),os.path.getsize(os.path.join(site,'ctv.json')))
