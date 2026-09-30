#!/usr/bin/env python3
import argparse,json,math,statistics,sys
def pct(a,b): return abs(float(a)/float(b)-1.0)*100.0 if float(b)!=0 else float('inf')
def mat_vec(P,X): return [sum(float(P[r][c])*float(X[c]) for c in range(4)) for r in range(3)]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('manifest'); ap.add_argument('--output'); a=ap.parse_args()
    with open(a.manifest,'r',encoding='utf-8') as f: m=json.load(f)
    c=m['canonical']; t=m.get('thresholds',{})
    aspect_tol=float(t.get('aspect_error_percent',0.25)); axis_tol=float(t.get('axis_scale_error_percent',0.25))
    common_tol=float(t.get('common_scale_error_percent',0.50)); reproj_tol=float(t.get('reprojection_rmse_px',1.5))
    min_margin=float(t.get('minimum_margin_px',20)); center_tol=float(t.get('center_margin_imbalance_fraction',0.05))
    errors=[]; checks=[]; scales=[]
    for v in m.get('views',[]):
        vid=v.get('view_id','UNKNOWN')
        if v.get('assembly_hash')!=c.get('assembly_hash'): errors.append(f'{vid}: assembly_hash mismatch')
        canvas=v.get('canvas_px',[0,0]); bbox=v.get('panel_bbox_px',[0,0,0,0])
        if len(canvas)!=2 or len(bbox)!=4: errors.append(f'{vid}: bad canvas/bbox'); continue
        cw,ch=map(float,canvas); x,y,bw,bh=map(float,bbox)
        lm,tm,rm,bm=x,y,cw-(x+bw),ch-(y+bh)
        if min(lm,tm,rm,bm)<min_margin: errors.append(f'{vid}: clipping/minimum margin violation')
        if v.get('framing_mode')=='centered':
            if abs(lm-rm)/max(lm,rm,1.0)>center_tol: errors.append(f'{vid}: horizontal framing imbalance')
            if abs(tm-bm)/max(tm,bm,1.0)>center_tol: errors.append(f'{vid}: vertical framing imbalance')
        axes=v.get('expected_axes')
        if v.get('projection')=='orthographic' and axes and len(axes)==2:
            xmm=float(c[axes[0]]); ymm=float(c[axes[1]])
            ae=pct(bw/bh,xmm/ymm); sx=bw/xmm; sy=bh/ymm; se=pct(sx,sy)
            checks.append({'view_id':vid,'aspect_error_percent':ae,'axis_scale_error_percent':se,'px_per_mm_x':sx,'px_per_mm_y':sy})
            scales.extend([sx,sy])
            if ae>aspect_tol: errors.append(f'{vid}: aspect error {ae:.4f}% > {aspect_tol}%')
            if se>axis_tol: errors.append(f'{vid}: axis px/mm mismatch {se:.4f}% > {axis_tol}%')
        labels=v.get('dimension_labels_mm',{})
        for label,key in [('H','h_mm'),('W','w_mm'),('D','d_mm')]:
            if label in labels and float(labels[label])!=float(c[key]): errors.append(f'{vid}: label {label} mismatch')
        for obj in v.get('object_scales',[]):
            s=obj.get('scale',[])
            if len(s)!=3 or any(abs(float(q)-1.0)>1e-9 for q in s): errors.append(f"{vid}: object {obj.get('id')} scale not [1,1,1]")
        P=v.get('projection_matrix_3x4'); lms=v.get('landmarks',[])
        if P and lms:
            sq=[]
            for p in lms:
                X=list(p['model_point_mm'])+[1.0] if len(p['model_point_mm'])==3 else p['model_point_mm']
                q=mat_vec(P,X)
                if abs(q[2])<1e-12: errors.append(f'{vid}: invalid projection depth'); continue
                u,vv=q[0]/q[2],q[1]/q[2]; ou,ov=map(float,p['image_point_px']); sq.append((u-ou)**2+(vv-ov)**2)
            if sq:
                rmse=math.sqrt(sum(sq)/len(sq)); checks.append({'view_id':vid,'reprojection_rmse_px':rmse})
                if rmse>reproj_tol: errors.append(f'{vid}: reprojection RMSE {rmse:.4f}px > {reproj_tol}px')
    common_scale=None
    if scales:
        common_scale=statistics.mean(scales); mx=max(pct(s,common_scale) for s in scales)
        if mx>common_tol: errors.append(f'cross-view common px/mm deviation {mx:.4f}% > {common_tol}%')
    result={'status':'PASS' if not errors else 'FAIL','errors':errors,'checks':checks,'common_px_per_mm':common_scale,'view_count':len(m.get('views',[]))}
    out=json.dumps(result,indent=2); print(out)
    if a.output:
        with open(a.output,'w',encoding='utf-8') as f: f.write(out+'\n')
    sys.exit(0 if not errors else 2)
if __name__=='__main__': main()
