# Font Fidelity Setup for Engineering Documents

## Purpose

Use the exact fonts referenced by source Word documents when validating layout, pagination, line wrapping or sheet-specific placement.

The public repository intentionally does **not** contain proprietary font binaries.

## Exact sources

### Petrobras Sans

Official Petrobras source:
- https://petrobras.com.br/quem-somos/nossa-marca

Petrobras states that its visual identity uses an exclusive typography and routes brand manuals/assets through the Petrobras Brand Content Library. Obtain the Petrobras Sans family only through an authorized Petrobras/corporate source.

Do not download or commit third-party copies from font-sharing sites.

### Microsoft fonts

Use fonts from a licensed Windows/Office installation or other authorized Microsoft/Monotype license.

Official Microsoft typography references:
- Arial: https://learn.microsoft.com/en-us/typography/font-list/arial
- Arial Black: https://learn.microsoft.com/en-us/typography/font-list/arial-black
- Courier New: https://learn.microsoft.com/en-us/typography/font-list/courier-new
- Wingdings: https://learn.microsoft.com/en-us/typography/font-list/wingdings
- Trebuchet MS: https://learn.microsoft.com/en-us/typography/font-list/trebuchet-ms
- Windows 11 font inventory: https://learn.microsoft.com/en-us/typography/fonts/windows_11_font_list

## Current source-document families observed

The source Word documents reviewed in this workflow reference families from this set:

- Petrobras Sans
- Arial
- Arial Black
- Calibri
- Calibri Light
- Courier New
- Times New Roman
- Wingdings
- Tahoma
- Symbol

Not every family is necessarily used for visible Portuguese body text; some may be style/font-table references. For exact fidelity, retain the source font set rather than guessing which references are harmless.

## Private font directory

Place licensed local font files in a directory outside version control, for example:

```text
private_fonts/
```

This path is ignored by Git.

Check a document:

```bash
python pipeline/font_fidelity_gate.py document.docx \
  --font-dir private_fonts \
  --layout-sensitive
```

Render with the same private font set:

```bash
pipeline/with_private_fonts.sh private_fonts \
  libreoffice --headless --convert-to pdf --outdir /tmp/render document.docx
```

## Petrobras Sans fallback

Historical Petrobras/Transpetro identity guidance identifies **Trebuchet MS** as a support font under technical restriction.

This fallback may be used for readable non-fidelity output only. It is **not** accepted as an exact-layout substitute and cannot be used to validate Word pagination against a Petrobras Sans source document.

## Gate behavior

- `EXACT_AVAILABLE`: exact family is available.
- `MISSING_EXACT`: exact required family is unavailable.
- `UNMANAGED_FONT_REFERENCE`: source refers to a family absent from the governed manifest.
- `NOT_VERIFIABLE_FROM_RENDER`: layout-sensitive conclusions are blocked until exact fonts are available or a native Word/PDF export confirms the layout.

## Security and licensing

Never commit proprietary font binaries to this public repository. CI validates the font manifest, gate logic and synthetic fixtures only. Exact-font rendering is expected on an authorized workstation/runner or with a secure private-font mount.
