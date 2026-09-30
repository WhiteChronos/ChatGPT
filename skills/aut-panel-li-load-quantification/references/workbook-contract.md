# Step 4 Workbook Contract

For each PANEL_ID create exactly:
1. <PANEL_ID>_MATERIAIS
2. <PANEL_ID>_CARGA

No cover, control, references, architecture, QA or hidden support sheets are allowed in the issued workbook. Traceability lives in columns of the two allowed sheets and in canonical Data Center artifacts.

## Materials sheet minimum columns
PROJECT_NUMBER, PANEL_ID, REVISION, ITEM, TAG, CATEGORY, MANUFACTURER, MODEL, CATALOG_ID, DESCRIPTION, QUANTITY, UNIT, QUANTITY_METHOD, QUANTITY_FORMULA_OR_TRACE_ID, DIMENSIONS_MM, MOUNTING, VOLTAGE, CURRENT_OR_POWER, SOURCE_REF_ID, OFFICIAL_PRODUCT_URL, DATASHEET_MANUAL_URL, AUTHORIZED_SUPPLIER_URL, LIFECYCLE_STATUS, NOTES.

Linear items use m as unit and must reference route/geometry trace.

## Load sheet minimum columns
PROJECT_NUMBER, PANEL_ID, REVISION, LOAD_TAG, DESCRIPTION, MANUFACTURER, MODEL, QUANTITY, SUPPLY_VOLTAGE, NOMINAL_CURRENT_A, NOMINAL_POWER_W, DUTY_OR_DIVERSITY, RAW_CURRENT_A, RAW_POWER_W, DESIGN_CURRENT_A, DESIGN_POWER_W, UPS_CRITICAL, HEAT_LOSS_W, SOURCE_REF_ID, OFFICIAL_URL, NOTES.

Use spreadsheet formulas for totals and derived quantities where supported.
