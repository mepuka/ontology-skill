# Ontology Skills Improvement — Research Output

## Part I — Critique

### Skill-authoring quality

The current suite is directionally right for an agent-harness repository. Its basic shape matches what entity["company","Anthropic","ai company"] recommends for Claude Code skills: a short `SKILL.md` that is loaded only when relevant, a `description` that helps routing, and deeper supporting material that can be referenced when needed. Anthropic’s own guidance is explicit on all three points: the `description` is what helps the model decide when to load a skill; longer reference material belongs outside the main skill body; and descriptions need the keywords users “would naturally say,” with the most important match language front-loaded because descriptions are budget-constrained and can be truncated. citeturn9view0turn8search2

The suite’s strongest authoring choice is that it already treats skills as process entrypoints rather than encyclopedic documents. The suite’s weakest authoring choice is that several `SKILL.md` files still try to be miniature methodology chapters instead of compact operational prompts. In practice, that means the first routing decision is often harder than it should be, because multiple skills read like “general ontology engineering help,” and the downstream execution decision is less deterministic than it should be, because workflow steps use verbs like *consider*, *assess*, *confirm*, or *ensure* without tying them to required artifacts, tool invocations, or exit criteria. That is exactly the failure mode Anthropic warns about when it distinguishes between inline “reference content” and explicit “task content,” and when it notes that `context: fork` only works for skills with actionable prompts rather than general guidance. fileciteturn0file0 citeturn9view0

On description quality, the suite is uneven. The better descriptions are the ones that name concrete inputs and outputs: requirements capture, query writing, ontology validation, and reuse scouting are naturally routable because users actually say things like “define scope,” “find an ontology to reuse,” “write SPARQL,” or “run QC.” The weaker descriptions are the ones that center on a broad domain label rather than a user intent. In the bundle, `ontology-architect/SKILL.md` is the clearest example of description drift: it overlaps upward with `ontology-conceptualizer` and downward with `ontology-validator`, because “design the ontology,” “write axioms,” “structure classes,” “pick templates,” and “prepare for reasoning” can all be read as one large undifferentiated activity. By Anthropic standards, that is a routing smell: if a description can plausibly match three adjacent skills, the description is not doing enough boundary work. fileciteturn0file0 citeturn9view0

On progressive disclosure, the suite is conceptually correct but not yet crisp. The right pattern is present: shared methodology, BFO notes, conventions, and practitioner notes sit outside the skill bodies, which is exactly what Claude Code’s “supporting files” design expects. But the split is not yet disciplined. Several `SKILL.md` files repeat background that should live only once in `_shared/`, while some skills omit the very information that should be inlined because it is routing-critical or execution-critical. The rule here should be simple: the `SKILL.md` should contain boundary, trigger language, required inputs, workflow steps, verification gates, and handoff contract; methodology prose, long examples, command details, and taxonomies should live in `_shared/` and be referenced explicitly. The current suite sometimes reverses that arrangement. fileciteturn0file0 citeturn9view0

On workflow actionability, the suite’s current state is mixed. The best files tell the agent what to produce next. The weaker files tell the agent what a practitioner ought to think about. That distinction matters. A step like “draft the CQ matrix and mark each CQ as structural, taxonomic, relational, or data-bearing” is actionable. A step like “make sure the conceptual model covers the competency questions” is not enough, because an LLM can satisfy it performatively without leaving evidence. Anthropic’s general prompting guidance makes the same point from the other side: strong agent prompts start from clear success criteria and empirical tests, not from prose aspirations. fileciteturn0file0 citeturn10view0

On handoff specification, the bundle is not yet deterministic enough. The handoff sections name artifacts, but several of the artifact contracts still encode implicit social assumptions that work for humans and fail for agents. The core problem is evidentiary rather than stylistic. If an inbound handoff says “conceptual model approved,” the next skill needs to know what counts as approval: a signed checklist, a note in the decision log, a green validation step, a resolved issue reference, or a specific artifact version. If that evidence is not required, the next skill has to guess whether it is safe to proceed, and different models will guess differently. That is the opposite of a reliable harness. fileciteturn0file0

On anti-patterns and error handling, the suite is accurate but under-instrumented. Many anti-patterns are correctly named, but not yet connected to executable checks. The professional ontology toolchain already provides the primitives to do this. The OBO / ROBOT quality-control workflow explicitly centers `validate-profile`, `reason`, `report`, and `verify`; the BFO 2020 repository itself ships SPARQL QC queries as a design-principle enforcement mechanism; and ODK standardizes routine operations for imports, releases, and test runs. A modern skill suite should convert as many warnings as possible into concrete detections, command templates, or hookable checks. citeturn18view0turn21view1turn11view0

The top three strongest skill files are `ontology-validator`, `sparql-expert`, and `ontology-requirements`. `ontology-validator` is strongest because its job is naturally tool-mediated and therefore easiest to operationalize into pass/fail gates. `sparql-expert` is strong because its outputs are executable and falsifiable; a query either runs and supports the CQ or it does not. `ontology-requirements` is strong because the artifact form is already discrete and auditable: scope, users, CQs, non-goals, and acceptance conditions. Those three skills are nearest to Anthropic’s “task content” ideal. fileciteturn0file0 citeturn9view0turn18view0turn19view0

The top three weakest skill files are `ontology-architect`, `ontology-conceptualizer`, and the evolution/maintenance skill in the bundle. `ontology-architect` is weakest because it is overloaded: pattern selection, OWL encoding, DL feature choice, reasoner expectations, and sometimes release/QC concerns are compressed into one boundary. `ontology-conceptualizer` is weak because its most important moves are exactly the ones LLMs are bad at—BFO alignment, scope-sensitive cardinality assumptions, relation semantics—and yet they are not currently guarded by mandatory escalation and verification rules. The evolution/maintenance skill is weak because it sits at the most iterative point in the lifecycle but is not yet backed by explicit loopback, regression, and import-refresh contracts. fileciteturn0file0 citeturn15view0turn18view0turn11view0

### Methodology-to-agent fidelity

The suite succeeds when it translates named ontology methodologies into stable artifacts. It distorts them when it treats methodology as a linear conveyor belt. The current backbone does a good job taking long-form professional practice and re-expressing it as a sequence of agent-usable jobs: requirements, reuse scouting, conceptualization, implementation, mapping, query formulation, validation, and maintenance. That is a legitimate harness design move. It is also consistent with the general insight from ontology engineering literature that scope, requirements, reuse, class/property decisions, and evaluation are separable work products. fileciteturn0file0 citeturn19view0turn3search1

