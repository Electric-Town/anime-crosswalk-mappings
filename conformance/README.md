# Conformance corpus

A set of cases that any correct anime crosswalk has to handle, with the capability each one
requires. It is written before the schema, because these cases are the specification and
deriving the schema from them is cheaper than discovering them afterwards.

It is also usable by projects that are not this one. The corpus asserts **structure**, not
identifiers, so you can run your own dataset against it and find out which capabilities your
format actually has.

## Why it holds no identifiers

Every case describes a shape: one upstream release covering part of a target season, two
source episodes forming one target episode, two distinct works sharing a title. None of them
names a MyAnimeList number or a TVDB number.

That is deliberate twice over. It keeps the corpus free of any provenance question, so it can
be shared and reused without inheriting anyone's licence terms. And it keeps the corpus
testing what it claims to test: whether a format can *express* a relationship, which is
independent of whether a particular row is correct.

Real identifiers belong in the dataset, where they carry evidence. They do not belong in a
specification.

## Capabilities

Each case declares the capabilities it needs. A format either has one or it does not, and
where it does not, the case says exactly what information is lost.

| Capability | Meaning |
|---|---|
| `range_scoped_coverage` | An edge applies to a stated span of episodes, not the whole release |
| `non_zero_offset` | Source episode *n* maps to target episode *n + k* |
| `dual_numbering` | Season and absolute numbering are both recorded where a target exposes both and they diverge |
| `cross_boundary_span` | One release spans more than one target season |
| `discontinuous_coverage` | One release maps to several non-adjacent target ranges |
| `cardinality_expand` | One source episode covers several target episodes |
| `cardinality_merge` | Several source episodes form one target episode |
| `numbering_space` | Specials, trailers, credits and parodies occupy their own sequences |
| `negative_assertion` | A recorded statement that two things are not the same, with reasoning |
| `alternate_cut` | Sibling releases that are the same work in a different edit |
| `multi_series_membership` | One release belongs to more than one series |
| `known_absent` | A recorded statement that no counterpart exists, with the reason |
| `ordering_variance` | Broadcast order differs from chronological or intended order |

## Case format

```json
{
  "id": "kebab-case-identifier",
  "title": "One line naming the shape",
  "breaks": "What a naive 1:1 mapper does with this, concretely",
  "capabilities": ["range_scoped_coverage", "non_zero_offset"],
  "shape": { "source": "...", "target": "...", "relationship": "..." },
  "loss_if_unsupported": "What information disappears when the format cannot express it",
  "observed_in": ["a real family of works, named without identifiers"]
}
```

`breaks` and `loss_if_unsupported` are the two fields that matter. A case that cannot say
what goes wrong is not a case, it is a preference.

## Using it

```bash
python3 tools/validate_conformance.py
```

Checks the corpus is well formed: unique ids, known capabilities, every required field
present and non-trivial, and every declared capability exercised by at least one case.

The corpus does not yet execute against a dataset, because there is no dataset. When the
schema lands, each case gains a fixture and an assertion, and the same ids carry through.

## For other projects

If you maintain a mapping dataset, the useful question is not whether you agree with this
project. It is which of the thirteen capabilities your format can express. Several
established formats handle ranges and offsets well and cannot express cardinality at all,
which means double-length episodes are silently approximated rather than represented.

Cases and capabilities can be proposed through the schema issue template. A case is accepted
when it names a real family of works and states what breaks.
