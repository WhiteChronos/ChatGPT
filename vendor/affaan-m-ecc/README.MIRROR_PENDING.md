# ECC upstream mirror

This directory is managed by `.github/workflows/sync-ecc-mirror.yml`.

After the integration lands on `main`, the workflow replaces this placeholder with a read-only byte mirror of `https://github.com/affaan-m/ECC` and writes `.whitechronos-mirror.json`.

The official upstream Codex plugin remains the runtime source of truth. Do not execute files from this mirror merely because they are present here.
