#!/usr/bin/env sh
set -eu
DEST=${1:-vendor/automation-engineering}; mkdir -p "$DEST"
clone(){ r=$1; n=$2; [ -d "$DEST/$n/.git" ] || git clone --depth 1 "https://github.com/$r.git" "$DEST/$n"; }
clone sympy/sympy sympy
clone scipy/scipy scipy
clone hgrecco/pint pint
clone networkx/networkx networkx
clone shapely/shapely shapely
clone opencv/opencv opencv
clone LibreDWG/libredwg libredwg
clone LibreCAD/LibreCAD librecad
clone mozman/ezdxf ezdxf
clone jsvine/pdfplumber pdfplumber
clone ocrmypdf/OCRmyPDF ocrmypdf
