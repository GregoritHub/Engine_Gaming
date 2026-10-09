# Engine Gaming — Workshop

A finite, playable agent workshop built on the pinned Socionics Engine. Agents pay to read, interpret and act. Generated proposals circulate through distinct types; retained Shell patterns can prevent work, interrupt it, or change under supported correction. The world also exposes a presentation-independent finite first-order interpretation.

**Release 0.1 accepted: EG01–EG08 complete.** The verified scope is a finite workshop with measured two-, three-, and four-agent sessions. See `docs/EG08_Record.md` for the142-method acceptance evidence and performance results.

## Start

Python **3.12**, standard library only:

```sh
git clone --recurse-submodules https://github.com/GregoritHub/Engine_Gaming.git
cd Engine_Gaming
git submodule update --init --recursive
python -m engine_gaming
```

For a short demonstration:

```sh
python -m engine_gaming --demo
```

You play Alice. Try `propose 5`, `reflect`, `wait 600`, `board`, `inspect`, `wait 12`, then `consume 1`. A different initial limit changes the generated reply. `help` lists all commands. Work and supplies are finite; `cancel` never refunds spent work. `renew` begins a further allocation from observed experience when the first has completed. Some continuations legitimately stop when no useful supplies remain.

`save saves/workshop.json` creates a new save; `load saves/workshop.json` verifies it by replaying its complete command history. Save to a new filename each time. Saves are local and contain the full simulated world; do not treat them as multiplayer secrecy boundaries.

Text and `board` show the same received information. Other inventories remain unknown. Explicit diagnostics are separate:

```sh
python -m engine_gaming --inspect-truth saves/workshop.json
```

## Evidence and source

The eight-batch reference is `project_sources/Engine_Gaming_Build_Reference_v1_0.txt`; contracts, batch decisions and frozen tests are under `contracts`, `docs`, and `evidence`. The native source and its history, licenses, sealed baselines and research evidence are preserved as the submodule `vendor/socionics` at `ab674a36e9234dcbf46634367bfc2b42b8b3cd18`.

```sh
python -m unittest discover -s tests -v
```

The research build is complete and separate. This game does not resume its automation, enable Phase 7 pricing, replenish resources invisibly, or establish claims about human psychology. The slice uses authored goals and a finite explicit policy; it is not a claim of unrestricted or indefinitely sustained generativity. No human playtest has yet been claimed.

Release verification: `python tools/release_verify.py YOUR_NEW_ATTEMPT_NAME` freezes and runs the complete relevant suite and declared panels. Use a new name so earlier evidence is preserved.
