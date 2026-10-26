#!/usr/bin/env python3
"""Render an orthographic solid isometric reference from STEP for visibility QA."""
from __future__ import annotations
import argparse, math
import cadquery as cq
import vtk

def poly_from_shape(shape, tol):
    verts, tris = shape.tessellate(tol)
    pts = vtk.vtkPoints(); cells = vtk.vtkCellArray()
    for v in verts:
        pts.InsertNextPoint(float(v.x), float(v.y), float(v.z))
    for tri in tris:
        t = vtk.vtkTriangle()
        for i in range(3):
            t.GetPointIds().SetId(i, int(tri[i]))
        cells.InsertNextCell(t)
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    clean = vtk.vtkCleanPolyData(); clean.SetInputData(pd); clean.Update()
    normals = vtk.vtkPolyDataNormals(); normals.SetInputData(clean.GetOutput())
    normals.ConsistencyOn(); normals.AutoOrientNormalsOn(); normals.SplittingOff(); normals.Update()
    return normals.GetOutput()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("step"); ap.add_argument("--out",required=True)
    ap.add_argument("--direction",default="1,-1,1"); ap.add_argument("--size",type=int,default=1200)
    ap.add_argument("--tess",type=float,default=0.15); ap.add_argument("--feature-angle",type=float,default=40.0)
    a=ap.parse_args()
    d=tuple(float(x) for x in a.direction.split(",")); n=math.sqrt(sum(x*x for x in d)); d=tuple(x/n for x in d)
    shape=cq.importers.importStep(a.step).val(); poly=poly_from_shape(shape,a.tess)
    ren=vtk.vtkRenderer(); ren.SetBackground(1,1,1)
    mapper=vtk.vtkPolyDataMapper(); mapper.SetInputData(poly)
    actor=vtk.vtkActor(); actor.SetMapper(mapper); actor.GetProperty().SetColor(0.92,0.92,0.92); actor.GetProperty().EdgeVisibilityOff(); ren.AddActor(actor)
    feat=vtk.vtkFeatureEdges(); feat.SetInputData(poly); feat.BoundaryEdgesOn(); feat.FeatureEdgesOn(); feat.NonManifoldEdgesOff(); feat.ManifoldEdgesOff(); feat.SetFeatureAngle(a.feature_angle); feat.Update()
    fm=vtk.vtkPolyDataMapper(); fm.SetInputConnection(feat.GetOutputPort()); fa=vtk.vtkActor(); fa.SetMapper(fm); fa.GetProperty().SetColor(0.25,0.25,0.25); fa.GetProperty().SetLineWidth(1.0); ren.AddActor(fa)
    b=poly.GetBounds(); c=((b[0]+b[1])/2,(b[2]+b[3])/2,(b[4]+b[5])/2); span=max(b[1]-b[0],b[3]-b[2],b[5]-b[4]); dist=max(span*5,1.0)
    cam=ren.GetActiveCamera(); cam.ParallelProjectionOn(); cam.SetFocalPoint(*c); cam.SetPosition(c[0]+d[0]*dist,c[1]+d[1]*dist,c[2]+d[2]*dist); cam.SetViewUp(0,0,1)
    sil=vtk.vtkPolyDataSilhouette(); sil.SetInputData(poly); sil.SetCamera(cam); sil.SetEnableFeatureAngle(False); sil.Update()
    sm=vtk.vtkPolyDataMapper(); sm.SetInputConnection(sil.GetOutputPort()); sa=vtk.vtkActor(); sa.SetMapper(sm); sa.GetProperty().SetColor(0,0,0); sa.GetProperty().SetLineWidth(2.0); ren.AddActor(sa)
    ren.ResetCamera(); cam.ParallelProjectionOn()
    rw=vtk.vtkRenderWindow(); rw.SetOffScreenRendering(1); rw.AddRenderer(ren); rw.SetSize(a.size,a.size); rw.Render()
    w2i=vtk.vtkWindowToImageFilter(); w2i.SetInput(rw); w2i.Update(); wr=vtk.vtkPNGWriter(); wr.SetFileName(a.out); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write()
    print(a.out)
if __name__=="__main__": main()