The translation is less faithful when `_shared/methodology-backbone.md` is read as a lifecycle rather than as a navigation aid. The bundle claims alignment to the workflow associated with entity["people","Elisa F. Kendall","ontology engineer"] and entity["people","Deborah L. McGuinness","ontology engineer"], but what survives in the current agent-first reformulation is mostly the middle of the lifecycle: requirements, vocabulary capture, conceptual modeling, formalization, and testing. What gets compressed away are preparatory governance, project-management rhythm, evidence-based iteration, staged publication, and deployment posture. That is not fatal, but it means the backbone is better understood as a skill map than as a faithful lifecycle implementation. fileciteturn0file0 citeturn3search0turn3search1

The three-pipeline model is useful as a user-facing simplification and as a routing heuristic. It is not faithful as a process model. Professional ontology work is strongly iterative: reuse discoveries change scope; modeling choices invalidate CQs; mappings expose conceptual mismatch; validation results force redesign; imports refreshes trigger maintenance modeling. The pipeline framing becomes misleading whenever it suggests that “new ontology,” “mapping,” and “evolution” are separable tracks rather than constantly reconnecting loops. The right fix is not to remove the pipelines. It is to mark every pipeline stage with explicit loopback conditions and target skills. fileciteturn0file0 citeturn16view2turn20view0

The CQ through-line is present in the bundle, but it weakens materially after the early phases. That is the biggest methodological fidelity problem. The professional literature is clear that competency questions are not just a discovery aid; they are a scope test and later a litmus test for adequacy. entity["book","Ontology Development 101","Stanford guide"] states this directly, and the current suite does not yet enforce it strongly enough at later phases. In the current skill design, CQs are strongest in requirements and conceptualization, present but softer in architecture, and too easy to treat as “nice to have” by the time the process reaches validation and maintenance. CQ traceability should survive all the way to executable SPARQL, anti-pattern checks, and regression gates. fileciteturn0file0 citeturn19view0

The BFO alignment procedure is conceptually sound as a default commitment. It is strengthened by the fact that entity["organization","International Organization for Standardization","standards body"] published BFO as ISO/IEC 21838-2, and the BFO repository itself positions BFO as a top-level hub for domain-ontology suites. That is fully compatible with the repo’s “do not abandon BFO” constraint. But the suite still underestimates how often BFO alignment is ambiguous in practice—for example, when distinguishing qualities from measurement data, roles from functions, or processes from plans and procedures. The problem is not that `_shared/bfo-categories.md` mentions the categories. The problem is that `ontology-conceptualizer` does not yet force the agent to stop, mark uncertainty, and escalate when ambiguity is high. fileciteturn0file0 citeturn21view0turn21view1

### Professional-ontologist parity

The bundle’s `practitioner-insights.md` correctly surfaces many gaps, but several professional practices are still missing or underweighted even after accounting for the current remediation work. The most important additional gap is pattern-based modeling as a first-class practice rather than an occasional implementation trick. Modern modular ontology work treats reusable patterns as templates for modules, documentation, and controlled axiomatization, not merely as examples on the side. The modular ontology modeling literature is explicit that modules and ontology design patterns support divide-and-conquer modeling, localized change, and clearer documentation. That missing practice belongs primarily in `ontology-scout`, `ontology-conceptualizer`, and `ontology-architect`, with a new shared file such as `_shared/pattern-catalog.md` and worked examples showing when to choose ROBOT templates, DOSDPs, or hand-authored OWL. Minimum viable addition: one shared file plus one explicit workflow step in scout and architect. Complete treatment: pattern library, pattern provenance, and OPLa-like reuse annotations in the artifacts. fileciteturn0file0 citeturn16view2turn16view1

A second missing practice is explicit mapping evaluation discipline. The bundle already recognizes mappings, but it does not yet treat mapping quality the way ontology-alignment practice does. OAEI evaluations still center precision, recall, and F-measure, and the conference track explicitly distinguishes reference alignments that are free of consistency and conservativity violations. SSSOM and SEMAPV go further by requiring mapping metadata about justification, process, review, and confidence. In the current suite, that material should land primarily in the mapping skill, secondarily in validator and maintainer, with new shared references such as `_shared/mapping-evaluation.md` and `_shared/sssom-semapv-recipes.md`. Minimum viable addition: require `mapping_justification`, confidence, reviewer, and evaluation summary for every accepted mapping set. Complete treatment: gold sets, OAEI-style metrics, clique/transitivity checks, and bridge-ontology repair workflows. fileciteturn0file0 citeturn13view0turn12view0turn12view1turn11view4

A third missing practice is modularization discipline beyond simple `owl:imports`. Professional practice distinguishes at least three things that the current suite tends to blur: importing reusable upstream modules, creating local modules for documentation and maintenance, and separating distinct but linked commitments through bridge structures or more formal modularization devices such as ε-connections-inspired decomposition. The point is not that the suite should implement ε-connections directly. The point is that it should teach the agent when *not* to solve every mismatch with a bigger import closure. This belongs in scout, architect, and the evolution skill, with a new shared file `_shared/modularization-and-bridges.md`. Minimum viable addition: a decision table for import vs local module vs bridge ontology. Complete treatment: worked bridge-ontology lifecycle and selective import strategy. fileciteturn0file0 citeturn22view0turn16view2

A fourth missing practice is closure-axiom discipline. This is a classic professional modeling issue and an unusually important LLM issue because models are prone to produce “all values from” or cardinality restrictions without understanding open-world consequences or reasoner/profile implications. The classic pizza tutorial remains valuable here: closure axioms are how one “closes off” a property under open-world reasoning, and OWL 2 EL does not support universal restrictions, cardinality restrictions, or disjoint union. The current suite needs a dedicated shared reference explaining when to add closure axioms, when not to, and when an EL-targeted ontology must switch reasoners or redesign. This belongs in conceptualizer, architect, validator, and sparql-expert. Minimum viable addition: `_shared/closure-and-open-world.md`. Complete treatment: worked examples comparing ELK-safe and DL-only encodings. fileciteturn0file0 citeturn23view0turn15view0

A fifth missing practice is provenance modeling at realistic granularity. The current bundle mentions justification and decisions, but it does not yet present a robust provenance pattern for ontology engineering artifacts, mapping reviews, validation events, or release events. PROV-O is a strong fit here, especially its qualified forms, which are explicitly intended for cases where more detail is needed about influences, associations, times, plans, and roles. This belongs in maintainer, mapper, validator, and governance docs, with a new shared file `_shared/provenance-recipes.md`. Minimum viable addition: a recipe for qualifying reviews, human approvals, automated validations, and mapping curation. Complete treatment: provenance graph conventions for all handoffs and releases. fileciteturn0file0 citeturn14view0turn14view1turn14view3

