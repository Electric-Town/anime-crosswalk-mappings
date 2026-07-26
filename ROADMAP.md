# Roadmap

What this project commits to supporting, and roughly in what order. Dates are deliberately
absent. Order is not.

## Now

**The conformance corpus.** Published in [`conformance/`](conformance/README.md): 18 cases
any correct implementation has to handle, and the 13 capabilities they require. Written
before the schema, because these cases are the specification and discovering them later
would invalidate everything built on top.

It holds no identifiers. Every case describes a shape, which keeps it free of any provenance
question and means it tests whether a format can *express* a relationship rather than whether
a particular row is right. Other projects can run their own data against it and find out
which capabilities their format actually has.

**The schema, derived from those cases.** Range-scoped edges with explicit cardinality, so a
one-to-many episode relationship is representable rather than approximated. Numbering spaces.
Negative assertions. Per-assertion identifiers and provenance.

**A route for rightsholders.** [`schema/authorities.json`](schema/authorities.json) registers
which organisations can make authoritative assertions, over what scope, and how they are
verified. The registry is empty, which is honest: nobody has registered yet. The structure
exists so that the first studio or licensor who wants to correct their own catalogue has
somewhere to put it that is neither a scraped marketing page nor an unbounded override.

**The invariant suite.** Structural rules the build enforces, so that dirty data is hard to
commit rather than merely discouraged. Transitive closure that respects negative assertions.
Corroboration computed over provably disjoint sources, failing closed on unknown lineage.
Coverage arithmetic with no gaps and no double-booked targets. Tombstone integrity. A
provenance gate that rejects any identifier whose route violates the declared licence posture.

## Next

**The first published dataset.** Small, hand-verified, and honest about its size. Every
artifact declares which evidence classes it contains and carries nothing else.

**Offset derivation from air dates.** Air dates are facts, available from several
public-domain and permissively-licensed sources, which makes them a route to episode offsets
that carries no licence encumbrance. Published together with its measured precision against a
stratified reference set, and with the cases where it declines to guess. A derivation that
cannot report its own failure is not usable.

**The consumer contract.** A verification script, a worked lookup example tested in CI, and a
documented overlay format so a consumer can correct a mapping locally without invalidating
the hash they verified or forking the dataset.

**Release plumbing.** Signed, immutable, hash-addressed releases with a manifest that names
the previous release and lists what changed. Revocations by assertion identifier, so a
known-bad claim can be withdrawn from copies already vendored.

## Later

**Compatibility output for existing tooling.** Emitting formats that established consumers
already read, so adoption is a change of URL rather than a rewrite. Whether every such format
can be produced without loss is an open question the conformance corpus will answer, and this
project will state plainly where a legacy format cannot express what the graph holds rather
than emitting something lossy and calling it compatible.

**Broader coverage.** More namespaces, more releases, and a published measurement of what
coverage is lost by excluding sources whose terms are incompatible with a public-domain
dedication. That gap is a real cost of the licence position and it will be measured and
published rather than glossed.

**An industry-standard identifier namespace.** Anime is badly under-registered in the
identifier systems the wider distribution supply chain already uses. Carrying that namespace
costs nothing while it is empty and is the hook that makes later adoption possible.

## What this project will not do

- **Ship descriptive metadata.** No synopses, tags, scores, or artwork. This is a crosswalk.
  Providers remain the authority on their own metadata.
- **Model streaming availability.** It is regional, it changes weekly, and it is not a
  property of the work. Baking it into the graph would guarantee the data is wrong the day it
  ships. Platform catalogue identifiers are identity and belong here; whether something is
  streamable in a territory today is an observation and does not.
- **Run an API.** The data is vendored. There is no service to depend on, rate-limit, or lose.
- **Adopt a share-alike licence.** It would make the dataset unusable for exactly the
  consumers it exists to serve.
- **Model manga.** The mapping problems are different enough to double the schema surface for
  a fraction of the demand.
- **Silently resolve a conflict.** Conflicting claims are published, attributed, and versioned
  against the policy that decided them.

## Open questions

Held in the open because pretending they are settled would be worse.

- Where a legacy compatibility format cannot express a range-scoped edge, is a lossy emission
  better than none? The current answer is no, and it is not yet tested against what consumers
  actually need.
- How much catalogue coverage is lost by excluding sources with incompatible terms, and does
  the permissive-route alternative reach far enough to matter for older and unlicensed works?
- Where should the boundary sit between a canonical identifier for a work and a stable
  identifier for a claim about a work? The second is clearly useful. The first is only useful
  if others adopt it.
