# Engineering decisions

## EG-D01 Pinned source import
The direct authenticated Git transport is unavailable. The supported connector creates a pinned git submodule at vendor/socionics, commit ab674a36e9234dcbf46634367bfc2b42b8b3cd18. This preserves the complete research tree and history through its source repository, with source-relative paths unchanged inside the submodule. A fresh checkout must use --recurse-submodules. The upstream repository stays unmodified. Reversal cost: a future flattening import would require a full path and evidence review. No flattened-copy or remote-history-copy claim is made.

## EG-D02 Isolated game extension
New runtime contracts and code go in engine_gaming, outside the pinned source. Maintenance scenario rules remain in explicit adapters. Research audits and test fixtures are reproduction tools, not the ordinary gameplay runtime.

## Workshop slice and release scope

The first playable scenario is a finite shared-allocation workshop. Players inhabit Alice with the same paid access/action boundary as an agent. Ownership and material consumption carry the immediate consequences; repairs, borrowing, broader institutions and commercial art are next-work candidates. Text is the primary interface, with a second compact board view of the same permitted information and a separate explicit truth inspector. This keeps foundational causal inspection available without giving the ordinary player hidden facts.

The field uses direct C3 movements through C5 admission, not timed maintenance workflow operations. It preserves those native schemas and their costs. No artificial old-social reception fee, universal estafette clock, replenishment or new energy law is introduced. Population experiments will be bounded finite sessions; idle turns will be measured separately from useful work. Reusable development capacity must come from native observed independent practice, never from merely labelling a correction successful.
