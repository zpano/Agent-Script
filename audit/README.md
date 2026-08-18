# DSH static audit runner

This temporary branch audits the immutable first 2,000 rows of the CSV snapshot
whose SHA-256 is `5852f4f8aa21582096b445f969609cb68b83fbb8e009c7dab3dfd89266afd5b7`.

The workflow never installs, builds, imports or executes repository content. It
uses shallow partial Git clones with no checkout, no hooks, no LFS smudging and
no submodules, then reads selected source/config blobs through `git cat-file`.
Every target receives a result status; the aggregate job fails unless rows
1..2000 are all present exactly once.
