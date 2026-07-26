# Contributing

Corrections are the most useful thing you can send. A wrong offset that reaches a media
server is visible to every user of that server, and the person best placed to spot it is
usually the person it broke for.

## Licence of contributions

Contributions are dedicated to the public domain under **CC0-1.0**.

Sign off each commit with `git commit -s` to certify:

> I certify that I have the right to submit this contribution, and I dedicate it to the
> public domain under CC0-1.0.

This is checked in CI. It cannot be added retroactively: once contributions exist under
unclear terms, relicensing means tracking down every contributor who ever touched the file.

## What may and may not be contributed

**Yes.** Identifiers, mappings, episode ranges, offsets, relations, corrections, negative
assertions, and evidence for any of the above.

**No.**

- Anything extracted directly from **AniDB**. Their content is CC BY-NC-SA 4.0, which
  explicitly covers sui generis database rights, and the NonCommercial term is incompatible
  with a CC0 output. AniDB identifiers are acceptable only when they arrive via Wikidata
  (P5646) or via cross-references published by Kitsu or AniList. The distinction is the
  route, not the number, which is why every mapping records its `id_source`.
- Any **IMDb** descriptive field. Identifiers only. Their non-commercial dataset terms
  prohibit republishing their fields into a derived database.
- **Descriptive metadata** in general: synopses, tags, scores, artwork. This is a crosswalk.
  Providers remain the authority on their own metadata, and consumers fetch it from them.
- Scraped **Rotten Tomatoes** or **Letterboxd** data. Their identifiers are available through
  Wikidata.

An identifier observed as a fact about the world is not the same as a systematic extraction
of somebody's database. The first is what this project collects. The second is what it
refuses, and [`schema/namespaces.json`](schema/namespaces.json) records which sources fall
where.

## The two gates

Admission is permissive. Merging is not.

**Adding a mapping is reversible.** Delete the edge and it is gone. So a single source is
fine, labelled `inferred`. Absence of corroboration is never grounds for rejection, because
that is exactly how obscure, older and unlicensed works get quietly excluded from every
dataset that has tried this before.

**Merging two releases is not reversible in practice.** Consumers have already cached the
surviving identifier, and the record of which facts belonged to which side is gone. A merge
needs corroboration from provably disjoint sources, a human verification, or an assertion
from a source that is authoritative within its own namespace.

Gate on irreversibility, not on confidence.

## Evidence and evidence classes

Evidence classes are defined in [`GLOSSARY.md`](GLOSSARY.md). Two things worth stating
plainly here:

**They are unordered.** `asserted`, `verified` and `corroborated` describe different kinds of
backing, not a ranked scale. Do not treat one as strictly better than another.

**`corroborated` is computed, not claimed.** Several projects in this ecosystem derive from
one another. Two of them agreeing can be one source counted twice, so corroboration is
checked against a declared derivation graph and fails closed when a source's lineage is not
declared. If you add a new source, declare where it draws from.

Your first contribution will usually land as `inferred` or `candidate`, and that is normal.
`candidate` is never published to the accepted artifact.

## Conflicts

Conflicting claims are kept, not resolved silently. Both survive in the record, the winner
carries the policy version that decided it, and two authoritative sources disagreeing produce
a `disputed` state that publishes both and ranks neither. The rules are versioned in
[`policy/resolution-policy.json`](policy/resolution-policy.json) so that any resolution can be
reproduced and argued with.

## Opening a pull request

Discuss anything structural in an issue first. Corrections do not need that.

Every pull request is reviewed by a maintainer who did not write it. Data changes get a
second pair of eyes on the underlying source, not just the diff, because a diff that looks
right and cites the wrong page is the failure mode that matters here.

Be specific about where a number came from. "MAL says 12 episodes" is not evidence.
"myanimelist.net/anime/35760, retrieved 2026-07-26, episode count 12" is.

## Reporting a wrong mapping

Open an issue with the mapping correction template. Include the identifier of the assertion
if you have it, what you expected, what you got, and where you looked. If you are a
downstream consumer, say which release you vendored.
