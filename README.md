# anime-crosswalk-mappings

A licence-clean crosswalk between anime identifiers, with episode-level ranges and offsets.

Give it a MyAnimeList id, get back the correct TVDB season and episode range, so a client
can fetch the right episode records without a human working out that the offset is 12.

This is a crosswalk, not a database. It stores pointers, ranges and offsets. Every provider
remains the authority on its own descriptive metadata.

## What is here today

This repository currently contains the schema, the vocabulary, the namespace registry and
the governance model. **There is no published dataset yet.** The roadmap says when there
will be.

| Path | Contents |
|---|---|
| [`conformance/`](conformance/README.md) | 18 cases any correct anime crosswalk has to handle, and the 13 capabilities they require. Structure only, no identifiers, so other projects can run their own data against it |
| [`schema/release.schema.json`](schema/release.schema.json) | The Release entity, derived from those cases. JSON Schema 2020-12 |
| [`conformance/capability-map.json`](conformance/capability-map.json) | Which schema construct expresses each capability. Checked in CI, so "derived from the corpus" is falsifiable rather than asserted |
| [`conformance/fixtures.json`](conformance/fixtures.json) | Worked records for every capability, and records that must be rejected |
| [`GLOSSARY.md`](GLOSSARY.md) | The vocabulary. Every term used in the schema and the code is defined here once |
| [`schema/namespaces.json`](schema/namespaces.json) | Every provider namespace, its identifier format, its deep-link template, and its licence posture |
| [`schema/authorities.json`](schema/authorities.json) | Which organisations can make authoritative assertions, over what scope, and how they are verified |
| [`policy/resolution-policy.json`](policy/resolution-policy.json) | Versioned rules for resolving conflicting claims, so any resolution can be reproduced and audited |
| [`ROADMAP.md`](ROADMAP.md) | What this project commits to supporting, and in what order |
| [`GOVERNANCE.md`](GOVERNANCE.md) | How decisions are made, and what happens if maintainers become unreachable |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | What may and may not be contributed, and why |

The conformance corpus comes before the schema on purpose. Its cases are the specification,
and deriving the schema from them is cheaper than discovering them afterwards.

That derivation is checked rather than claimed. CI fails if a capability the corpus declares
has no construct in the schema, if a construct it names does not exist, or if no worked
record exercises it. A schema that accepts everything is easy to write and useless, so eight
records that must be rejected are validated alongside the six that must pass.

Everything the README describes is in the repository and passing CI. That is enforced by
[`tools/check_docs.py`](tools/check_docs.py), which fails the build if any path referenced in
any Markdown file does not exist.

## Build

Nothing is required to *consume* the published data. It is plain JSON.

To run the checks:

```bash
pip install --require-hashes -r requirements-dev.lock
python3 tools/validate_registry_files.py    # namespaces, authorities, resolution policy
python3 tools/validate_conformance.py       # corpus well formed, no identifiers
python3 tools/validate_schema.py            # schema valid, fixtures enforced, capabilities covered
python3 tools/check_docs.py                 # every documented path exists
```

## The problem

Services disagree about what an anime is.

| Service | Unit of identity | Attack on Titan |
|---|---|---|
| AniDB, MyAnimeList, AniList, Kitsu | broadcast release: a cour, an OVA, a film | 4 to 9 separate entries |
| TVDB | continuing series, seasonal and absolute numbering | 1 series, 4 seasons |
| TMDB | series plus season, or standalone for films | 1 TV entry, separate films |
| Trakt | mirrors the TMDB and TVDB shape | 1 show |
| Letterboxd | films only, television does not exist | only the compilation films |

Attack on Titan Season 3 is one TVDB season, two MyAnimeList entries, and two Netflix parts
with different numbering again. There is no 1:1 assignment that is correct. A dataset whose
schema can only express 1:1 is guaranteed wrong for a meaningful share of the catalogue, and
that share is disproportionately the long-running, high-traffic shows people actually import.

## Design commitments

**Mappings are typed, range-scoped edges, not fields on a record.**

The complete example below is mirrored in
[`examples/release.json`](examples/release.json) and validated in CI.

<!-- validated-release-example: examples/release.json -->
```json
{
  "id": "rel_01ARZ3NDEKTSV4RRFFQ69G5FAV",
  "schema_version": "1.0.0",
  "status": "active",
  "primary_title": {
    "text": "Placeholder Release, Second Part",
    "language": "ja-Latn"
  },
  "type": "TV",
  "episode_count": 10,
  "mappings": [
    {
      "assertion_id": "asr_01ARZ3NDEKTSV4RRFFQ69G5FB0",
      "ns": "example-series-db",
      "id": "100000",
      "entity": "series",
      "relation": "subset_of",
      "coverage": [
        {
          "mode": "season",
          "season": 3,
          "source_start": 1,
          "source_end": 10,
          "offset": 12
        }
      ],
      "evidence_class": "verified",
      "evidence": [
        {
          "method": "human_verified",
          "observed_source": "example-series-db series 100000, season listing",
          "reviewer": "gh:example",
          "at": "2026-07-26"
        }
      ],
      "id_source": "example-crossref:mappings"
    }
  ],
  "updated": "2026-07-26"
}
```

Episodes 1 to 10 of this release are target season 3 episodes 13 to 22.
`source_start` and `source_end` are 1-based inclusive **source** episode numbers; the target
is `source + offset`. A consumer fetches exactly the right ten episode records. A boolean
saying "this might be wrong" cannot answer that question, which is why this project exists.

**Identifiers are permanent.** They are never reused and never deleted. A retired identifier
becomes a tombstone carrying a redirect, so any identifier ever published resolves forever.

**Gate on irreversibility, not on confidence.** Adding a mapping is reversible, so admission
is permissive and a single source is labelled rather than rejected. Merging two releases is
not reversible in practice, because consumers have already cached the surviving identifier.
Corroboration guards merges, not admission. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

**Provenance is recorded per assertion.** Every mapping carries how it was established and by
what route the identifier arrived. Corroboration is computed over provably disjoint sources,
not asserted, because several projects in this ecosystem derive from one another and counting
two of them as agreement is counting one source twice.

**CC0 at the root, not just on the output.** Sources whose terms are incompatible with a
public-domain dedication are excluded at acquisition rather than laundered through a
derivative. [`schema/namespaces.json`](schema/namespaces.json) records the posture for every
namespace.

**Rightsholders have somewhere to speak, with bounded scope.** A studio, production
committee, publisher or licensor holds catalogue facts nobody can derive from the outside:
which works are one production, what a release was called on delivery, which cuts exist.
Today those reach the ecosystem by being scraped off marketing pages, if at all.
[`schema/authorities.json`](schema/authorities.json) gives them a place to be stated
directly, and bounds the claim so that stating them does not become a way to overwrite
everything else. An organisation is authoritative over its own catalogue. It is not
authoritative about how a third party catalogued its work, because that is a claim about
somebody else's database. An organisation absent from that registry carries no precedence
whatever it claims about itself.

## Licence

[CC0-1.0](LICENSE). Public domain dedication. No attribution required, no share-alike.

Share-alike would make the dataset unusable for the platforms and providers this is meant to
serve, and that is the whole point. This project is based in Ireland, where the sui generis
database right applies, and CC0 waives it explicitly.

Contributions are CC0. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
