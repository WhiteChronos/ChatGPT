# Step 6 Document Composition Contract

Required inputs:
PROJECT_NUMBER, PANEL_ID, REVISION, Step 5 image/assembly fingerprint, frozen H_MM/W_MM/D_MM, LI/load revision, electrical topology revision, communication topology revision, command/I/O logic revision, MODEL 001 composition revision.

Required block types:
PHYSICAL_VIEW, LEGEND, PANEL_DATA, ELECTRICAL_ARCHITECTURE, COMMUNICATION_ARCHITECTURE, COMMAND_DIAGRAM, DIMENSIONING.

Grow-only rule:
Each block declares native width/height. The planner may reposition blocks and increase canvas extent. It may not reduce dimensional blocks.

For each dimensional physical view:
scale_x = 1.0
scale_y = 1.0
source fingerprint unchanged

The document fails if any block references a different panel revision, LI revision, geometry fingerprint or topology revision.
