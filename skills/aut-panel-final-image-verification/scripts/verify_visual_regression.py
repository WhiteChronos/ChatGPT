#!/usr/bin/env python3
import argparse,json,sys
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('baseline'); ap.add_argument('candidate'); ap.add_argument('--ssim-min',type=float,default=0.995); ap.add_argument('--output'); a=ap.parse_args()
    try:
        import cv2
        from skimage.metrics import structural_similarity
    except Exception as e:
        print(json.dumps({'status':'UNAVAILABLE','reason':str(e)},indent=2)); sys.exit(3)
    b=cv2.imread(a.baseline,cv2.IMREAD_GRAYSCALE); c=cv2.imread(a.candidate,cv2.IMREAD_GRAYSCALE)
    if b is None or c is None: raise SystemExit('Could not read image')
    if b.shape!=c.shape: result={'status':'FAIL','reason':'image dimensions differ'}
    else:
        score=float(structural_similarity(b,c,data_range=255)); result={'status':'PASS' if score>=a.ssim_min else 'FAIL','ssim':score,'threshold':a.ssim_min}
    out=json.dumps(result,indent=2); print(out)
    if a.output:
        with open(a.output,'w',encoding='utf-8') as f: f.write(out+'\n')
    sys.exit(0 if result['status']=='PASS' else 2)
if __name__=='__main__': main()
