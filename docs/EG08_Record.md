# EG08 accepted release 0.1

Input EG07: 9b4449d3afb6cb006c568904c14583c1bb86a646; source unchanged at ab674a36e9234dcbf46634367bfc2b42b8b3cd18. The prospective release panel was saved before implementation. Final local candidate: aac4e71092f488622eb83a28686425dc6068e751. Every tested runtime, test and contract byte is pinned by the recorded SHA256 manifests.

Candidate1: all43 game methods and all32 sealed social methods passed; its67-method inherited selection had two import errors caused by package shadowing. Its population panels and clean-checkout demo passed. Candidate2 changed only the release launcher and lineage-measurement tools. All67 inherited methods then passed. The game/test/contract hashes are identical, so the43+32 passing methods are carried with an explicit identity proof in attempt2/reused_checks.json. This is142 distinct passing test methods plus the declared scenario panels. Neither the source742-method research total nor its complete release pipeline is claimed as rerun.

Commands: python tools/release_verify.py attempt1; python tools/release_verify.py attempt2 --tooling-recheck. The second run froze all current files, passed every corrected command, and confirmed unchanged source. The first held candidate and all outputs remain. Details: docs/EG08_Attempt1_Findings.md.

## Measured panel

| Scenario | Turns | Simulation seconds | p95 step ms | Save MB | Lineage depth | Full return |
|---|---:|---:|---:|---:|---:|---|
| two | 600 | 12.37 | 28.73 | 2.03 | 50 | yes |
| three | 600 | 16.16 | 40.19 | 2.85 | 77 | yes |
| four | 1200 | 38.33 | 44.65 | 3.75 | 102 | yes |
| four_severed | 1200 | 26.06 | 28.07 | 2.36 | 41 | no |
| exhausted | 600 | 15.42 | 34.34 | 2.44 | 127 | no |

Five field panels met all declared ceilings. Peak RSS reported for those panels was 49.0 MiB; maximum measured step was 81.3 ms. Lineage depth uses only committed inputs/evidence between atomic transactions; it is not a count of semantic innovations. Generated-intention counts are recorded separately. All exact deliveries were unique; scheduling counts differed by at most one; no negative balances, invisible credits or unexpected refusals occurred.

The two-episode retained-history session restored exactly in 42.61 seconds from 6.75 MB, below its90-second/32-MB ceilings. No separate peak-memory measurement is claimed for that restore. Paid cancellation, exhausted partial work, wrong types, forged budgets/statuses, duplicate commands, competing actions and stale native revisions remain covered by the full game/native tests.

The four-actor connected run returned a generated result to Alice; cutting Bryn→Cass removed Alice’s consumption. The exhausted arm retained75 exhausted turns and a zero budget with no refund. Normal sessions legitimately quiesce after the allocation; large idle counts are reported and not presented as sustained semantic activity. Further useful activity in the renewed episode is tied to retained generated experience.

Fresh checkout: tools/fresh_checkout.py cloned the candidate into a new directory, populated the exact pinned submodule through local Git objects, and successfully ran python -m engine_gaming --demo. It checked the returned limit and further player consumption. Source history/archives remain intact; the ordinary runtime imports no research test fixtures.

## Decision

Accepted as Engine Gaming0.1, a finite text/board workshop vertical slice. EG01–EG08 are complete at the verified-code level; remote delivery is recorded separately. FOL, causal feedback, paid cognition, mature Shell integrity, acquired-capacity evidence, preserved history and inspectable play all have executable evidence. Human enjoyment, broad institutions, graphical polish, populations above four, and indefinitely sustained play are not established. See EG_Limitations.md, Play_Notes.md and EG_Next_Work.md.