A sixth missing practice is publication and discoverability engineering. The bundle is strong on development, weaker on publication. Professional ontology work does not end at “released OWL file.” W3C’s vocabulary-publishing guidance covers dereferenceable ontology IRIs and content negotiation, and Google recommends JSON-LD for structured data publication when SEO/discoverability matters. The current suite should not turn into a web-publishing framework, but it should have a release-time skill path for ontology-as-a-service publication, content negotiation, and optional schema.org JSON-LD exposure for high-level catalog entities. This belongs in the evolution skill and shared release docs. Minimum viable addition: `_shared/publication-recipes.md` and `_shared/imports-manifest.md`. Complete treatment: release packaging, catalog landing pages, machine-readable metadata, and discoverability tests. fileciteturn0file0 citeturn11view3turn11view2turn11view1

A seventh missing practice is load-bearing integration with ODK and release automation as a modeled workflow, not a background assumption. ODK already standardizes `refresh-imports`, `prepare_release`, complete test runs, and profile validation. If ROBOT and ODK are “load-bearing,” the skills should treat those commands as first-class workflow gates, especially in validation and maintenance. This belongs in architect, validator, and maintenance, with explicit support materials `_shared/odk-integration.md`, `_shared/github-actions-template.md`, and `_shared/imports-manifest.md`. Minimum viable addition: command templates and expected outputs. Complete treatment: CI templates and release-run checklists. fileciteturn0file0 citeturn11view0turn18view0

### Agent-specific failure modes

The suite currently acknowledges that LLMs are uneven at ontology work, but that awareness has not yet been encoded into the skills as a formal acceptance regime. That is the main gap. The correct design is to distinguish two classes of steps. Some steps produce advisory material that can be accepted on human review alone. Other steps produce ontology artifacts whose correctness is not credibly established until an external tool checks them. The current bundle gestures toward that distinction. It should make it explicit. fileciteturn0file0 citeturn18view0turn15view0

The skills that most need explicit “LLM verification required” markers are `ontology-conceptualizer`, `ontology-architect`, the mapping skill, `sparql-expert`, and the maintenance skill. Conceptualizer needs it for BFO alignment, cardinality assumptions, relation semantics, and class-vs-quality-vs-datum calls. Architect needs it for every DL-relevant encoding choice: closure axioms, cardinalities, disjoint unions, property chains, equivalence axioms, and profile claims. Mapper needs it for exact/broad/narrow semantics and clique repair. Sparql-expert needs it for CQ-derived tests before claiming a CQ is satisfied. Maintenance needs it whenever imports refresh or semantic changes can alter inference. Validator itself is the gatekeeper rather than the producer, so its “verification” need is mostly evidentiary rather than epistemic. fileciteturn0file0 citeturn11view4turn13view0turn18view0

The cleanest encoding is not frontmatter alone. Add a required markdown section to every `SKILL.md` called `## Verification gates`, with a compact table containing: step, risk class, required external verifier, pass criterion, and loopback target on failure. Then add a required `## Progress criteria` section so the agent knows when the skill is actually done. Anthropic’s current guidance already pushes skill authors toward explicit task prompts and explicit success criteria; the template should extend that logic into ontology-specific validation. fileciteturn0file0 citeturn10view0turn9view0

The suite should make several tool invocations mandatory before completion is claimed. For `ontology-architect`, completion must require `ROBOT validate-profile --profile DL` and `ROBOT reason`, plus a profile-aware note if the intended operational reasoner is EL-only. For `ontology-validator`, the full gate should be `validate-profile` → `reason` → `report` → `verify`, with `pySHACL` added whenever shapes and data graphs are in scope. For `sparql-expert`, a preflight execution on a sample or target graph must be required, because a plausible query is not the same thing as a valid query. For mapping work, at minimum the accepted mapping set should pass SSSOM metadata checks, exact-match clique/transitivity checks, and consistency/conservativity checks when bridge semantics are used. citeturn18view0turn17search0turn11view4turn13view0

The “confident but wrong” problem needs an explicit recovery workflow. The right pattern is not “fix and continue.” It is: capture the failing artifact, classify the failure, roll back to the last passing handoff, isolate the minimal reproducer, revise the conceptual assumption or axiom pattern that caused the failure, rerun the mandatory checks, and record the incident in the decision log. Failure classes should include at least syntax/profile violation, incoherence/inconsistency, unsupported-reasoner construct, ambiguous BFO alignment, incorrect mapping predicate, and CQ/query mismatch. That recovery workflow should be identical across architect, mapper, sparql, validator, and maintenance so the harness behaves consistently. fileciteturn0file0 citeturn18view0turn15view0

### Architectural coherence

Eight skills is still a plausible number, but only if the boundaries are narrowed and the shared materials get sharper. The main structural problem is not that there are eight. It is that one or two of the eight are carrying the cognitive load of twelve. That is why the current architecture feels coherent at a distance and blurry in operation. fileciteturn0file0

`ontology-architect` is the biggest coherence problem. Today it is simultaneously pattern selector, OWL encoder, DL profile chooser, reasoner-aware modeler, and sometimes quasi-validator. That is too much. My recommendation is not an immediate hard split in the first implementation wave; the fastest path is to narrow its boundary and extract pattern, profile, closure, and verification materials into shared files. But the bundle should define a conditional phase-two split path if evaluations still show routing confusion after the redlines land. fileciteturn0file0 citeturn15view0turn18view0

`sparql-expert` and `ontology-validator` should remain cross-cutting skills rather than being subsumed. They do different jobs. SPARQL authoring is about turning questions, extraction needs, and anti-pattern definitions into executable graph queries. Validation is about quality gates, pass/fail judgment, and remediation. The literature supports that separation: graph querying and graph validation are distinct technical activities, even when they interact tightly in practice. fileciteturn0file0 citeturn20view0turn18view0

The pipelines are not the right place to add more ontology phases, but they are the right place to add more named *entry routes*. In addition to the current decomposition, the workspace should expose at least three named pipeline aliases: **audit existing ontology**, **add terms to existing ontology**, and **refresh imports after upstream release**. Those are recurring user intentions that currently get forced into broader skills and broader pipelines. They should be implemented as routable entry recipes or lightweight orchestrator skills, not necessarily as brand-new full skills. fileciteturn0file0 citeturn11view0turn18view0

The shared reference set is not yet complete for the architecture it is trying to support. The bundle is missing exactly the kinds of references that make agentic skills safe and portable: SHACL guidance, ODK integration, imports manifests, CI templates, LLM-verification patterns, and domain-calibrated worked examples. Those are not nice extras. They are the missing pieces that let the current architecture become deterministic. fileciteturn0file0 citeturn11view0turn17search0turn10view0

## Part II — Recommendations

### Per-skill redlines

#### ontology-requirements

