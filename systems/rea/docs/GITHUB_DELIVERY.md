# REA repository integration and release gates

The internal reverse engineering MCP server, static engine, Web-loopback interface, CLI, examples and tests live in `systems/rea/`, independent of the MCE product. This is an independently implemented static-analysis engine and is NOT a full copy of the official `morluto/rea` server.

Local QA: `python -m pip install -r systems/rea/requirements.txt && python -m pytest -q systems/rea/tests`.

Local authenticated MCP: export `REA_MCP_TOKEN` as an operator-generated secret and run `python systems/rea/src/server.py --transport http --root /authorized/data`; this binds only to loopback, not the Internet. ChatGPT Web requires a separately authorized HTTPS endpoint, access control and actual host discovery. Publishing to GitHub does not activate a Web app or create an MCP connection.
