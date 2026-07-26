# Security

This project publishes data, not a service. There is no server to compromise and no user
account to steal. The security surface is the integrity of what gets published and the
trustworthiness of what gets accepted.

## What counts as a vulnerability here

**Artifact integrity.** Anything that would let a published release differ from what the
repository and its history say it should contain. A build that hashes a file it did not
produce, a release whose manifest does not match its artifacts, a way to get an unintended
file into a signed release.

**Provenance bypass.** Anything that lets data enter the dataset by a route the namespace
registry forbids, or that makes an assertion appear better evidenced than it is. Forging an
official claim, defeating the corroboration check by declaring a false derivation root, or
promoting assertions without the evidence the policy requires.

**Identifier integrity.** Anything that silently repoints a published identifier at a
different work. Consumers cache these, and a wrong redirect propagates into every copy.

**Supply chain.** Anything in the build or release workflow that would execute untrusted
content with privileges, or that would let a fork of this repository produce artifacts that
verify as genuine.

Ordinary data errors are not vulnerabilities. A wrong offset is a bug, and the mapping
correction issue template is the right route for it.

## Reporting

Use GitHub's private vulnerability reporting on this repository: **Security → Report a
vulnerability**. That routes to the maintainers privately and gives us a place to coordinate
a fix and a release.

Please include what you did, what happened, and what you expected. A proof of concept helps.
If the issue involves a maintainer, say so in the report; it goes to all of them.

We will acknowledge within seven days and tell you what we intend to do. If we disagree that
something is a vulnerability we will say why rather than let the report go quiet.

## Disclosure

We would rather fix a problem before it is public, but we will not ask anyone to sit on a
finding indefinitely. If we have not shipped a fix or given you a date within 90 days,
publish.

When a published release is affected, the fix ships as a new release, the affected
assertions are withdrawn through the revocation feed, and the advisory says plainly which
releases were affected and what a consumer who already vendored one should do.

## For consumers

This data is consumed by vendoring: download an artifact, verify it against the published
hash, commit it. Two things follow.

**Verify what you vendor.** The manifest publishes a SHA-256 for every artifact. A copy you
did not verify is a copy you cannot reason about, and under a public domain dedication anyone
may lawfully republish a modified version.

**Watch the revocation feed.** Because you hold a copy rather than calling a service, a
correction cannot reach you. Known-bad assertions are withdrawn by identifier, and applying
that feed is how a vendored copy stays honest between updates.
