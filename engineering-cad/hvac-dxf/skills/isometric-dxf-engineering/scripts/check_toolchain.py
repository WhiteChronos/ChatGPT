#!/usr/bin/env python3
import importlib.util, shutil, json
mods=['cadquery','OCP','ezdxf','trimesh']
cmds=['FreeCADCmd','freecadcmd','freecad','blender','openscad']
print(json.dumps({'python_modules':{m:bool(importlib.util.find_spec(m)) for m in mods},'commands':{c:shutil.which(c) for c in cmds}},indent=2))
