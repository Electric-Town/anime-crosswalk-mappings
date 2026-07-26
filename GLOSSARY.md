# Glossary

The vocabulary of this project. Every term here appears as a schema field name, a module
name, or both. Defined once, used everywhere, and changed only through a schema version bump.

## Entities

**Series**
: A continuing programme, at the grain TVDB and media servers use. A grouping, not a parent
  of truth. A Release may belong to zero or many Series, and recap films commonly belong to
  two.

**Release**
: The primary entity. A broadcast unit, at the grain AniDB and MyAnimeList use: a television
  cour, an OVA, an ONA, a film, a special. A film is a Release with one episode. Everything
  is a Release.

**Episode**
: A single episode within a Release. Materialised only where the mapping cannot be described
  by a constant offset. Most Releases have no Episode records and do not need any.

**Franchise**
: A loose grouping such as Monogatari or Gundam. Useful for presentation, useless for
  mapping. Deliberately kept separate so nothing is tempted to map against it.

## Mapping

**Mapping**
: A typed, directional, range-scoped edge from a Release to an identifier in an external
  namespace. Not a field on a record. This distinction is the reason the project exists.

**Assertion**
: A single mapping claim together with its evidence and its identifier. Assertions carry
  their own stable identifier so that one claim can be corrected or withdrawn without
  affecting the rest of the Release.

**Namespace** (`ns`)
: A provider identifier space: `mal`, `anilist`, `tvdb`, `tmdb`, `imdb`, `anidb`, `kitsu`,
  `trakt`, and others. Registered in [`schema/namespaces.json`](schema/namespaces.json) with
  its identifier format, deep-link template, and licence posture.

**Relation**
: What the edge asserts.

  | Value | Meaning |
  |---|---|
  | `exact` | The two records describe the same unit with the same boundaries |
  | `subset_of` | This Release is part of the target, such as one cour of a TVDB season |
  | `superset_of` | This Release contains several target records |
  | `overlaps` | Partial, non-nesting overlap. Requires explicit ranges |
  | `alternate_cut_of` | Same content, different edit |
  | `related` | Explicitly not a mapping. A sequel, spin-off or adaptation. Never merge on this |
  | `not_same_as` | A negative assertion. See below |

**Coverage**
: Which episodes of this Release the edge applies to, and how they map to the target.
  `start` and `end` are 1-based inclusive **source** episode numbers. The target episode is
  `source + offset`. `mode` selects the target's numbering scheme:

  | Mode | Meaning |
  |---|---|
  | `single` | A film or OVA. No episode arithmetic |
  | `flat` | The target has no seasons |
  | `season` | The target is season-numbered |
  | `absolute` | The target uses absolute ordering across the whole series |

  Where a target exposes both season and absolute numbering, both are recorded, because that
  is the difference between working and not working for media server agents.

**Numbering space**
: Which sequence an episode number belongs to: `regular`, `special`, `trailer`, `credit`,
  `parody`, or `other`. A trailer numbered 1 and an episode numbered 1 are different things,
  and conflating them silently corrupts every downstream fetch.

**Negative assertion**
: A recorded statement that two things are *not* the same, with its reasoning. Hunter x
  Hunter 1999 is not Hunter x Hunter 2011. One Piece the live-action series is not One Piece
  the anime. No existing dataset stores these, which is why the same bad merges keep being
  re-derived. Storing the refutation means an automated pass can never repeat the error.

## Provenance

**Evidence**
: How an assertion was established. Records the method, the observed source, the retrieval
  date, and the reviewer. A person's name identifies a curator, not a fact, so the observed
  source is recorded separately from whoever checked it.

**Evidence class**
: What kind of evidence backs an assertion. **Unordered.** These are categories, not a
  ranked scale, and consumers should not treat them as one.

  | Class | Meaning |
  |---|---|
  | `asserted` | The rightsholder or platform declared it, within its own namespace |
  | `verified` | A person opened both sources and checked |
  | `corroborated` | Two sources with provably disjoint derivation roots agree |
  | `inferred` | One source, or derived transitively |
  | `candidate` | Heuristic only. Never published to the accepted artifact |
  | `disputed` | Conflicting assertions exist. Published unranked, never silently resolved |

**Derivation root**
: The upstream a source ultimately draws from. Several projects in this ecosystem derive
  from one another, so agreement between two of them can be one source counted twice.
  Corroboration is computed over provably disjoint roots and fails closed when a source's
  lineage is unknown.

**Identifier source** (`id_source`)
: The route by which an identifier arrived, which is distinct from the namespace it names.
  An AniDB identifier read from Wikidata and the same identifier extracted from AniDB
  directly share a namespace and have different provenance. Licence posture attaches to the
  route, not to the namespace.

**Authority**
: An organisation that can make assertions carrying precedence within a declared scope: a
  studio, production committee, publisher, licensor, distributor, or platform. Registered in
  [`schema/authorities.json`](schema/authorities.json) with its role, its scope, and how it
  is verified. An organisation absent from that registry carries no precedence whatever it
  claims about itself, because otherwise asserting authority would be the cheapest way to
  poison the graph.

**Scope**
: What an Authority is authoritative *about*. Bounded deliberately. An organisation is
  authoritative over its own catalogue identifiers and its own delivered structure. It is
  not authoritative about how a third party catalogued its work, because that is a claim
  about somebody else's database. Outside its scope an authority's assertion is ordinary
  evidence, weighed on the same terms as anything else.

## Lifecycle

**Tombstone**
: A retired identifier. Never deleted, never reused. Carries a redirect so that any
  identifier ever published continues to resolve.

**Redirect**
: The forwarding pointer on a tombstone. Chains must terminate and must not cycle.

**Revocation**
: A published statement that a specific assertion is known to be wrong. Because consumers
  vendor a copy of the data rather than calling an API, corrections cannot be pushed, and
  revocation by assertion identifier is how a known-bad claim is withdrawn.

**Known absent**
: A recorded statement that no mapping exists in a given namespace, with the reason. A film
  has no Letterboxd equivalent problem; a television release does, because Letterboxd holds
  films only. Recording absence stops the same fruitless lookup being retried forever.

## Publication

**Artifact**
: A published file. Each artifact declares which evidence classes it contains, and carries
  nothing outside that declaration.

**Manifest**
: The signed index of a release: a SHA-256 for every artifact, the schema version, the input
  snapshot identifiers, and the previous release for comparison.

**Vendoring**
: The intended way to consume this data. A consumer downloads an artifact, verifies it
  against the published hash, and commits it into their own repository. There is no API to
  depend on and nothing to rate-limit. The trade-off is that corrections cannot be pushed,
  which is why revocations exist and why precision at publication time matters more than it
  would for a hosted service.

**Overlay**
: A consumer-owned file of local corrections, applied on top of a vendored artifact. The
  upstream bytes stay untouched so their published hash remains valid.