**Target file:** `.claude/skills/ontology-requirements/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Capture ontology scope, stakeholders, intended users, competency questions, non-goals, and acceptance criteria for a new ontology or major extension. Use when a request is vague, when domain notes must become a scoped ontology plan, or when you need to decide whether work belongs in ontology modeling, mappings, or downstream data/application logic.”
  **Rationale:** routes on real user language and establishes exclusion boundaries. That is closer to Anthropic guidance on natural trigger wording and boundary-specific descriptions. citeturn9view0

- **Activation triggers**
  “define scope”, “write competency questions”, “capture use cases”, “requirements package”, “is this an ontology problem?”, “non-goals”, “acceptance criteria”, “stakeholders”, “what should this ontology cover?”

- **Structural workflow changes**
  Add a first decision step: **ontology vs mapping vs application logic boundary test**.
  Add a required **CQ matrix** step with: priority, expected answer shape, testability, and downstream validation owner.
  Add a required **non-goals and exclusions** step.
  Add a final **approval evidence** step that records how requirements were accepted.

- **New shared-reference dependencies**
  `_shared/cq-traceability.md`
  `_shared/scope-and-nongoals.md`
  `_shared/llm-verification-patterns.md`

- **Worked examples to add**
  `worked-examples/microgrid/requirements-scope-vs-nongoals.md` — distinguishes ontology scope from operational analytics and dashboard requirements.

- **Handoff-checklist changes**
  Require `requirements.md`, `cq-matrix.tsv`, `non-goals.md`, `decision-log.md`, and an explicit approval note.

- **Anti-patterns to add/remove**
  Add: “ontology every noun,” “unanswerable CQ,” “scope stated without non-goals,” “requirements approved without evidence.”
  Remove any anti-pattern phrased only as general caution and replace with an artifact check.

#### ontology-scout

**Target file:** `.claude/skills/ontology-scout/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Find, compare, and recommend reusable ontologies, modules, relations, patterns, and imports. Use when you need to reuse existing terms, choose between upstream sources, decide whether to import or bridge, or prepare a reuse decision memo before conceptual modeling.”

- **Activation triggers**
  “reuse existing ontology”, “what should we import”, “find BFO/RO/IAO/PROV-O terms”, “compare ontologies”, “should we bridge or import”, “candidate upstreams”

- **Structural workflow changes**
  Add a **reuse-decision matrix** with scope fit, license, maintenance cadence, import size, identifier policy, and profile implications.
  Add a **module vs import vs bridge** decision step.
  Add a **rejection rationale** step for each non-selected candidate.

- **New shared-reference dependencies**
  `_shared/reuse-decision-template.md`
  `_shared/imports-manifest.md`
  `_shared/modularization-and-bridges.md`
  `_shared/pattern-catalog.md`

- **Worked examples to add**
  `worked-examples/microgrid/reuse-decision-provo-ro-iao.md` — choosing provenance, relation, and information-artifact reuse without over-importing.

- **Handoff-checklist changes**
  Require `reuse-memo.md`, `candidate-comparison.tsv`, `imports-manifest-draft.tsv`, `rejected-candidates.md`.

- **Anti-patterns to add/remove**
  Add: “import whole upstream by default,” “reuse by label similarity only,” “no version pinning,” “no bridge strategy for partial alignment.”

#### ontology-conceptualizer

**Target file:** `.claude/skills/ontology-conceptualizer/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Turn approved requirements and reuse decisions into a BFO-aligned conceptual model: classes, relations, roles, qualities, processes, generically dependent continuants, cardinality assumptions, disjointness candidates, and unresolved modeling questions.”

- **Activation triggers**
  “conceptual model”, “BFO alignment”, “class vs quality”, “role or function”, “model the domain concepts”, “relations and cardinalities”, “property candidates”

- **Structural workflow changes**
  Add a **mandatory BFO ambiguity checkpoint** with confidence levels and escalation rules.
  Add a **relation-semantics sheet** before any OWL encoding.
  Add a **closure/open-world review** for every cardinality-like domain assumption.
  Add a **CQ coverage map** linking each CQ to prospective concepts and relations.

- **New shared-reference dependencies**
  `_shared/bfo-categories.md`
  `_shared/relation-semantics.md`
  `_shared/closure-and-open-world.md`
  `_shared/llm-verification-patterns.md`

- **Worked examples to add**
  `worked-examples/microgrid/quality-vs-datum-vs-process.md` — `StateOfCharge` as a BFO quality, observation result as a datum/GDC, and inspection as process.

- **Handoff-checklist changes**
  Require `conceptual-model.md`, `bfo-alignment.tsv`, `relation-semantics.tsv`, `cardinality-assumptions.tsv`, `cq-coverage.tsv`, and explicit unresolved issues.

- **Anti-patterns to add/remove**
  Add: “treating information artifacts as qualities,” “BFO alignment without confidence tag,” “hidden cardinality assumption,” “premature OWL syntax.”
  Remove generic “be careful with BFO” wording and replace with explicit escalation triggers.

#### ontology-architect

**Target file:** `.claude/skills/ontology-architect/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Encode the approved conceptual model into OWL/ROBOT artifacts using profile-aware axiom patterns, reusable templates, and explicit reasoning assumptions. Use when you need to author axioms, restrictions, property chains, value partitions, disjoint unions, or ontology modules from a validated conceptual model.”

- **Activation triggers**
  “write OWL axioms”, “encode restrictions”, “create ROBOT templates”, “property chain”, “value partition”, “disjoint union”, “profile-aware modeling”, “closure axioms”

- **Structural workflow changes**
  Reorder the workflow as: **choose target profile and reasoner** → **select pattern/template strategy** → **encode axioms** → **run mandatory profile/reasoning checks** → **package source artifacts and rationale**.
  Add a **construct support matrix** step: if ELK is targeted, flag any universal restriction, cardinality, or disjoint union immediately.
  Add a **source-of-truth rule**: repetitive or compositional branches should default to ROBOT templates or DOSDPs rather than freehand OWL.

- **New shared-reference dependencies**
  `_shared/owl-profile-playbook.md`
  `_shared/pattern-catalog.md`
  `_shared/odk-integration.md`
  `_shared/llm-verification-patterns.md`
  `_shared/closure-and-open-world.md`

- **Worked examples to add**
  `worked-examples/reasoner/stringquartet-qualified-cardinality.md` — qualified cardinality authored under an EL assumption, silently ignored by ELK, then repaired with DL reasoning and updated gating.
  `worked-examples/microgrid/disjoint-union-vs-el-profile.md` — disjoint union allowed in OWL DL but not OWL 2 EL.

- **Handoff-checklist changes**
  Require `ontology-edit.owl`, source TSV/templates, `axiom-rationale.md`, `profile-check.txt`, `reasoning-output.txt`, and a note on intended operational reasoner.

