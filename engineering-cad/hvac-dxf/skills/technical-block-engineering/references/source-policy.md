# Source Policy

## Core authority rule

Every technical block, dimensional reconstruction, CAD/BIM import, catalog reference, datasheet, supplier citation, or product selection must be tied to the **real manufacturer brand** and its own official channel.

Allowed source chain:

1. manufacturer official product page/domain;
2. manufacturer official CAD/BIM/download portal;
3. manufacturer official catalog/datasheet/manual/dimensional drawing;
4. distributor/partner explicitly listed or verifiable through the manufacturer's own official partner/distributor locator;
5. manufacturer-certified CAD catalog that preserves the original manufacturer identity and file provenance.

Anything else is only a lead until independently verified.

## Brand-locked supplier rule

A supplier is valid for a brand only when at least one of these is true:

- the supplier is the manufacturer itself;
- the supplier appears in the manufacturer's official distributor/partner locator;
- the manufacturer explicitly identifies the supplier as an authorized distributor/partner in an official page or document.

Do not accept a supplier because it:
- uses the manufacturer's logo;
- sells genuine-looking products;
- appears high in search results;
- is a marketplace seller;
- is described as a distributor only on its own website;
- republishes a datasheet without manufacturer authorization evidence.

If authorization cannot be verified from the brand itself, classify the source as `RESELLER` or `UNKNOWN` and do not use it as the technical authority for final geometry.

## Authority hierarchy

| Rank | Source | Can establish identity? | Can establish dimensions? | Can establish native geometry? |
|---|---|---:|---:|---:|
| A1 | Manufacturer native CAD/BIM + exact model match | yes | yes | yes |
| A2 | Manufacturer dimensional drawing/manual | yes | yes | reconstruct only |
| A3 | Manufacturer datasheet/catalog PDF | yes | yes when explicit | reconstruct only |
| A4 | Manufacturer product page | yes | only explicit values | no |
| B1 | Authorized distributor/partner verified by manufacturer locator, preserving manufacturer file | yes with cross-check | yes with cross-check | yes only if manufacturer file provenance is preserved |
| B2 | Manufacturer-certified CAD catalog preserving brand/model provenance | locator/cross-check | cross-check | yes when original manufacturer file identity is preserved |
| C1 | Engineering index/database | locator only | no | no |
| C2 | Unverified reseller / marketplace / forum / image page | lead only | no | no |

## Acceptance rules

- Match exact manufacturer + model/part number, not only family/series.
- Prefer manufacturer drawing number and revision.
- Treat regional variants as distinct until proven identical.
- Distinguish current from discontinued/legacy models.
- If two official manufacturer documents disagree, preserve both and resolve revision/date/region before selecting geometry.
- Project data sheets express project intent but do not silently override the manufacturer.
- Product photos are not dimensional drawings.
- A PDF without identifiable manufacturer/publisher, model, or revision is not sufficient for final geometry.
- A distributor copy of a document never outranks the original manufacturer document.
- When a brand has no verified partner locator available, use **manufacturer-direct sources only** until authorization is proven.

## Supplier classification

Use exactly one:
- `MANUFACTURER`
- `AUTHORIZED_DISTRIBUTOR`
- `AUTHORIZED_PARTNER`
- `SYSTEM_INTEGRATOR`
- `RESELLER`
- `UNKNOWN`

For `AUTHORIZED_DISTRIBUTOR` or `AUTHORIZED_PARTNER`, record:
- brand;
- official manufacturer locator/page URL;
- supplier name exactly as shown;
- country/region;
- date checked;
- evidence status.

## Search pattern

Search manufacturer/model combinations with:
- official product page;
- official datasheet PDF;
- dimensions / dimensional drawing / outline drawing;
- installation manual;
- technical data book;
- CAD / DXF / DWG;
- STEP / STP / IGES / IGS;
- BIM / RFA / IFC;
- mounting / foundation drawing;
- official distributor / partner locator.

## Default fail-safe

If the brand-to-supplier relationship is not verifiable from an official manufacturer source:

`SOURCE_STATUS = BLOCKED_FOR_FINAL_GEOMETRY`

The source may remain as a research lead but cannot support final DXF geometry, dimensions, or supplier authorization.
