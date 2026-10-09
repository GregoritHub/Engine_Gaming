# EG01 accepted source intake

Objective: preserve source and identify compatible mechanisms before game implementation.

Input: Socionics_Engine ab674a36e9234dcbf46634367bfc2b42b8b3cd18, tree 294edf4170efa127814b99a999ecd52702b9a563. Fresh public clone; every inherited tracked file remains unchanged. Destination import is a pinned submodule at vendor/socionics. Remote import commit f75d24b88428e5625fe571de3efe71a59e7c232b and gaming lease checkpoint 6d566fbc6ed7f421a2c9b9f67ac4a6b6c565ce17 are confirmed. A clone must use --recurse-submodules. Full research history stays accessible in the submodule; it was not flattened into the destination's commit graph.

Contracts: contracts/EG01_Protocol_v1.json and EG_Contract_Manifest.json. Mechanism inventory and dependency boundaries: docs/EG_Source_Inventory.md. The complete extracted reference is retained in project_sources. The original DOCX remains the user-supplied attachment; automatic approval review rejected its upload because of embedded assets. It was not uploaded or converted to bypass that rejection. No ambiguity required those assets for this build. No inherited engine, baseline, source meanings, evidence or research status was changed.

Environment: Python 3.12.14, Linux, standard library. Tested executable identity is the exact source commit above (already frozen); source manifests and a clean tracked-tree check confirm unchanged bytes.

Commands and outcomes:
- python vendor/socionics/docs/examples/first_run.py --output evidence/EG01/first_run: exit 0, automatic native choice, downstream consumer, exact restore, generated approval prevention/correction and ordinary-audited bypass refusal. Checkpoint JSON is losslessly gzipped; uncompressed SHA256.json remains authoritative.
- python vendor/socionics/tools/test_c6.py ../../evidence/EG01/baseline_tests tests_u2 tests_u3 tests_workflow_selection: exit 0, 83 methods, zero errors/failures, source unchanged. Output path was corrected during the run; original open log remains complete in evidence/EG01/baseline_tests, final summary was copied from the command's resolved output directory. No executed file changed.
- PYTHONPATH=vendor/socionics/baseline/HLE_Rebuild_R21B python -m unittest discover -s vendor/socionics/baseline/HLE_Rebuild_R21B/tests -t vendor/socionics/baseline/HLE_Rebuild_R21B -p test_socion.py -v: exit 0, 32 tests.
- Exhaustive geometry loop: 16 × 16 × 8 = 2048 checks of element equality across directional landing; all passed, raw rows retained.

Preserved setup failures: direct destination push could not obtain an HTTPS username; connector empty-repository ref creation returned 409; cross-repository tree/blob reuse returned 422, leading to the explicit pinned-submodule import decision. First social invocation omitted unittest's package root and failed import before any test; the corrected command above passed. These are not relabelled successful runs and are not inherited code repairs.

Decision: EG01 accepted on this targeted scope. No full 742-method rerun or game behavior is claimed. All external raw research archive IDs remain traceable but those archives were not rematerialized. Next eligible batch: EG02, finite FOL semantics and explicit source adapter.