- **Anti-patterns to add/remove**
  Add: “freehand repetitive axiom authoring,” “OWL profile not declared,” “EL reasoner assumed for DL constructs,” “closure axiom added without open-world rationale.”
  Remove broad stylistic warnings that are better handled as validation gates.

#### ontology-mapper

**Target file:** mapping skill `SKILL.md` in the current suite fileciteturn0file0

- **Description field — proposed text**
  “Create, review, and maintain cross-ontology mappings using SSSOM with explicit predicates, justifications, provenance, confidence, and repair checks. Use when aligning terms, producing crosswalks, reviewing mapping candidates, or maintaining bridge mappings over time.”

- **Activation triggers**
  “map these ontologies”, “exact or broad match”, “crosswalk”, “SSSOM”, “review mapping candidates”, “bridge ontology”, “harmonize identifiers”

- **Structural workflow changes**
  Split the workflow into **candidate generation**, **curation**, **evaluation**, and **repair**.
  Add a required **mapping predicate decision tree**.
  Add required SSSOM metadata: `mapping_justification`, confidence, reviewer, date, and method provenance.
  Add **exactMatch clique/transitivity checks** and **consistency/conservativity checks** prior to merge.

- **New shared-reference dependencies**
  `_shared/mapping-evaluation.md`
  `_shared/sssom-semapv-recipes.md`
  `_shared/bridge-ontology-maintenance.md`
  `_shared/llm-verification-patterns.md`

- **Worked examples to add**
  `worked-examples/mappings/exactmatch-transitivity-trap.md` — demonstrates why an appealing local `skos:exactMatch` can become globally wrong when closure is considered.

- **Handoff-checklist changes**
  Require candidate mappings, accepted mappings, rejected mappings, evaluation metrics, and repair notes as separate artifacts.

- **Anti-patterns to add/remove**
  Add: “exactMatch means ‘pretty close’,” “accepted and candidate mappings mixed together,” “mapping without justification,” “no review provenance.”

#### sparql-expert

