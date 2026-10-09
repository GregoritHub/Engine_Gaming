# Finite world semantics version 1

Prospective contract. Inputs are the exact EG01 research source plus game adapters; no inherited files change.

## Interpretation

An authoritative snapshot is a finite, nonempty relational, function-free first-order structure with equality. Its domain consists of JSON-encoded namespace/key entity IDs of all active heads at an explicit journal prefix. Revisions and journal offsets are metadata, not replacement identities. Retired entities leave later domains; old snapshots keep their domains. Constants are explicit aliases denoting domain members; labels and screen positions have no truth-bearing role. There are no numeric or Boolean literals in formulas: entities are exact strings, and True cannot equal 1 by coercion. Unary predicates implement sorts in ordinary one-sorted FOL.

The fixed initial signature is Person/1, Item/1, Context/1, Claim/1, Interpretation/1, Event/1, Owns/2, Holds/2, Serviceable/1, Damaged/1, Inside/2. Owns and Holds are distinct. Inside is empty for this workshop adapter, which implements no containment dynamics; it is not inferred from custody. All extensions are complete for the declared snapshot. Claim and Interpretation classify records; their contents never populate authoritative material predicates. The adapter reports all unmapped facets/roles. It maps only active Person/Context roles, material facets and record occurrence/categories; foreign schemas reject.

Invariants: Item and Person are disjoint; each Item has exactly one Person owner and one Person custodian; Owns/Holds have Person×Item arguments; Serviceable/Damaged have Item arguments and are disjoint; Inside has Item×Item arguments, no self-containment or cycles. These are game axioms, not consequences of FOL. Each constant denotes a member; predicate extension arity and domain membership are checked, with unknown symbols rejected.

## Formulas and evaluation

AST terms: ["var", name], ["const", alias]. Formulas: ["atom", predicate, term...], ["eq", term, term], ["not", formula], ["and", formula, formula], ["or", formula, formula], ["implies", formula, formula], ["forall", variable, formula], ["exists", variable, formula]. Names are nonempty strings. Exact node length, symbol and term validation occurs over the whole AST before evaluation, including short-circuited branches. Lexical quantifier binding supports shadowing. Open formulas require an assignment for exactly all free variables, with domain-member values. Sentences take an empty assignment. A node/work budget raises EvaluationIncomplete, never False. Depth and node limits reject oversized syntax before recursion overflow.

The primary evaluator uses recursive interpretation. The independent reference evaluator compiles satisfying assignment sets over the finite domain with relational complement, intersection, union and quantifier projection/expansion. It does not call the production evaluator or validator. Its small-world scope and limits are explicit.

## Projection and access

Text and board are projections of the same snapshot. Their query API evaluates that snapshot, independent of labels/camera. A renderer can omit facts but cannot create a different authoritative interpretation. Participant views are separate partial knowledge, with known/unknown/disputed/believed statuses; they are never classical snapshots with absent facts treated as false. Policies receive only native detached participant views. Truth inspection is an explicit administrator/debug operation.

## Time, actions and persistence

The authoritative journal prefix defines time; source ObjectRef revisions are preserved in the adapter's revision map. Historical queries select a prefix, never silently resolve the current head. Actions are serialized by expected snapshot revision, and competing stale actions reject. Candidate state validation is atomic; rejected attempts retain their reason. Native material execution and its paid failures remain under native authority. Game action changes will be declared separately; this batch supplies a generic validated atomic snapshot boundary and does not grant a player a truth-editing command. Snapshot save/restore is versioned, checksum-verified and fully revalidated.

## Acceptance panel

Compare both evaluators on nested scope, shadowing, equality, implication, conjunction, disjunction and negation, including all interpretations of a tiny unary signature embedded in valid small workshop snapshots. Exercise unknown symbols, malformed hidden branches, free variables, assignments, non-domain aliases, bool/int confusion, empty domains, budget exhaustion, invalid custody/containment, atomically rejected transitions, stale competing updates, history, restore, adapter identity, unmapped records, hidden participant facts, and projection/label/camera invariance. All declared cases must pass on a recorded unchanged source freeze. No general theorem prover, arbitrary human semantics, 3D renderer fidelity or Tarski's World certification is claimed.
