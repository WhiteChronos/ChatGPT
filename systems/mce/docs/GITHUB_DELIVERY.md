# MCE repository integration and release gates

The complete independent MCE workflow is maintained in `systems/mce/`, including the Python execution engine, P&ID adapters, synthetic examples, tests and specifications. Global skill entrypoints in `.agents/skills/` are byte-identical to the local MCE skill files and are checked by CI. No models, Excel templates or project input files are published here.

Local QA: `python -m pip install -r systems/mce/requirements.txt && python -m pytest -q systems/mce/tests`. Human authorizations remain mandatory; a passed CI job never permits automatically writing a project matrix.

The GitHub PR only publishes code and docs. Activation as a registered ChatGPT Web Skill is a separate client-side action and requires observed tool discovery. MCE has no dependency on REA or its MCP runtime.