**Target file:** `.claude/skills/sparql-expert/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Turn competency questions, extraction needs, and QC rules into executable SPARQL queries, preflight them on target graphs, and package them as acceptance tests, diagnostic reports, or regression checks.”

- **Activation triggers**
  “write SPARQL”, “translate CQ to query”, “acceptance query”, “ontology QC query”, “ASK test”, “SELECT report”, “CONSTRUCT diagnostic view”

- **Structural workflow changes**
  Add a **CQ decomposition** step: variables, expected result type, data assumptions, and failure interpretations.
  Require a **preflight execution** step.
  Pair each query with either an expected answer pattern or an explanation of why empty results are acceptable.

- **New shared-reference dependencies**
  `_shared/cq-traceability.md`
  `_shared/sparql-preflight.md`
  `_shared/llm-verification-patterns.md`

- **Worked examples to add**
  `worked-examples/sparql/ask-plus-diagnostic-select.md` — one ASK query for pass/fail and one SELECT query for diagnosis.

- **Handoff-checklist changes**
  Require `.sparql` files, expected-results notes, runner command, target graph assumptions, and CQ links.

- **Anti-patterns to add/remove**
  Add: “no preflight run,” “query conflates no data with false answer,” “unspecified imports context,” “query delivered without prefixes or sample invocation.”

#### ontology-validator

**Target file:** `.claude/skills/ontology-validator/SKILL.md` fileciteturn0file0

- **Description field — proposed text**
  “Run the ontology quality gate: OWL profile validation, reasoning, ROBOT report/verify checks, shape-based validation where relevant, and CQ regression. Use when deciding pass/fail for merge, release, or handoff.”

- **Activation triggers**
  “validate ontology”, “run QC”, “profile check”, “reasoner”, “ROBOT report”, “ROBOT verify”, “pySHACL”, “release gate”

- **Structural workflow changes**
  Make the command order explicit: **validate-profile → reason → report → verify → pySHACL if in scope → CQ regression summary**.
  Add explicit **severity thresholds** and what counts as a blocking failure.
  Add a required **loopback target** field for each failed gate.

- **New shared-reference dependencies**
  `_shared/qc-thresholds.md`
  `_shared/shacl-patterns.md`
  `_shared/github-actions-template.md`
  `_shared/llm-verification-patterns.md`

- **Worked examples to add**
  `worked-examples/validator/profile-fail-exact-cardinality.md`
  `worked-examples/validator/custom-verify-antipattern.md`

- **Handoff-checklist changes**
  Require raw outputs, machine-readable status summary, triaged failures, and recommended next skill.

- **Anti-patterns to add/remove**
  Add: “pass with untriaged warnings,” “reasoner mismatch not declared,” “validation claimed without output artifacts,” “shape validation run against ontology graph when data graph was intended.”

#### ontology-maintainer

**Target file:** maintenance/evolution skill `SKILL.md` in the current suite fileciteturn0file0

- **Description field — proposed text**
  “Safely evolve a released ontology: term additions, deprecations, imports refreshes, upstream sync, change impact analysis, regression runs, and release packaging. Use when modifying an existing ontology rather than designing from scratch.”

- **Activation triggers**
  “update existing ontology”, “refresh imports”, “release update”, “deprecate term”, “upstream sync”, “semantic change impact”, “add classes to existing ontology”

- **Structural workflow changes**
  Add a first **change classification** step: annotation-only, structural, semantic, mapping, release-infra.
  Add required **ODK import refresh** and **full regression** steps for any upstream change.
  Add a **release-note provenance** step.

- **New shared-reference dependencies**
  `_shared/imports-manifest.md`
  `_shared/odk-integration.md`
  `_shared/change-impact-playbook.md`
  `_shared/publication-recipes.md`

- **Worked examples to add**
  `worked-examples/maintenance/import-refresh-breaks-cq.md` — an upstream import changes inferences and breaks an existing CQ.

- **Handoff-checklist changes**
  Require diff summary, impact matrix, regenerated imports manifest, release notes, regression outputs, and rollback note.

- **Anti-patterns to add/remove**
  Add: “annotation-only used to mask semantic change,” “silent upstream drift,” “release without CQ regression,” “deprecation without successor guidance.”

### Shared-material changes

The shared material should stop being a mixed collection of background notes and become a deliberately layered reference stack: methodology, modeling decisions, executable verification, and worked examples. The current `_shared` files have the right instincts. They need sharper boundaries and more extraction. fileciteturn0file0

For `_shared/methodology-backbone.md`, keep the current lifecycle map and pipeline orientation. Expand it with explicit loopback arrows, entry/exit artifacts per stage, and a CQ traceability strip that persists across all stages. Extract detailed examples into `_shared/cq-traceability.md` and `_shared/change-impact-playbook.md`. This file should remain the one-page “how the suite thinks” backbone, not the place where all operational detail accumulates. fileciteturn0file0

For `_shared/bfo-categories.md`, keep the category overview and the commitment to BFO as the default upper ontology. Expand it with ambiguity checkpoints for role vs function, quality vs datum, process vs plan, object vs fiat part, and GDC vs SDC. Extract the heavier worked examples into `_shared/bfo-decision-recipes.md`. This file should be the summary; the recipes should live elsewhere. BFO’s status as an ISO-published top-level ontology and as a hub for ontology suites makes that investment worthwhile. fileciteturn0file0 citeturn21view0turn21view1

For the current CQ/reuse/modeling shared notes in the bundle, keep the parts that explain why CQs matter and why reuse matters. Expand them with **artifact forms** rather than more prose. Extract long rationale or literature review into `_shared/professional-method-appendix.md`, and keep only the operational minimum in the live skill references. This better matches Anthropic’s progressive-disclosure model. fileciteturn0file0 citeturn9view0turn19view0

For any current validation or SPARQL shared notes, keep the command skeletons and query idioms. Expand them with “expected outputs” and “failure interpretations.” Extract tool-specific long form references to `_shared/odk-integration.md`, `_shared/shacl-patterns.md`, and `_shared/qc-thresholds.md`. ROBOT already has a clean QC vocabulary; the shared docs should mirror it. fileciteturn0file0 citeturn18view0turn11view0

The specific new shared-reference files I recommend are these:

- `_shared/cq-traceability.md`
  One-page artifact spec for linking each CQ to concepts, axioms, queries, and regression tests. Referenced by requirements, conceptualizer, sparql-expert, validator, maintainer.

- `_shared/llm-verification-patterns.md`
  Marks which outputs are advisory vs tool-verified, with standard recovery workflows. Referenced by conceptualizer, architect, mapper, sparql-expert, validator, maintainer.

- `_shared/owl-profile-playbook.md`
  Explains OWL EL/QL/RL/DL implications, reasoner expectations, unsupported constructs, and required checks. Referenced by architect and validator. Ground it in the W3C profiles specification. citeturn15view0

- `_shared/closure-and-open-world.md`
  Closure axioms, universal restrictions, cardinality, and when open-world reasoning changes the interpretation. Referenced by conceptualizer, architect, validator, sparql-expert. citeturn23view0

- `_shared/relation-semantics.md`
  Relation-choice guide, including when to reuse RO or local properties, and how to state domain/range assumptions. Referenced by conceptualizer and architect. citeturn6search13

- `_shared/pattern-catalog.md`
  Short library of pattern choices: ROBOT template, DOSDP, hand-authored OWL, local module, bridge module. Referenced by scout and architect. citeturn16view2turn16view1

- `_shared/mapping-evaluation.md`
  OAEI-style metrics, consistency/conservativity checks, and what “good enough” means for downstream merge. Referenced by mapper and validator. citeturn13view0

- `_shared/sssom-semapv-recipes.md`
  Required SSSOM fields, mapping justifications, provenance, review vocabulary, and examples. Referenced by mapper and maintainer. citeturn12view0turn12view1

- `_shared/modularization-and-bridges.md`
  Import vs local module vs bridge ontology vs stronger modular separation. Referenced by scout, architect, maintainer. citeturn22view0turn16view2

- `_shared/odk-integration.md`
  ODK commands, expected outputs, import refresh discipline, release prep, and how skills should cite them. Referenced by architect, validator, maintainer. citeturn11view0

- `_shared/imports-manifest.md`
  Manifest format for import source, version, reason, refresh schedule, local module boundary, and impact notes. Referenced by scout and maintainer.

- `_shared/github-actions-template.md`
  CI skeleton for validate-profile, reason, report, verify, import refresh, and CQ regression. Referenced by validator and maintainer.

- `_shared/shacl-patterns.md`
  When SHACL is in scope, which graphs it applies to, how `pySHACL` fits, and common false-assumption traps. Referenced by validator and maintainer. citeturn2search2turn17search0

- `_shared/provenance-recipes.md`
  PROV-O-based recipes for approvals, validations, mapping reviews, and releases. Referenced by mapper, validator, maintainer. citeturn14view0turn14view1

- `_shared/publication-recipes.md`
  Dereferenceable IRIs, content negotiation, release metadata, and optional JSON-LD/schema.org catalog exposure. Referenced by maintainer. citeturn11view3turn11view2

### Governance changes

`CONVENTIONS.md` should remain the normative center of the suite, but it needs to move from “safe behavior” to “safe and checkable behavior.” The current non-negotiables are directionally correct; the missing additions are mostly about verification and loopback. fileciteturn0file0

Add these non-negotiable rules:

- **LLM-generated axioms must pass `validate-profile` and `reason` before handoff.**
- **Any CQ claimed as satisfied must be linked to an executable query or entailment check.**
- **Accepted mappings must carry SSSOM justification, provenance, and review metadata.**
- **`skos:exactMatch` mappings must be clique-checked and transitivity-reviewed before merge.**
- **Any import refresh must regenerate the imports manifest and rerun regression checks.**
- **No downstream skill may silently accept an upstream artifact that fails a declared verification gate.**

These additions are justified by existing OBO / ROBOT practice, OWL profile constraints, SSSOM metadata norms, and SKOS exact-match semantics. citeturn18view0turn15view0turn12view0turn11view4

Add a new section to `CONVENTIONS.md` called **Iteration and loopback**. It should codify when a downstream skill must reject a handoff, what defect classes exist, where the artifact loops back to, and how rejection is recorded. The suite currently behaves as if iteration exists. It should instead specify it. That is the single most important governance upgrade after verification gates. fileciteturn0file0

For the authoring standard, make these sections required in every skill:

- `## Use when`
- `## Do not use when`
- `## Required inputs`
- `## Core workflow`
- `## Verification gates`
- `## Progress criteria`
- `## Handoff contract`
- `## Failure recovery`
- `## Worked examples`
- `## Shared references`

That aligns better with the way Anthropic frames skill descriptions, task prompts, supporting files, and explicit success criteria. citeturn9view0turn10view0

The updated `SKILL-TEMPLATE.md` boilerplate should be this:

```markdown
---
name: <skill-name>
description: <front-load the primary use case in natural language; include phrases users will actually say; name adjacent exclusions>
context: inline
# optionally:
# disable-model-invocation: true
# allowed-tools:
# agent:
---

# <Skill Title>

## Use when
- <primary triggering intents>
- <non-obvious trigger phrases>

## Do not use when
- <neighboring skills that should handle adjacent tasks instead>

## Required inputs
- <required artifact list>
- <required approval / verification evidence>

## Core workflow
1. <step with required output artifact>
2. <step with required output artifact>
3. <step with required output artifact>

## Verification gates
| Step | Risk class | Required verifier | Pass criterion | On failure |
|------|------------|-------------------|----------------|-----------|

## Progress criteria
- <what must be true before the skill can claim completion>

## Handoff contract
- Outbound artifacts:
- Mandatory evidence:
- Suggested next skill:

## Failure recovery
- <standard rollback / defect classification / loopback instructions>

## Worked examples
- <example file and what it demonstrates>

## Shared references
- <shared file> — <why it matters here>
```

