---
name: demo-iri-facility-api
description: Query the IRI Facility API demo adapter (facility, status resources, account whoami). Example skill showing how a facility publishes Agent Skills via GET /api/v2/skills.
category: research
required_environment_variables:
  - name: IRI_API_URL
    prompt: IRI Facility API base URL
    help: "Defaults to http://127.0.0.1:8000/api/v2"
    optional: true
  - name: IRI_API_TOKEN
    prompt: IRI Facility API bearer token
    help: "The demo adapter accepts the fixed demo key 12345"
    optional: true
---

# IRI Facility API demo

This skill talks to the IRI Facility API demo adapter. It is an example of a facility-published
skill: the whole bundle, including `scripts/`, is returned by
`GET /api/v2/skills/demo-iri-facility-api`. Write every entry of `files[]` to disk at its `path`
(decode `base64` entries, keep `executable`); script paths below are relative to this skill directory.

- **Base URL:** `$IRI_API_URL`, default `http://127.0.0.1:8000/api/v2`
- **Auth:** `Authorization: Bearer $IRI_API_TOKEN` (demo key `12345`, user `gtorok`).
  `/facility` and `/status` are public.
- **Helper:** `scripts/demo_iri_client.py` (stdlib only).

## Usage

    python3 scripts/demo_iri_client.py facility     # GET /facility
    python3 scripts/demo_iri_client.py resources    # GET /status/resources (name, type, status)
    python3 scripts/demo_iri_client.py whoami       # GET /account/whoami (needs a token)

## Notes

- The demo data is fake and resets on restart; do not treat it as a real facility.
- Never print the bearer token.
