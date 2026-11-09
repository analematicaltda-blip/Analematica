# UBL invoice reference schemas

These are unmodified reference resources mirrored by `phax/ph-ubl` and
`phax/ph-xsds`, with pinned commits and SHA-256 digests in `PROVENANCE.json`.
Original copyright notices, LICENSE and NOTICE files are retained.

The invoice header identifies **OASIS UBL 2.1 CS1, generated 2013-06-16**.
This is a structural test reference, **not qualification against the current
Colombian DIAN annex or a claim that this is its approved distribution**.

Only the transitive invoice schema closure and the declared CCTS/XMLDSIG/XAdES
schema dependencies are included. Some mirrored Java resources use namespace-only
imports. `FRONTEND/deployment/tests/validate_ubl_reference.py` supplies an explicit
local import catalog without modifying the resources or fetching remote schemas.

The presence of signature type definitions does not implement or validate fiscal
signatures. No executable code from the upstream repositories is run or vendored.