### New or merged skills

I do **not** recommend immediate reshaping of the eight-skill set in the first implementation wave. The highest-return move is to narrow boundaries, sharpen descriptions, and add verification/shared materials first. That will solve most of the route-confusion problem at lower effort and lower migration risk. fileciteturn0file0

I **do** recommend defining a conditional phase-two split path for `ontology-architect` if the evaluation harness still shows route confusion after the redlines land. The most defensible split is this:

**New boundary one — `ontology-pattern-engineer`**

```yaml
name: ontology-pattern-engineer
description: Select and apply ROBOT templates, DOSDP patterns, reusable modules, and profile-aware scaffolding when turning an approved conceptual model into implementation structures. Use when repetitive class families, module design, or template-driven generation are needed before hand-authored axioms.
context: inline
```

**New boundary two — `ontology-axiom-engineer`**

```yaml
name: ontology-axiom-engineer
description: Encode approved conceptual models and pattern outputs as OWL axioms, restrictions, disjointness, property chains, value partitions, and closure axioms; choose the appropriate reasoner and pass profile/coherence checks before handoff.
context: inline
```

**Handoff diff**

- `ontology-conceptualizer` would hand off conceptual model, BFO alignment sheet, relation semantics, and cardinality assumptions to `ontology-pattern-engineer`.
- `ontology-pattern-engineer` would hand off templates, module plan, source TSVs, and pattern rationale to `ontology-axiom-engineer`.
- `ontology-axiom-engineer` would hand off ontology draft plus profile/reasoning outputs to `ontology-validator`.

**Migration plan**

- Extract pattern-selection logic, template guidance, and module structure material out of the current `ontology-architect/SKILL.md` into the new pattern skill and `_shared/pattern-catalog.md`.
- Retain OWL-construct authoring, profile/risk matrices, and closure guidance in the axiom skill and `_shared/owl-profile-playbook.md`.
- Leave `sparql-expert` and `ontology-validator` separate.

If the first evaluation cycle shows improved routing without a split, keep the current eight-skill topology and shelve the split.

### Worked-example library design

The best demo domain is a **community microgrid operations and maintenance ontology**. It is close enough to the repo’s energy commitment to be strategically useful, but small enough to audit in one session. It also naturally supports asset, role, quality, process, document, mapping, query, validation, and maintenance tasks. fileciteturn0file0 citeturn21view0turn20view0

**Size target**

- ≤ 30 classes
- ≤ 10 CQs
- one import-level relationship to external standards terms
- one small mapping set
- one release/maintenance update scenario

**Seed term list**

`EnergyAsset`, `GenerationAsset`, `StorageAsset`, `LoadAsset`, `SolarPanel`, `Inverter`, `BatteryModule`, `BatteryManagementController`, `MicrogridSite`, `Technician`, `BackupSupplyRole`, `MaintainerRole`, `StateOfCharge`, `OperatingTemperature`, `EfficiencyQuality`, `ChargeCycle`, `DischargeCycle`, `InspectionProcess`, `MaintenanceProcedure`, `WorkOrder`, `AlarmCode`, `PowerOutputMeasurement`, `ChargeState`, `LowCharge`, `NominalCharge`, `HighCharge`.

**Five highest-priority competency questions**

- Which assets at a given microgrid site can supply backup power during an outage?
- Which battery modules currently bear a low-charge state and therefore require intervention?
- Which inspection processes detected an overheating condition on an inverter?
- Which maintenance procedure applies to an inverter with a specific alarm code?
- Which technician participated in the inspection process that generated a given work order?

**Required axiom patterns**

- **BFO Object:** `SolarPanel`, `Inverter`, `BatteryModule`
- **BFO Role:** `BackupSupplyRole`, `MaintainerRole`
- **BFO Quality:** `StateOfCharge`, `OperatingTemperature`
- **BFO Process:** `InspectionProcess`, `ChargeCycle`
- **BFO GDC:** `MaintenanceProcedure`, `WorkOrder`, `AlarmCode`
- **Qualified cardinality:** `BatteryString` or equivalent component class has exactly one `BatteryManagementController`
- **Property chain:** e.g. `hasPart o locatedIn -> locatedIn`
- **Disjoint union:** `EnergyAsset` disjoint union of `GenerationAsset`, `StorageAsset`, `LoadAsset`
- **Value partition:** `ChargeState` partitioned into `LowCharge`, `NominalCharge`, `HighCharge`

**Why this library works**

It supports BFO alignment, reuse scouting, axiomatization, mapping, query generation, validation, import/maintenance, and regression testing in one domain. It also gives you a realistic place to teach the quality-vs-datum distinction and the open-world/closure distinction, which are both agent failure hotspots. citeturn23view0turn15view0turn21view1

### Evaluation harness design

The evaluation harness should measure not just answer quality, but *workflow reliability*. Anthropic’s own guidance is to define success criteria and build evaluations before trying to improve prompts. The same principle should govern skill evolution here. citeturn10view0

**Minimum viable held-out task set**

Use a frozen baseline of the current skill suite and create a held-out set of tasks in six buckets:

- **Routing tasks**
  Short user requests that should trigger exactly one primary skill and optionally one secondary skill.

- **Requirements tasks**
  Given domain notes, produce scope, non-goals, and CQ matrix.

- **Conceptualization/architecture tasks**
  Given approved requirements, produce BFO-aligned concept sheets and axiom plans.

- **Mapping tasks**
  Given two small vocabularies, produce candidate and accepted SSSOM mappings with metadata.

- **SPARQL tasks**
  Given CQs and a graph, produce executable ASK/SELECT queries.

- **Validation/maintenance tasks**
  Given an ontology or ontology diff, detect anti-patterns, run quality checks, triage failures, and recommend loopback.

**Automated scoring**

- Skill-routing precision / recall / confusion matrix
- Artifact completeness score against expected fields
- `ROBOT validate-profile` pass/fail
- `ROBOT reason` consistency/coherence pass/fail
- `ROBOT report` severity counts
- `ROBOT verify` anti-pattern detection precision / recall / F1
- CQ execution pass rate
- Mapping precision / recall / F1 against gold
- Mapping consistency / conservativity / exact-match clique status
- Maintenance regression delta: did the candidate preserve prior passing CQs?

