# Governance

The dataset this project replaces was archived in July 2026 after years as the ecosystem's
primary cross-reference dump. It was a personal repository, on free-tier hosting, with no
documented plan for what happened if its maintainer stopped. Everything downstream now reads
a frozen file.

It did not fail for technical reasons. Every decision below exists because of that.

## Principles

**The project outlives any individual maintaining it.** No knowledge, credential, or process
required to continue is held privately by one person.

**Forkable without permission.** A successor needs nothing from the current maintainers.
Identifiers can be minted by anyone with no coordination, there is no private registry to
inherit, and every release is verifiable from its published hashes alone.

**Organisation namespace, never personal.** The repository lives under an organisation, and
ownership is held by more than one person.

**CC0 from the first commit.** Retro-licensing after contributions arrive is not practical.

## Roles

**Maintainers** hold write access, review pull requests, and cut releases. Every change is
reviewed by a maintainer other than its author, including changes authored by maintainers.
Current maintainers are listed in [`.github/CODEOWNERS`](.github/CODEOWNERS).

**Contributors** open issues and pull requests. No prior involvement is required. Sustained,
accurate contribution is how people become maintainers, and the bar is judgement about
sources rather than volume of commits.

## Decisions

Routine changes are decided in review by any maintainer other than the author.

Changes to the schema, the licence posture of a source, the resolution policy, or this
document are decided by maintainer agreement in a public issue, with at least seven days for
comment. Disagreement is resolved by discussion. If it cannot be, the change does not happen,
because the status quo is the safer default for a dataset other projects vendor.

Anything affecting published identifiers is one-way. Identifiers are never reused and never
deleted, so those changes get the longest review and the most scepticism.

## Releases

Releases are tagged, immutable, and signed. Every release publishes a manifest carrying a
SHA-256 for each artifact, the schema version, the input snapshot identifiers, and the
previous release for comparison.

Signing uses keyless OIDC, so there is no signing key to lose, rotate, or hand to a
successor, and the identity binding is the repository rather than a person.

Archival copies are deposited outside GitHub, so that the loss of this repository or this
organisation does not lose the data.

## If maintainers become unreachable

A maintainer is considered unreachable after 90 days with no commit, issue response, or
release.

1. At day 90 an automated workflow opens a public issue titled `SUCCESSION: maintainer
   unreachable`, and a notice goes to the project's external contact address and to the
   archival deposit record. The notice does not depend on this repository or this
   organisation remaining reachable, because a dead-man's switch wired to the same power
   supply as the patient is not a switch.
2. If no maintainer responds by day 120, anyone may fork and continue.
3. The fork announces itself in that issue. The last release remains valid and verifiable
   from its published manifest.

No permission is required at step 3. That is deliberate.

## What a successor needs, and where it is

Nothing in this table is held privately.

| Requirement | Location |
|---|---|
| Full history | this repository |
| Vocabulary | [`GLOSSARY.md`](GLOSSARY.md) |
| Schema and namespace registry | [`schema/`](schema/) |
| Conflict resolution rules, versioned | [`policy/resolution-policy.json`](policy/resolution-policy.json) |
| Direction and commitments | [`ROADMAP.md`](ROADMAP.md) |
| Published artifacts and their hashes | GitHub Releases, and the archival deposit |
| Release signing | keyless OIDC, bound to the repository. Nothing to transfer |

## Identifiers after a fork

Canonical identifiers are ULIDs: 48 bits of timestamp, 80 bits of randomness. A fork can mint
new identifiers immediately, with no coordination and no realistic collision risk.

This is why the identifier scheme is not a governance dependency. There is no registry to
inherit and no authority to transfer. Where two forks continue in parallel, their identifiers
remain distinguishable, and reconciliation later is a matter of publishing redirects between
them rather than negotiating a merge.

## Conflicts of interest

Maintainers who also maintain a downstream or competing project disclose it in
[`.github/CODEOWNERS`](.github/CODEOWNERS) and recuse themselves from decisions that would
advantage it. Disclosure converts a criticism into a matter of record, which is the cheaper
outcome for everyone.

## Reporting a governance problem

Open a public issue. If it involves a maintainer and cannot be raised publicly, use the
contact route in [`SECURITY.md`](SECURITY.md).
