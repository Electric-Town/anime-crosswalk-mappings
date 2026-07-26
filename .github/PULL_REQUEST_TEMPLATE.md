<!--
Corrections do not need an issue first. Anything structural should have one.
Sign off your commits with `git commit -s`. See CONTRIBUTING.md.
-->

## What this changes

<!-- One or two sentences. What is different after this merges? -->

## Why

<!-- The problem this solves. If it fixes a wrong mapping, say what was wrong and what
     a downstream consumer would have seen. -->

## Evidence

<!-- For any change to data, this is the part that gets reviewed.

     "MAL says 12 episodes" is not evidence.
     "myanimelist.net/anime/35760, retrieved 2026-07-26, episode count 12" is.

     List every source you checked, with the date you checked it. If two sources
     disagreed, say so and say which you went with. -->

## Checklist

- [ ] Commits are signed off (`git commit -s`)
- [ ] I have the right to contribute this, and I dedicate it to the public domain under CC0-1.0
- [ ] No content extracted directly from a source the namespace registry marks `indirect_only` or `excluded`
- [ ] No descriptive metadata (synopses, tags, scores, artwork)
- [ ] Documentation matches what is actually in the repository
- [ ] `python3 tools/check_docs.py` and `python3 tools/validate_registry_files.py` pass locally

## Anything you are unsure about

<!-- Genuinely useful. Say where you had to guess, or where a source was ambiguous.
     Flagging it is faster for everyone than a reviewer finding it. -->
