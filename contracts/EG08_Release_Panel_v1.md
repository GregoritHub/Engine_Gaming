# EG08 prospective bounded release panel

Release candidate after accepted EG07. Freeze all game source, tests, tools and contracts; keep inherited commit ab674a36e9234dcbf46634367bfc2b42b8b3cd18 clean. Run all new unit tests, original native U2/U3 acceptance/controls, selected C5 interruption/correction/forgery regressions, and the sealed 32-method socion suite. Preserve exact commands, platform, hashes, exit codes and failed attempts. The broader research release and its reported 742 methods are not a claim of a fresh full rerun.

Declare deterministic panels before implementation/evaluation:
- Two actors, stocks12/8, cap5, budget4000, quantum17, horizon600: return loop and quiescence.
- Three actors, stocks12/8/4, same cap/budget/quantum, horizon600: caps5/3/1 and consumed1/5/3.
- Four actors, stocks12/8/4/2, same cap/budget/quantum, horizon1200: full four-actor return.
- Four actors with Bryn→Cass severed, same genesis and horizon: no Alice return.
- Three actors budget80, quantum1, horizon600, no generated history: legitimate exhausted partial work, no negative wallets or credits.
- Three-actor corrected-history session, two600-turn episodes: further material use from retained generated content, followed by legitimate zero-material stop. The six-arm EG05 controls are rerun in the full suite.

No stochastic seed; types in scenario.setup fixed order. Shell admission enabled in every panel. The low-budget arm need not complete its initial opportunity read; honest incomplete work must persist. Do not bypass exhausted processing.

Measure execution wall time and per-turn p95/max latency, process peak RSS, uncompressed checkpoint size, transaction count, turns by actor, idle/exhausted/stopped work, duplicate exact outputs, dependency-edge count and longest ancestry depth from actual references. A scheduler tie or idle turn is not semantic activity. Expected full loops finish or legitimately quiesce; no unresolved funded pending job at horizon. Limits per panel: generation+simulation≤90s, native independent audit≤180s, p95 step≤1s, max step≤5s, checkpoint≤32MB, journal≤5,000 transactions, process peakRSS≤768MiB. Replayed three-actor save≤90s. These are engineering ceilings on the recorded machine, not universal benchmarks.

Malformed saves, duplicate keys/commands, forged status/credits, negative horizons, wrong types, competing actions and stale revisions must refuse without unearned effect. Native costs survive cancellation and failure. Fresh-launch demonstration and recorded scripted player choices must work. State explicitly that there was no human usability study or fun assessment. Package launch instructions, causal examples, limitations and next-work register. Finite sessions are the release scope; populations2–4 are the measured range, higher supported constructor bounds remain experimental. No replenishment or Model G change.
