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
| [`GLOSSARY.md`](GLOSSARY.md) | The vocabulary. Every term used in the schema and the code is defined here once |
| [`schema/namespaces.json`](schema/namespaces.json) | Every provider namespace, its identifier format, its deep-link template, and its licence posture |
| [`policy/resolution-policy.json`](policy/resolution-policy.json) | Versioned rules for resolving conflicting claims, so any resolution can be reproduced and audited |
| [`ROADMAP.md`](ROADMAP.md) | What this project commits to supporting, and in what order |
| [`GOVERNANCE.md`](GOVERNANCE.md) | How decisions are made, and what happens if maintainers become unreachable |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | What may and may not be contributed, and why |

Everything the README describes is in the repository and passing CI. That is enforced by
[`tools/check_docs.py`](tools/check_docs.py), which fails the build if any path referenced in
any Markdown file does not exist.

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

```json
{
  "ns": "tvdb",
  "id": "267440",
  "relation": "subset_of",
  "coverage": { "mode": "season", "season": 3, "start": 1, "end": 10, "offset": 12 }
}
```

Episodes 1 to 10 of this release are TVDB season 3 episodes 13 to 22. `start` and `end` are
1-based inclusive **source** episode numbers; the target is `source + offset`. A consumer
fetches exactly the right ten episode records. A boolean saying "this might be wrong" cannot
answer that question, which is why this project exists.

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
derivative. `schema/namespaces.json` records the posture for every namespace.

## Licence

[CC0-1.0](LICENSE). Public domain dedication. No attribution required, no share-alike.

Share-alike would make the dataset unusable for the platforms and providers this is meant to
serve, and that is the whole point. This project is based in Ireland, where the sui generis
database right applies, and CC0 waives it explicitly.

Contributions are CC0. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
