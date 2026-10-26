# Agent Foundation

This is a reusable starter repository. Keep business rules and product data out of `src/agent_foundation`.

- Preserve server-side model and voice key references. Never put literal credentials in `MODEL_CONFIG_JSON`, generated YAML, logs, tests, or browser responses.
- Bind wiki access to a server-resolved owner. New multi-user apps must replace the default local identity resolver and add their own authorization tests.
- New DeerFlow tools require an authorization provider, an explicit allowed tool list, and per-run grants.
- Keep local and external Compose paths independently runnable. Do not overwrite `.env` or `.runtime` during setup.
- Run `PYTHONPATH=src .venv/bin/python -m unittest discover -s tests` after installing the project in a Python 3.12 virtual environment.