The OAEI conference evaluation provides the right conceptual template for mapping metrics and alignment repair thinking, while the ROBOT QC stack provides the right foundation for ontology QA. citeturn13view0turn18view0

**Baseline and regression discipline**

- Freeze the current skills as `skills-baseline-v1`.
- Version every subsequent redline set.
- Run the full harness on baseline and candidate revisions.
- Require a non-regression report for any structural skill change.
- Keep a small “tricky failures” bank: EL profile mistakes, over-eager exactMatch, bad closure axioms, and BFO ambiguity cases.

**Why this matters**

Without a harness, the suite will drift toward longer prompts and stronger opinions with no evidence of better performance. With a harness, you can test whether narrower descriptions actually improve routing, whether verification gates reduce hallucinated completion, and whether extracted shared files improve success without hurting latency. citeturn10view0turn9view0

### Prioritized roadmap

The ranking below is based on impact × confidence ÷ effort, with dependencies made explicit. It assumes the current bundle structure and tool commitments stay in place. fileciteturn0file0

1. **Change:** Add mandatory `Verification gates` and `Progress criteria` to `SKILL-TEMPLATE.md` and enforce them through `CONVENTIONS.md`.
   **Files:** `SKILL-TEMPLATE.md`, `CONVENTIONS.md`
   **Effort:** XS
   **Depends on:** none

2. **Change:** Add `Iteration and loopback` policy with reject-and-return rules.
   **Files:** `CONVENTIONS.md`
   **Effort:** XS
   **Depends on:** none

3. **Change:** Rewrite description fields for all eight skills to front-load natural trigger language and neighbor exclusions.
   **Files:** all eight `SKILL.md` files
   **Effort:** S
   **Depends on:** item 1

4. **Change:** Create `_shared/llm-verification-patterns.md` and reference it from all high-risk skills.
   **Files:** new shared file + conceptualizer/architect/mapper/sparql/validator/maintainer `SKILL.md`
   **Effort:** S
   **Depends on:** item 1

5. **Change:** Add CQ traceability artifact and enforce it from requirements through maintenance.
   **Files:** `ontology-requirements/SKILL.md`, `ontology-conceptualizer/SKILL.md`, `sparql-expert/SKILL.md`, `ontology-validator/SKILL.md`, maintenance skill, new `_shared/cq-traceability.md`
   **Effort:** S
   **Depends on:** item 1

6. **Change:** Narrow `ontology-architect` to OWL/profile-aware implementation only.
   **Files:** `ontology-architect/SKILL.md`
   **Effort:** S
   **Depends on:** item 3

7. **Change:** Add explicit BFO ambiguity checkpoint with escalation rules.
   **Files:** `ontology-conceptualizer/SKILL.md`, `_shared/bfo-categories.md`, new `_shared/bfo-decision-recipes.md`
   **Effort:** S
   **Depends on:** item 4

8. **Change:** Add `_shared/owl-profile-playbook.md` and make profile choice mandatory in architect.
   **Files:** new shared file, `ontology-architect/SKILL.md`, `ontology-validator/SKILL.md`
   **Effort:** S
   **Depends on:** item 6

9. **Change:** Add `_shared/closure-and-open-world.md` and closure review step.
   **Files:** new shared file, conceptualizer/architect/validator/sparql skills
   **Effort:** S
   **Depends on:** item 8

10. **Change:** Convert anti-pattern sections into executable detections wherever possible.
    **Files:** `ontology-validator/SKILL.md`, `sparql-expert/SKILL.md`, shared QC files
    **Effort:** M
    **Depends on:** items 4, 5, 8

11. **Change:** Add `_shared/odk-integration.md` and `_shared/imports-manifest.md`.
    **Files:** new shared files, scout/architect/maintainer skills
    **Effort:** S
    **Depends on:** none

12. **Change:** Make import refresh and release gates explicit in maintenance skill.
    **Files:** maintenance skill `SKILL.md`
    **Effort:** S
    **Depends on:** item 11

13. **Change:** Add `_shared/mapping-evaluation.md` and `_shared/sssom-semapv-recipes.md`.
    **Files:** new shared files, mapping skill `SKILL.md`, validator skill
    **Effort:** M
    **Depends on:** item 4

14. **Change:** Require exact-match clique/transitivity checks and mapping provenance before merge.
    **Files:** mapping skill `SKILL.md`, `CONVENTIONS.md`
    **Effort:** S
    **Depends on:** item 13

15. **Change:** Add `_shared/pattern-catalog.md` and pattern-first step in scout/architect.
    **Files:** scout and architect skills, new shared file
    **Effort:** M
    **Depends on:** item 6

16. **Change:** Add `_shared/shacl-patterns.md` and pySHACL gate where relevant.
    **Files:** validator and maintenance skills, new shared file
    **Effort:** S
    **Depends on:** item 4

17. **Change:** Build the microgrid worked-example library.
    **Files:** new `worked-examples/microgrid/` tree
    **Effort:** M
    **Depends on:** items 5, 7, 8, 13

18. **Change:** Implement the evaluation harness with frozen baseline.
    **Files:** `docs/evals/`, CI workflows, baseline snapshot
    **Effort:** M
    **Depends on:** item 17

19. **Change:** Add `_shared/publication-recipes.md` and release/discoverability guidance.
    **Files:** new shared file, maintenance skill, `CONVENTIONS.md`
    **Effort:** M
    **Depends on:** item 11

20. **Change:** Prototype the conditional `ontology-architect` split only if the harness still shows routing confusion after the first wave.
    **Files:** new skill directories if needed, migration notes
    **Effort:** L
    **Depends on:** item 18

## Appendix — Open questions back to the repo owner

- Which eight skill directories are considered stable API surface for users, and which are still experimental? That answer affects whether `ontology-architect` should be narrowed in place or split later. fileciteturn0file0
- Is the intended operational target primarily OWL DL with selective EL-aware optimization, or is EL compatibility a hard design goal for most deliverables? That answer changes several architect and validator defaults. citeturn15view0
- Should mapping deliverables stop at SSSOM artifacts, or is the repo expected to generate and maintain bridge ontologies as first-class outputs? citeturn12view0turn13view0
- Will the agent harness reliably have access to ROBOT, ODK, reasoners, and `pySHACL` in all execution contexts, or do some skills need degraded-mode instructions? citeturn18view0turn17search0turn11view0
- Is publication/discoverability in scope for this workspace, or are ontology releases expected to remain repository-local artifacts? That determines whether the publication recipes should ship in wave one or wave two. citeturn11view3turn11view2
- Does the repo owner want the worked-example library to align tightly with the energy exemplar, or is there value in a second non-energy mini-domain for generalization testing? A dual-domain harness would improve evaluation quality at modest extra cost. fileciteturn0file0
