# Engineering decisions

## EG-D01 Pinned source import
The direct authenticated Git transport is unavailable. The supported connector creates a pinned git submodule at vendor/socionics, commit ab674a36e9234dcbf46634367bfc2b42b8b3cd18. This preserves the complete research tree and history through its source repository, with source-relative paths unchanged inside the submodule. A fresh checkout must use --recurse-submodules. The upstream repository stays unmodified. Reversal cost: a future flattening import would require a full path and evidence review. No flattened-copy or remote-history-copy claim is made.

## EG-D02 Isolated game extension
New runtime contracts and code go in engine_gaming, outside the pinned source. Maintenance scenario rules remain in explicit adapters. Research audits and test fixtures are reproduction tools, not the ordinary gameplay runtime.
