# Ontology Skills Improvement — Research Output

**Source basis.** I treated the uploaded 2026-04-21 research bundle as the source of truth for current repository state, skill text, shared references, hooks, rules, `CLAUDE.md`, and practitioner-insights. File/section references below name the exact in-bundle path and section being critiqued. External citations are used only where the recommendation is anchored in public methodology or tooling documentation.

## Part I — Critique

### 1. Skill-authoring quality

#### 1.1 Suite-level assessment against Anthropic-style skill authoring

The suite is unusually strong for ontology engineering content, but only moderately strong as an **agent skill package**. The most important issue is that the **metadata descriptions are not carrying enough of the routing burden**. Anthropic’s current skill-authoring guidance is explicit: the `description` field is used for skill discovery, should say both what the skill does and when to use it, should include key trigger terms, and is “critical for skill selection” because Claude chooses among potentially many skills from that field before reading the body. The same guidance also recommends keeping `SKILL.md` under about 500 lines, pushing details to referenced files, using concrete examples, including verification steps for critical operations, and adding feedback loops for quality-critical tasks. ([Claude][1])

**What the suite gets right.** The current `CONVENTIONS.md` requires the right major sections: frontmatter, role statement, activation, shared references, core workflow, commands, outputs, handoff, anti-patterns, and error handling. File/section: `.claude/skills/CONVENTIONS.md` §Skill Authoring Standard. It also enforces shared terminology and tool-selection rules, which prevents drift across the eight skills. File/section: `.claude/skills/CONVENTIONS.md` §Shared Terminology and §Tool Selection Rules.

**What the suite gets wrong.** It over-trusts the body-level “When to Activate” sections. Those are useful after a skill has loaded, but the routing model sees the YAML description first. Several descriptions omit the natural phrases users will actually say, such as “write SPARQL for this CQ,” “check if these mappings are safe,” “refresh imports,” “audit an existing ontology,” “fix a failed reasoner run,” “generate SHACL shapes,” “publish release artifacts,” or “update stale CQs.” File/section: all eight `SKILL.md` files §YAML frontmatter and §When to Activate.

**Progressive disclosure is mostly good but uneven.** The current skill bodies are all under the rough 500-line threshold, with `ontology-architect` at 413 lines and the others around 254–300 lines according to the bundle’s audit. File/section: bundle §7 Current-State Quality Assessment. However, several long shared references do not have a table of contents, and Anthropic guidance recommends a TOC for reference files longer than 100 lines so the agent can navigate selectively. File/section: `_shared/axiom-patterns.md`, `_shared/anti-patterns.md`, `_shared/quality-checklist.md`, `_shared/tool-decision-tree.md`, `_shared/bfo-categories.md` §entire files. ([Claude][1])

**Workflow actionability is high for tools, weaker for process gates.** The architect, validator, mapper, and curator skills include concrete commands. The requirements and conceptualizer skills are more vulnerable because several steps say “gather,” “document,” “review,” or “produce” without a deterministic acceptance check. File/section: `ontology-requirements/SKILL.md` §Step 1 Domain Scoping, §Step 7 Test Suite Generation; `ontology-conceptualizer/SKILL.md` §Step 3 Upper Ontology Alignment, §Handoff checklist.

**Handoffs are explicit in artifact names but not explicit enough in verification state.** The checklists say things like “User has reviewed and approved the conceptual model,” “KGCL patch was reviewed and approved,” and “All Level 1-6 checks have been executed,” but no artifact records who approved what, when, against which diff, and with which unresolved exceptions. File/section: `ontology-conceptualizer/SKILL.md` §Handoff checklist; `ontology-curator/SKILL.md` §Handoff checklist; `ontology-validator/SKILL.md` §Handoff checklist. This is a process integrity gap, not a content gap.

**Anti-patterns are much better than typical, but only half operationalized.** `_shared/anti-patterns.md` gives 16 anti-patterns and several SPARQL detection queries. File/section: `_shared/anti-patterns.md` §1–16. But many detections remain natural-language-only, such as role-type confusion, process-object confusion, circular definition, quality-as-class, information-physical conflation, polysemy, complement overuse, OO inheritance leakage, and system-blueprint modeling. File/section: `_shared/anti-patterns.md` §2, §3, §5–7, §9, §12–15. For an agent workflow, each anti-pattern needs a detection mode: SPARQL, ROBOT report rule, LLM review prompt with required evidence, or manual expert gate.

#### 1.2 Skill-by-skill critique

##### `ontology-requirements`

**Description field quality.** Good but incomplete. It mentions “requirements specification,” “competency questions,” “ORSD,” “CQ test suites,” and “acceptance tests,” which are strong triggers. It misses “stakeholder interview,” “scope boundary,” “use case,” “traceability matrix,” “convert CQs to SPARQL,” “stale CQ,” and “requirements debt.” File/section: `ontology-requirements/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** The CQ taxonomy and use-case YAML template are useful enough to inline. The ORSD template is named as an output but not actually supplied; it should be either inlined or moved to `_shared/orsd-template.md`. File/section: `ontology-requirements/SKILL.md` §Step 1.5, §Outputs.

**Workflow actionability.** Step 7 says to generate `.sparql` files and a manifest, and the tool command validates syntax for one query. It does not require running each query against a sample graph, does not call `sparql-expert`, and does not define how `expected_result` is encoded for `robot verify`. File/section: `ontology-requirements/SKILL.md` §Step 7 Test Suite Generation and §Tool Commands.

**Handoff.** The checklist is good but not deterministic for approval. “Every CQ traces to at least one SPARQL test” is verifiable. “All Must-Have CQs have formalized SPARQL queries” is verifiable. But no `requirements-approval.yaml` or `cq-freeze` gate exists. File/section: `ontology-requirements/SKILL.md` §Handoff checklist.

**Anti-patterns and error handling.** The anti-pattern list is excellent on retroactive CQs and stale tests. The weak point is enforcement: “CQs must be written BEFORE conceptualization begins” is written as a warning, not as a blocking gate checked by `CONVENTIONS.md` or a hook. File/section: `ontology-requirements/SKILL.md` §Anti-Patterns to Avoid.

##### `ontology-scout`

**Description field quality.** The description correctly names reusable ontologies, OLS, BioPortal, OBO Foundry, LOV, ROBOT extraction, and ODPs. It misses user phrasing like “does this term already exist?”, “should we import GO/OEO/QUDT?”, “MIREOT,” “refresh import,” “license compatibility,” “evaluate candidate ontology,” and “find upstream term.” File/section: `ontology-scout/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** Too much import-management detail is embedded in the skill while the import lifecycle is cross-cutting across scout, architect, validator, and curator. The MIREOT/STAR/BOT table should move to a new `_shared/imports-management.md`; the skill should keep a short decision table and reference the deeper material. File/section: `ontology-scout/SKILL.md` §Step 4 Module Extraction.

**Workflow actionability.** Registry search and ROBOT extraction are concrete. The ODP search step is not concrete enough: it lists patterns but provides no source, no pattern template, no selection criteria, and no output schema beyond “Document which ODPs apply.” File/section: `ontology-scout/SKILL.md` §Step 5 ODP Search.

**Handoff.** “ODP recommendations reference specific pattern templates” is a good checklist item, but the skill does not provide the templates. File/section: `ontology-scout/SKILL.md` §Handoff checklist.

**Anti-patterns and error handling.** Error handling covers unreachable OLS, extract failure, no candidates, and missing licenses. It does not cover stale oaklib cache, ontology registry disagreement, incompatible license families, or candidate ontology failing profile validation. File/section: `ontology-scout/SKILL.md` §Error Handling.

##### `ontology-conceptualizer`

**Description field quality.** Good for “conceptual model,” “glossary,” “taxonomy,” “property design,” “BFO,” and “anti-pattern.” It misses “domain/range vs SHACL,” “role vs disposition,” “process vs object,” “value partition,” “closure axiom,” “axiom plan,” “module boundary,” and “layering.” File/section: `ontology-conceptualizer/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** The property-design section duplicates the domain/range anti-pattern because the issue is important enough to inline. That duplication is justified. Architecture layering is introduced in Step 2.5 but not reinforced in outputs beyond a sentence. File/section: `ontology-conceptualizer/SKILL.md` §Step 2.5 Architecture Layering and §Outputs.

**Workflow actionability.** The BFO decision procedure is actionable if the agent actually reads `_shared/bfo-categories.md`. But the skill does not mark ambiguous cases as a mandatory user/expert gate; it only says to document ambiguity for user decision. File/section: `ontology-conceptualizer/SKILL.md` §Step 3 Upper Ontology Alignment and §Anti-Patterns to Avoid.

**Handoff.** The “user approved conceptual model” item is non-deterministic. The handoff should require `docs/conceptual-model-review.md` or `docs/approval-record.yaml` with reviewer, date, accepted exceptions, and unresolved modeling risks. File/section: `ontology-conceptualizer/SKILL.md` §Handoff checklist.

**Anti-patterns and error handling.** The anti-pattern review points to `_shared/anti-patterns.md`, but the conceptualizer does not instruct the agent to run the SPARQL detections once a draft model exists, nor to produce an `anti-pattern-review.md` with false-positive decisions. File/section: `ontology-conceptualizer/SKILL.md` §Step 6 Anti-Pattern Detection.

##### `ontology-architect`

**Description field quality.** Strongest of the suite, but overloaded. It includes POD, OWL 2 axioms, class hierarchies, ROBOT templates, reasoners, ROBOT/oaklib/KGCL/OWLAPY/owlready2/LinkML, and “creating or modifying ontology axioms.” It misses “SHACL shapes,” “DOSDP,” “ODK edit file,” “validate-profile,” “fix unsatisfiable class,” “formalize axiom plan,” and “ROBOT template preflight.” File/section: `ontology-architect/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** At 413 lines it is within Anthropic’s rough body-size guidance but close enough that dense implementation details should be extracted. ROBOT template pitfalls, ODK awareness, LinkML scope, rdflib vs OWLAPY, and reasoner strategy are all cross-cutting and deserve shared references. File/section: `ontology-architect/SKILL.md` §ROBOT Template Pitfalls, §Tool Commands §ODK Awareness, §Step 6 Schema-First via LinkML, §Step 7 Verify.

**Workflow actionability.** Very high for ROBOT, KGCL, rdflib, and reasoning. The weak part is SHACL: it is an output and a one-line validation command, but the skill does not teach shape authoring. File/section: `ontology-architect/SKILL.md` §Step 7 Verify and §Outputs.

**Handoff.** The checklist is useful but under-specified for DL features. “Ontology passes `robot reason`” is not enough if ELK was used while qualified cardinality or complements were present; OWL 2 profiles trade expressivity for reasoning efficiency, and profile choice must be connected to reasoner choice. File/section: `ontology-architect/SKILL.md` §Step 1 Select OWL 2 Profile, §Step 7 Verify. ([W3C][2])

**Anti-patterns and error handling.** Strong on skipping reasoner, hand-editing, metadata, and backups. Error handling should add “ELK silently ignored non-EL axiom,” “profile violation after import merge,” “ROBOT template created partial terms,” and “SHACL shape contradicts OWL axiom.” File/section: `ontology-architect/SKILL.md` §Anti-Patterns to Avoid and §Error Handling.

##### `ontology-mapper`

**Description field quality.** Good but too generic. It mentions mapping, alignment, SSSOM, lexical matching, and LLM verification. It misses “validate mapping,” “mapping QA,” “exactMatch clique,” “sameAs risk,” “bridge ontology,” “obsolete upstream term,” “mapping refresh,” “OAEI metrics,” and “precision/recall.” File/section: `ontology-mapper/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** The skill has the right high-level flow, but SSSOM metadata, predicate semantics, clique checks, bridge ontology conversion, and mapping-maintenance lifecycle should move into `_shared/mapping-evaluation.md` and `_shared/bridge-ontology-lifecycle.md`. File/section: `ontology-mapper/SKILL.md` §Step 4 Mapping Predicate Selection, §Step 5.5 Clique Analysis, §Tool Commands §SSSOM operations.

**Workflow actionability.** Candidate generation, triage, validation, and clique detection are concrete. The LLM verification step gives a prompt skeleton but lacks a scoring rubric, batch format, abstention criteria, and required evidence fields. File/section: `ontology-mapper/SKILL.md` §Step 3 LLM Verification.

**Handoff.** SSSOM validation, CURIE resolution, justifications, confidence scores, and QA report are good. It should also require exact-match clique report, obsolete-term report, and mapping-evaluation metrics against a gold/dev set when available. File/section: `ontology-mapper/SKILL.md` §Handoff checklist.

**Anti-patterns and error handling.** Strong on `exactMatch`, `sameAs`, and stale mappings. Missing: cross-ontology incoherence after bridge conversion and many-to-one exactMatch conflict detection. File/section: `ontology-mapper/SKILL.md` §Anti-Patterns to Avoid and §Error Handling. SSSOM is correctly chosen as the mapping format because it standardizes TSV mappings, metadata elements, and translation to OWL. ([Mapping Commons][3])

##### `ontology-validator`

**Description field quality.** Good for “validate,” “quality assurance,” “reasoners,” “SHACL,” “CQ tests,” “ROBOT reports,” “metrics,” and “diff reports.” It misses “audit ontology,” “find anti-patterns,” “debug failed reasoner,” “validate SSSOM,” “check import freshness,” “validate-profile,” “pre-release gate,” and “CI.” File/section: `ontology-validator/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** OWA/CWA distinction is important enough to inline. The Level 1–7 pipeline is also appropriate. But SHACL templates, anti-pattern queries, and CI/CD examples should be shared references rather than ad hoc commands. File/section: `ontology-validator/SKILL.md` §Consistency vs. Validity, §Core Workflow, §Tool Commands.

**Workflow actionability.** Excellent for Levels 1–4. Levels 5–6 are weaker: “Document qualitative assessments” is correct professional practice, but not an agent acceptance gate. File/section: `ontology-validator/SKILL.md` §Step 5 Coverage Metrics, §Step 6 Evaluation Dimensions. SHACL is a W3C Recommendation for validating data graphs against shapes graphs, so the validator’s OWL-vs-SHACL framing is methodologically sound. ([W3C][4])

**Handoff.** “All Level 1-6 checks have been executed” should require machine-readable result files: `validation-results.yaml`, `reasoner.log`, `robot-report.tsv`, `shacl-results.ttl`, `cq-results.json`, `anti-pattern-results/`, and `diff.md`. File/section: `ontology-validator/SKILL.md` §Handoff checklist and §Quality Report Format.

**Anti-patterns and error handling.** Strong in principle. But if SHACL shapes are missing, the current recovery says “Create minimal shapes or defer SHACL check.” That weakens the validator’s “does not fix issues” role and should instead loop back to architect unless the user explicitly approves a validator-generated temporary shape set. File/section: `ontology-validator/SKILL.md` §Role Statement and §Error Handling.

##### `ontology-curator`

**Description field quality.** Good for maintenance, evolution, versioning, deprecation, KGCL, diff, and release. It misses “obsolete,” “import refresh,” “upstream release,” “mapping maintenance,” “PURL,” “content negotiation,” “FAIR,” “OBO date release,” “release notes,” and “consumer communication.” File/section: `ontology-curator/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** FAIR assessment and release publishing are cross-cutting enough to be in shared references. The skill should keep the release checklist but move content-negotiation, FAIR, OBO release, and publication guidance to `_shared/publication-content-negotiation.md` and `_shared/fair-release.md`. File/section: `ontology-curator/SKILL.md` §Step 5.5 FAIR Assessment and §Release Publishing.

**Workflow actionability.** Deprecation and versioning are strong. Import refresh is a useful shell sketch but lacks manifest inputs, source version pinning, obsolete-term remapping, and mapper handoff. File/section: `ontology-curator/SKILL.md` §Tool Commands §Import refresh.

**Handoff.** “KGCL patch was reviewed and approved by user before applying” has no approval artifact. The skill should require `docs/change-approval.yaml` and `docs/change-impact.md`. File/section: `ontology-curator/SKILL.md` §Handoff checklist.

**Anti-patterns and error handling.** Strong on deletion/deprecation and version bump. Missing: “release without consumer-facing migration notes,” “refresh imports without revalidating mappings,” and “change ontology header without updating publication metadata.” File/section: `ontology-curator/SKILL.md` §Anti-Patterns to Avoid.

##### `sparql-expert`

**Description field quality.** Weakest relative to importance. It says SPARQL 1.1/SPARQL-star, validation, execution, backend differences, query KG/debug SPARQL. It misses ontology-engineering triggers: “write CQ test,” “convert CQ to SPARQL,” “anti-pattern query,” “coverage metric,” “ROBOT query,” “expected zero violations,” “entailment regime,” “mapping clique query,” and “validate query syntax.” File/section: `sparql-expert/SKILL.md` §YAML frontmatter.

**Progressive disclosure.** Good: compact body, references only namespaces and methodology. Missing shared dependency on anti-pattern query library and CQ test conventions. File/section: `sparql-expert/SKILL.md` §Shared Reference Materials.

**Workflow actionability.** Strong for basic local execution and syntax validation. It lacks endpoint authentication setup, named graph discovery commands, and a formal connection to `cq-test-manifest.yaml` expected-result semantics. File/section: `sparql-expert/SKILL.md` §Core Workflow and §Error Handling.

**Handoff.** Query syntax and PREFIX completeness are deterministic. The skill should additionally require the query’s expected entailment regime, expected-result assertion, and target graph/source artifact. File/section: `sparql-expert/SKILL.md` §Handoff checklist and §Entailment Regime Awareness.

**Anti-patterns and error handling.** Strong on PREFIXes, LIMIT, production updates, RDF-star, blank nodes, variable distinctness, and entailment regimes. Needs ontology-specific anti-patterns: `COUNT` query returning one row where manifest expects row count, as seen in the skygest validation report. File/section: `sparql-expert/SKILL.md` §Anti-Patterns to Avoid; `ontologies/skygest-energy-vocab/docs/validation-report-2026-04-14.md` §Phase 3 — DSD wiring.

#### 1.3 Top 3 strongest skill files

1. **`ontology-architect/SKILL.md`**
   Quote-level evidence: “You ALWAYS run the reasoner after structural changes. You NEVER hand-edit ontology files.” File/section: §Role Statement. It also contains concrete ROBOT template TSV, KGCL commands, rdflib example, ODK awareness, and reasoner escalation. File/section: §Step 3, §Step 4, §Step 5, §Tool Commands §ODK Awareness, §Step 7.
   Why strong: it captures real POD behavior rather than abstract ontology advice.

2. **`ontology-mapper/SKILL.md`**
   Quote-level evidence: “The LLM verification step is not optional — it is essential for this tier.” File/section: §Step 2 Confidence Triage. “After validation, compute the transitive closure of `skos:exactMatch` and flag any clique larger than 3 terms for human review.” File/section: §Step 5.5 Clique Analysis.
   Why strong: it recognizes that mapping errors propagate through transitivity and designs an explicit mitigation.

3. **`ontology-validator/SKILL.md`**
   Quote-level evidence: “Use both OWL reasoning and SHACL; they answer different questions.” File/section: §Consistency vs. Validity. The 7-level validation pipeline is the right architecture. File/section: §Core Workflow.
   Why strong: it separates logical consistency, closed-world validation, functional acceptance tests, metrics, qualitative review, and diff review.

#### 1.4 Top 3 weakest skill files

1. **`sparql-expert/SKILL.md`**
   Quote-level evidence: “User mentions ‘SPARQL’, ‘query’, or ‘knowledge graph’.” File/section: §When to Activate.
   Why weak: too generic for routing. It does not foreground the ontology-specific uses that will actually summon it: CQ tests, anti-pattern detection, coverage metrics, mapping clique checks, and validation diagnostics.

2. **`ontology-scout/SKILL.md`**
   Quote-level evidence: “Search for applicable Ontology Design Patterns: Part-Whole, N-ary Relation, Value Partition…” File/section: §Step 5 ODP Search.
   Why weak: ODP guidance is a list, not a workflow. It lacks pattern source, template, instantiation schema, acceptance criteria, and worked examples.

3. **`ontology-requirements/SKILL.md`**
   Quote-level evidence: “CQs must be written BEFORE conceptualization begins — they drive the design, not document it.” File/section: §Anti-Patterns to Avoid.
   Why weak: the rule is correct but not enforced. This skill should be the suite’s strongest process-gate skill, yet it lacks a freeze/approval artifact and a deterministic CQ quality validator.

---

### 2. Methodology-to-agent fidelity

#### 2.1 Where the reformulation succeeds

The phase map is broadly faithful to professional ontology engineering. METHONTOLOGY explicitly frames ontology engineering as a lifecycle from requirements through maintenance, with specification, conceptualization, formalization, integration, implementation, and maintenance states, and it emphasizes early evaluation and documentation. The workspace’s `requirements → scout → conceptualizer → architect → validator → curator` mapping preserves those concerns well. File/section: `_shared/methodology-backbone.md` §Methodology Foundations and §Lifecycle Phases and Skill Mapping. ([Archivo Digital UPM][5])

The CQ through-line is also methodologically justified. Grüninger and Fox characterize an ontology by competency questions and say the ontology must contain a necessary and sufficient axiom set to represent and solve those questions. File/section: `_shared/methodology-backbone.md` §CQ Through-Line; `ontology-requirements/SKILL.md` §Core Workflow. ([Springer][6])

The NeOn emphasis on reuse, collaborative development, ontology networks, and evolution is represented in the scout, mapper, and curator skills. File/section: `_shared/methodology-backbone.md` §Methodology Foundations; `ontology-scout/SKILL.md` §Reuse Decision; `ontology-mapper/SKILL.md` §Core Workflow; `ontology-curator/SKILL.md` §Core Workflow. NeOn is explicitly scenario-based and aimed at collaborative ontology networks and dynamic evolution, so the workspace is right to treat reuse/mapping/maintenance as first-class rather than afterthoughts. ([Ontology Engineering Group][7])

BFO is appropriately treated as a decision procedure rather than just a namespace. ISO/IEC 21838-2 describes BFO as a top-level ontology for information interchange and includes BFO-2020 definitions, OWL 2/CL axiomatizations, and requirements for lower-level ontologies using BFO as a hub. File/section: `_shared/bfo-categories.md` §Decision Procedure and §Known Ambiguities. ([ISO][8])

#### 2.2 K&M 9-phase mapping: faithful but lossy

The `methodology-backbone.md` K&M mapping is a useful compression, but it loses three things. File/section: `_shared/methodology-backbone.md` §K&M Phase Mapping.

First, **business architecture** is collapsed into conceptualization. That is workable for small ontologies, but in real enterprise/KG settings business architecture includes stakeholder workflows, organizational boundaries, application interfaces, data products, and governance context. Conceptualizer Step 2.5 “Architecture Layering” begins to address this, but the layer assignment is not connected back to stakeholder workflows or deployment architecture. File/section: `ontology-conceptualizer/SKILL.md` §Step 2.5 Architecture Layering.

Second, **initial and subsequent term excerption** become scout plus iterative revisit, but there is no operational loopback. The table says “Phase 2 (iterative revisit),” yet the three pipelines remain linear. File/section: `_shared/methodology-backbone.md` §K&M Phase Mapping and §Pipelines.

Third, **review and deployment** are under-modeled. Review is mostly validator, but professional review includes domain expert review of definitions, ontology engineer review of axioms, consumer review of release diffs, and mapping steward review of cross-ontology effects. Deployment is “cross-cutting release/maintenance,” but content negotiation, PURLs, registry submission, documentation generation, and consumer communication are not first-class. File/section: `_shared/methodology-backbone.md` §K&M Phase Mapping; `ontology-curator/SKILL.md` §Release Publishing.

#### 2.3 The three-pipeline model is useful for routing but too linear for practice

Pipeline A/B/C is a good minimal routing model. File/section: `_shared/methodology-backbone.md` §Pipelines. It prevents the agent from treating “build a new ontology,” “map two ontologies,” and “evolve an existing ontology” as the same task.

But the pipelines artificially linearize work that should be iterative:

- Architect failure should loop back to conceptualizer when a selected axiom pattern is unsound or profile-incompatible. File/section: `ontology-architect/SKILL.md` §Error Handling; `ontology-conceptualizer/SKILL.md` §Axiom Pattern Selection.
- Validator failure should loop back to architect, mapper, curator, requirements, or scout depending on the failed gate. File/section: `ontology-validator/SKILL.md` §Role Statement and §Handoff.
- Import refresh should route curator → scout → mapper → validator, not just curator → validator. File/section: `ontology-curator/SKILL.md` §Tool Commands §Import refresh; `ontology-mapper/SKILL.md` §Updating mappings for new ontology version.
- New CQs during maintenance should route curator → requirements → conceptualizer → architect → validator. File/section: `_shared/methodology-backbone.md` §CQ Through-Line and `ontology-curator/SKILL.md` §Core Workflow.

The fix is not to abandon pipelines. The fix is to add a loopback protocol with explicit rejection reasons, owner skill, required artifact, and retry gate.

#### 2.4 CQ through-line is strong early, weaker later

The CQ through-line is strong from requirements through conceptualization: CQs produce a pre-glossary, traceability matrix, and axiom plan. File/section: `ontology-requirements/SKILL.md` §Steps 2–8; `ontology-conceptualizer/SKILL.md` §Step 5 Axiom Pattern Selection.

It weakens in formalization. Architect receives tests “indirectly” and forwards them to validator, but the architect workflow does not require a per-CQ implementation status file, such as `docs/cq-implementation-matrix.csv`. File/section: `ontology-architect/SKILL.md` §Handoff.

It weakens further in maintenance. Curator does not require a CQ impact analysis for deprecations, reparenting, equivalence changes, or import refresh. File/section: `ontology-curator/SKILL.md` §Core Workflow.

It is weakest in mapping. Mapper should use high-priority CQs to evaluate whether a mapping improves integration behavior, not just whether the SSSOM file validates. File/section: `ontology-mapper/SKILL.md` §Quality Report.

#### 2.5 BFO ambiguity is acknowledged but not operationalized

`_shared/bfo-categories.md` is one of the best shared files. It acknowledges disease, organization, information entities, toxicity/drug roles, software, legal entities, money, and BFO 2020 vs BFO 2.0. File/section: `_shared/bfo-categories.md` §Known Ambiguities.

The conceptualizer routes to it only weakly: “If alignment is unclear, consult `_shared/bfo-categories.md` and document the ambiguity for user decision.” File/section: `ontology-conceptualizer/SKILL.md` §Anti-Patterns to Avoid. That is not enough for an LLM. It needs an explicit ambiguity detector:

```yaml
bfo_alignment_status:
  value: aligned | ambiguous | out_of_scope | needs_expert_review
  ambiguity_type: role_vs_disposition | gdc_concretization | object_vs_aggregate | process_vs_disposition | social_construct | other
  default_choice:
  alternative_choices:
  rationale:
  reviewer_required: true|false
```

---

### 3. Professional-ontologist parity

The practitioner-insights file already identifies ODK, ROBOT gotchas, oaklib/KGCL limitations, imports, BFO ambiguity, SSSOM complexity, reasoner performance, domain/range, LinkML scope, SHACL, hand-edit exceptions, CI/CD, CQ failure modes, OWLAPY overemphasis, multi-ontology coordination, LLM limitations, and OBO versioning. File/section: `docs/practitioner-insights.md` §Themes 1–17 and §Summary.

The following additions go beyond that list.

| Missing practice                                  | Why it matters                                                                                                                                                                                                                                                    | Where it lands                                                                                                                                                                   | Minimum viable addition                                                                                       | Complete treatment                                                                                |
| ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **DOSDP / pattern-based OWL expansion**           | Professional OBO projects often use design patterns to generate repeatable logical definitions. DOSDP was created to make OWL class design patterns easy to document, validate, and apply, and it has been adopted by multiple ontology projects. ([Springer][9]) | `ontology-architect` §Bulk creation; `ontology-scout` §ODP Search; new `_shared/dosdp-patterns.md`                                                                               | One shared file with a DOSDP YAML example, TSV filler example, and when to prefer DOSDP over ROBOT templates. | Pattern library with generated docs, validation scripts, example outputs, and CI checks.          |
| **OAEI-style mapping evaluation**                 | Mapping QA needs precision, recall, F-measure, and alignment size against gold/dev sets where available; OAEI uses those standard parameters. ([CEUR-WS][10])                                                                                                     | `ontology-mapper` §Quality Report; `ontology-validator` §SSSOM checks; new `_shared/mapping-evaluation.md`                                                                       | Add optional gold-set evaluation: precision/recall/F1, confusion table by predicate.                          | Full mapping benchmark harness with held-out mapping pairs and regression dashboard.              |
| **E-connections / modularization theory**         | Current module guidance is pragmatic but not theoretically explicit. E-connections-style partitioning helps reason about modules, links, and encapsulation in multi-ontology systems.                                                                             | `ontology-conceptualizer` §Architecture Layering; `ontology-scout` §Module Extraction; `ontology-curator` §Multi-ontology coordination; new `_shared/modularization-patterns.md` | Paragraph distinguishing extraction, partitioning, bridge ontologies, and imports.                            | Module-boundary methodology with dependency graph checks and cross-module reasoning tests.        |
| **Closure-axiom discipline**                      | Universal restrictions alone are vacuously true; closure patterns require explicit existential plus universal treatment. File/section: `_shared/axiom-patterns.md` §3 Universal Restriction.                                                                      | `ontology-conceptualizer` §Axiom Pattern Selection; `ontology-architect` §Complex Axioms; `_shared/axiom-patterns.md`                                                            | Add “closure required?” field to `axiom-plan.yaml`.                                                           | Pattern-specific test fixtures proving expected inferences under OWA.                             |
| **Realistic PROV-O granularity**                  | PROV-O is a W3C OWL2 ontology for representing and exchanging provenance across systems and contexts. ([W3C][11]) Current skills say “use PROV-O” but not what granularity to model.                                                                              | `ontology-scout`, `ontology-architect`, `ontology-curator`; new `_shared/provenance-patterns.md`                                                                                 | Define three granularity levels: term provenance, build provenance, release provenance.                       | Complete PROV profile with SHACL shapes and release provenance examples.                          |
| **Bridge ontology maintenance**                   | Mapper can convert SSSOM to OWL, but bridge ontologies have their own lifecycle and can introduce incoherence. File/section: `ontology-mapper/SKILL.md` §Tool Commands §SSSOM operations.                                                                         | `ontology-mapper`; `ontology-curator`; new `_shared/bridge-ontology-lifecycle.md`                                                                                                | Add bridge lifecycle checklist: generate, reason with both sides, validate, version, publish.                 | Dedicated bridge ontology project layout, tests, release, and mapping refresh workflow.           |
| **Ontology-as-a-service / content negotiation**   | Curator says publish dereferenceable IRIs with content negotiation but does not specify implementation. File/section: `ontology-curator/SKILL.md` §Release Publishing.                                                                                            | `ontology-curator`; `sparql-expert`; new `_shared/publication-content-negotiation.md`                                                                                            | Add PURL/HTTP content negotiation checklist and sample Nginx/Apache/PURL notes.                               | Full deployment guide with TTL/RDFXML/JSON-LD negotiation, docs, SPARQL endpoint, and monitoring. |
| **Schema.org JSON-LD export for discoverability** | Schema.org is a shared vocabulary for structured data on web pages and supports JSON-LD; it is used by major search/application ecosystems. ([Schema.org][12])                                                                                                    | `ontology-architect` §JSON-LD conversion; `ontology-curator` §Release Publishing; new `_shared/jsonld-schema-export.md`                                                          | Add JSON-LD context and schema.org export note for ontology landing pages.                                    | Automated landing-page structured data generation and validation.                                 |
| **OBO Dashboard profile alignment**               | OBO principles are normative for OBO Foundry review and are recommended as generally good practice. ([obofoundry.org][13])                                                                                                                                        | `ontology-validator`; `ontology-curator`; new `_shared/obo-dashboard-profile.md`                                                                                                 | Map existing quality checklist to OBO principles.                                                             | Automated local dashboard mimic with rule IDs and thresholds.                                     |
| **Term request / issue lifecycle**                | Professional maintenance includes term requests, triage, labels, reviewer assignment, and communication.                                                                                                                                                          | `ontology-curator`; `ontology-requirements`; new `_shared/term-request-workflow.md`                                                                                              | Add GitHub issue template and triage statuses.                                                                | Full term request pipeline integrated with KGCL and release notes.                                |
| **Golden ABox fixtures**                          | CQ tests need data fixtures; otherwise tests become syntax checks or stale expectations.                                                                                                                                                                          | `ontology-requirements`; `ontology-validator`; new `_shared/cq-fixture-patterns.md`                                                                                              | Require `tests/fixtures/` for CQs with expected bindings.                                                     | Fixture generator, manifest, and coverage scoring.                                                |
| **Consumer-facing documentation and diagrams**    | Domain experts cannot review raw OWL. File/section: `docs/practitioner-insights.md` §Theme 17.                                                                                                                                                                    | all producer skills; new `_shared/review-artifacts.md`                                                                                                                           | Require human review tables for glossary, model, mappings, and release changes.                               | Mermaid/tree diagrams, generated docs, and reviewer sign-off workflow.                            |

---

### 4. Agent-specific failure modes

#### 4.1 Add explicit “LLM verification required” markers

The skill files should use a standard inline gate:

```markdown
**LLM Verification Required**

- Generated artifact: {artifact}
- Failure risk: {syntax hallucination | false BFO alignment | invalid mapping | stale CQ | etc.}
- Mandatory tool check: `{command}`
- Accept only if: {machine-verifiable condition}
- If failed: loop back to {skill} with {artifact}
```

This should be added to `SKILL-TEMPLATE.md` and then used in each skill where an LLM produces ontology content. File/section: `.claude/skills/SKILL-TEMPLATE.md` §Core Workflow; `.claude/skills/CONVENTIONS.md` §Skill Authoring Standard.

Do not rely on frontmatter for this. Anthropic’s frontmatter requirements center on `name` and `description`; the verification marker belongs in the skill body and can be made machine-searchable by exact heading text. ([Claude][1])

#### 4.2 Required verification by skill

| Skill                     | Steps needing explicit marker                                      | Required tool/check before acceptance                                                                               |
| ------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `ontology-requirements`   | CQ-to-SPARQL generation; sample answers; traceability matrix       | `prepareQuery` parse; run against fixture when available; manifest consistency check                                |
| `ontology-scout`          | reuse recommendation; import term list; ODP recommendation         | `runoak info` term existence; license metadata check; `robot extract`; `robot validate`; candidate CQ probes        |
| `ontology-conceptualizer` | BFO alignment; definitions; axiom plan; property design            | anti-pattern review; BFO ambiguity status; domain/range decision record; user/expert gate for ambiguous categories  |
| `ontology-architect`      | every generated OWL axiom, ROBOT template, KGCL patch, SHACL shape | ROBOT template preflight; `robot validate-profile`; `robot reason` with correct reasoner; `robot report`; `pyshacl` |
| `ontology-mapper`         | LLM mapping predicates and confidence; bridge ontology conversion  | `sssom validate`; entity existence check; exactMatch clique check; optional OAEI precision/recall/F1                |
| `ontology-validator`      | natural-language root-cause interpretation                         | attach raw logs and result files; do not claim pass without tool output                                             |
| `ontology-curator`        | KGCL change plan; deprecation; release notes; import refresh       | KGCL dry-run/apply log; `robot diff`; reason/report; obsolete-term and replacement check                            |
| `sparql-expert`           | SPARQL generation and optimization                                 | parse query; run on fixture or target graph; record entailment regime and expected-result semantics                 |

#### 4.3 Tool invocation should be mandatory, not implicit

The following checks should be hard gates in skills and `CONVENTIONS.md`:

- **Structural OWL changes:** `robot validate-profile` and `robot reason` before handoff; use HermiT/Pellet/Openllet for non-EL features before release. File/section: `ontology-architect/SKILL.md` §Step 7 Verify. OWL 2 profiles are syntactic subsets that trade expressivity for reasoning efficiency, so unsupported constructs must be detected rather than assumed. ([W3C][2])
- **ROBOT templates:** preflight header parsing, CURIE resolution, and required-cell completeness before `robot template`. ROBOT template syntax uses class template strings such as `SC %` and `%` substitution, and supports `SPLIT=|` for multi-value cells; those are exactly where silent mistakes occur. ([GitHub][14])
- **SHACL:** `pyshacl` or equivalent after shape generation, and after reasoning if the validation target is the reasoned graph. File/section: `ontology-validator/SKILL.md` §Step 3 SHACL Validation.
- **SPARQL:** syntax parse before execution and actual execution for reusable CQ/anti-pattern queries. File/section: `sparql-expert/SKILL.md` §Step 4 Validate Syntax.
- **SSSOM:** `sssom validate`, entity existence, duplicate/self mapping check, predicate conflict check, exactMatch clique check. File/section: `ontology-mapper/SKILL.md` §Step 5 Validate and §Step 5.5 Clique Analysis.
- **Import refresh:** term existence, obsolete replacement, module re-extraction, reasoner check over imports closure, mapping refresh handoff. File/section: `ontology-curator/SKILL.md` §Tool Commands §Import refresh.

#### 4.4 Recovery workflow for “confident but wrong” axioms

When an LLM emits an axiom with high confidence and the toolchain rejects it, the suite should require this recovery flow:

1. **Quarantine the change.** Move the generated template/KGCL/patch to `work/failed/{date}-{id}/` and restore the last checkpoint. File/section: `CONVENTIONS.md` §Safety Rules #10.
2. **Capture the failure artifact.** Save reasoner output, profile report, ROBOT report, SHACL results, or SPARQL error.
3. **Classify the failure.** Syntax, profile, inconsistency, unsatisfiable class, missing declaration, import closure, domain/range cascade, mapping-induced incoherence, or CQ failure.
4. **Identify owner skill.** Syntax/profile → architect; semantic mismatch → conceptualizer; stale CQ → requirements; mapping incoherence → mapper; import issue → scout/curator.
5. **Apply least-commitment repair.** Downgrade premature `EquivalentClass` to `SubClassOf`, remove/soften closure, broaden domain/range, replace `exactMatch` with `closeMatch`, or add missing declarations.
6. **Rerun full gate.** The fix is not complete until the same failed check passes and downstream checks are rerun.
7. **Record a failure ledger entry.** `docs/llm-failure-ledger.md` should capture generated text, failed check, root cause, correction, and prevention rule.

---

### 5. Architectural coherence

#### 5.1 Keep 8 top-level skills, but refactor inside them

Eight is the right number for **process skills**. Splitting `ontology-architect` into top-level ROBOT-template, KGCL, OWL-axiom, and reasoning skills would create routing ambiguity and force users to know implementation internals. Architect should remain the formalization owner, but its dense implementation material should move into shared references.

`ontology-validator` and `sparql-expert` should remain cross-cutting. They are not lifecycle phases only; they are verification utilities used by requirements, scout, conceptualizer, architect, mapper, and curator.

#### 5.2 Add named workflows, not necessarily new skills

The pipeline set should expand beyond A/B/C as named workflows in `_shared/methodology-backbone.md` or a new `_shared/workflow-pipelines.md`:

1. **New ontology:** requirements → scout → conceptualizer → architect → validator.
2. **Audit existing ontology:** validator → conceptualizer → architect/curator fixes → validator.
3. **Add N classes:** requirements delta → scout → conceptualizer delta → architect → validator.
4. **Refresh imports:** curator → scout → architect → mapper → validator.
5. **Mapping maintenance:** curator/scout → mapper → validator.
6. **Bridge ontology publication:** mapper → architect → validator → curator.
7. **Release:** validator → curator → validator smoke check.
8. **CQ refresh:** requirements → sparql-expert → validator → conceptualizer/architect if gaps found.

#### 5.3 Shared reference set is good but incomplete

The current shared set is strong: methodology, tool decision tree, BFO, axiom patterns, anti-patterns, naming, quality, namespaces. File/section: bundle §3.5 Shared Reference Materials.

Missing shared references should be added:

- `_shared/llm-verification-patterns.md`
- `_shared/iteration-loopbacks.md`
- `_shared/reasoner-strategy.md`
- `_shared/robot-template-preflight.md`
- `_shared/shacl-patterns.md`
- `_shared/odk-integration.md`
- `_shared/imports-management.md`
- `_shared/imports-manifest.md`
- `_shared/dosdp-patterns.md`
- `_shared/mapping-evaluation.md`
- `_shared/bridge-ontology-lifecycle.md`
- `_shared/provenance-patterns.md`
- `_shared/publication-content-negotiation.md`
- `_shared/jsonld-schema-export.md`
- `_shared/github-actions-template.md`
- `worked-examples/music-ensemble/`

ODK deserves a shared reference because the ODK is explicitly a toolbox of ontology tools bundled in Docker plus executable workflows for CI, QC, releases, and dynamic imports; the current architect has only an awareness box, not a workflow integration. ([Inca Tools][15])

---

## Part II — Recommendations

### A. Per-skill redlines

#### A.1 `ontology-requirements`

**Proposed description field**

```yaml
description: >
  Elicits ontology requirements and competency questions (CQs), writes ORSD
  scope/use-case artifacts, converts stakeholder questions into validated
  SPARQL acceptance tests, and maintains traceability. Use when starting an
  ontology, defining in/out scope, creating or refreshing CQs, generating
  cq-*.sparql tests, building a traceability matrix, or preventing retroactive
  requirements after modeling has begun.
```

**Rationale.** Adds natural routing triggers: stakeholder questions, scope, SPARQL tests, traceability, refreshing stale CQs.

**Activation triggers**

- “Start a new ontology,” “define requirements,” “write ORSD,” “scope this ontology.”
- “Generate competency questions,” “turn these use cases into CQs.”
- “Convert CQs to SPARQL tests,” “create acceptance criteria.”
- “Audit stale CQs,” “update CQ tests after ontology changes.”
- “Build traceability matrix.”

**Structural workflow changes**

- Add **Step 0: Requirements gate detection**. If modeling has already started, require `requirements-retrofit-note.md`.
- Add **Step 2.5: CQ quality scoring** with pass/fail criteria: atomic, answerable, falsifiable, scoped, priority assigned, sample answer present.
- Add **Step 7.5: SPARQL validation and fixture execution**. Call `sparql-expert`; parse every query; run against fixture when present.
- Add **Step 9: Requirements approval artifact**. Produce `docs/requirements-approval.yaml`.

**New shared-reference dependencies**

- `_shared/llm-verification-patterns.md`
- `_shared/cq-fixture-patterns.md`
- `_shared/iteration-loopbacks.md`
- `_shared/review-artifacts.md`

**Worked examples to add**

- `music-ensemble-cq-to-sparql.md`: shows five CQs, expected results, fixture data, and manifest entries.
- `bad-cq-retrofit.md`: “What instruments exist?” vs “Which string instruments require a bow?” and why the latter can fail.

**Handoff-checklist changes**

Add:

- [ ] `requirements-approval.yaml` exists or retroactive requirements are explicitly flagged.
- [ ] Every Must CQ has a parsed SPARQL query.
- [ ] Every CQ declares target entailment regime: asserted-only, RDFS, OWL-reasoned, or endpoint-specific.
- [ ] Every test has an expected-result assertion and, where feasible, fixture data.
- [ ] `traceability-matrix.csv` includes stakeholder need → use case → CQ → term placeholder → test.

**Anti-patterns to add/remove**

Add:

- **CQ without falsifiability:** A CQ that cannot produce an empty/false/failing result is not an acceptance test.
- **Fixture-free CQ suite:** Queries that parse but never run against any representative graph are incomplete.
- **Retrofit without impact review:** If CQs are added after modeling, require conceptualizer review.

Remove none.

---

#### A.2 `ontology-scout`

**Proposed description field**

```yaml
description: >
  Finds, evaluates, and imports reusable ontology resources before new term
  creation. Searches OBO/OLS/BioPortal/LOV/schema.org and domain registries,
  checks term existence, licenses, maintenance, BFO/RO fit, import strategy
  (MIREOT/STAR/BOT/ODK), and recommends ODP/DOSDP patterns or mappings. Use
  for reuse scouting, import planning, upstream term checks, ODP selection,
  and import-refresh triage.
```

**Activation triggers**

- “Does this term already exist?”
- “Should we reuse/import OEO, GO, QUDT, BFO, RO, schema.org?”
- “Create import term list,” “MIREOT,” “extract module,” “refresh import.”
- “Find ontology design pattern,” “ODP,” “DOSDP pattern.”
- “Evaluate candidate ontology quality/license.”

**Structural workflow changes**

- Add **Step 0: Tool/source availability check**. If registries fail, use local cache and document source freshness.
- Split Step 2 into **coverage**, **quality**, **license**, **maintenance**, **BFO/RO fit**, and **import risk**.
- Replace Step 5 ODP Search with **ODP/DOSDP selection**: source, pattern name, applicability, variables, example instantiation, downstream axiom pattern.
- Add **Step 6: Import manifest update** using `imports-manifest.yaml`.

**New shared-reference dependencies**

- `_shared/imports-management.md`
- `_shared/imports-manifest.md`
- `_shared/dosdp-patterns.md`
- `_shared/odk-integration.md`
- `_shared/modularization-patterns.md`

**Worked examples to add**

- `energy-technology-import-choice.md`: OEO term list, MIREOT vs STAR trade-off, stale term check.
- `music-instrument-reuse-scout.md`: reuse BFO/RO/IAO/SKOS/PROV; reject a weak music vocabulary due to license/maintenance.

**Handoff-checklist changes**

Add:

- [ ] Every searched registry/source is listed with date and access status.
- [ ] Every recommended external term has IRI, label, source ontology version, and license.
- [ ] `imports-manifest.yaml` updated with source, version, extraction method, term file, and refresh policy.
- [ ] ODP/DOSDP recommendations include actual pattern templates or references.
- [ ] Candidate CQ benchmark probe results recorded.

**Anti-patterns to add/remove**

Add:

- **Unversioned import recommendation:** Reuse without source version pinning is incomplete.
- **ODP name-dropping:** Listing a pattern without an instantiation template is not a recommendation.
- **Registry-only trust:** Registry hit does not imply logical/metadata quality.

Remove none.

---

#### A.3 `ontology-conceptualizer`

**Proposed description field**

```yaml
description: >
  Transforms approved CQs and reuse findings into a BFO-aligned conceptual
  model: glossary, taxonomy, module/layer design, property design, BFO
  category decisions, SHACL-vs-OWL intent, axiom plan, and anti-pattern review.
  Use before OWL formalization, when designing class hierarchies/properties,
  resolving BFO ambiguities, choosing domain/range vs SHACL, or selecting
  axiom patterns from CQs.
```

**Activation triggers**

- “Design taxonomy,” “conceptual model,” “class hierarchy,” “property model.”
- “Align to BFO,” “role or disposition,” “object or aggregate,” “process or object.”
- “Create axiom plan,” “select OWL patterns,” “closure axiom,” “value partition.”
- “Should this be domain/range, restriction, or SHACL?”
- “Review modeling anti-patterns.”

**Structural workflow changes**

- Add **Step 0: Verify inbound gate**: requirements approval, reuse report, CQ priorities.
- Add **Step 3.1: BFO ambiguity register** with status and reviewer requirement.
- Add **Step 4.1: OWL-vs-SHACL intent** for each property/cardinality.
- Add **Step 5.1: Profile/reasoner implication of axiom plan**.
- Add **Step 6.1: Anti-pattern review artifact**: `docs/anti-pattern-review.md`.
- Add **Step 7: Domain expert review package**: tables/diagrams, not just YAML.

**New shared-reference dependencies**

- `_shared/llm-verification-patterns.md`
- `_shared/reasoner-strategy.md`
- `_shared/shacl-patterns.md`
- `_shared/review-artifacts.md`
- `_shared/modularization-patterns.md`

**Worked examples to add**

- `orchestra-object-vs-object-aggregate.md`
- `musical-score-gdc-concretization.md`
- `student-role-not-person-subclass.md`
- `domain-range-cascade-prescribes-example.md`
- `closure-axiom-vegetarian-pizza-style-music-example.md`

**Handoff-checklist changes**

Add:

- [ ] `bfo-alignment.md` includes ambiguity status for every top-level class.
- [ ] `property-design.yaml` declares intent: infer, validate, restrict, or annotate.
- [ ] `axiom-plan.yaml` includes expected OWL profile and reasoner gate for each non-EL pattern.
- [ ] `anti-pattern-review.md` lists each anti-pattern, detection mode, result, and resolution.
- [ ] `conceptual-model-review.md` or `approval-record.yaml` exists.

**Anti-patterns to add/remove**

Add:

- **Unreviewed BFO ambiguity:** Ambiguous alignment without reviewer decision cannot pass handoff.
- **Axiom-plan/profile mismatch:** Selecting qualified cardinality while expecting ELK-only validation is a planning error.
- **Layer without boundary:** Assigning modules to layers without import/dependency implications is decorative.

Remove none.

---

#### A.4 `ontology-architect`

**Proposed description field**

```yaml
description: >
  Formalizes an approved conceptual model as programmatic OWL/SHACL artifacts
  using ROBOT templates, KGCL, DOSDP/ODK workflows, rdflib or OWL API escape
  hatches, and reasoner/profile gates. Use when adding or modifying classes,
  properties, axioms, SHACL shapes, ROBOT templates, KGCL patches, import
  declarations, or when debugging OWL profile, reasoner, or formalization
  failures.
```

**Activation triggers**

- “Add class/property/axiom,” “formalize model,” “implement axiom plan.”
- “Generate ROBOT template,” “KGCL patch,” “DOSDP,” “ODK edit file.”
- “Create SHACL shape,” “domain/range implementation,” “property chain.”
- “Fix unsatisfiable class,” “reasoner failed,” “validate OWL profile.”
- “Qualified cardinality,” “EquivalentClass,” “DisjointUnion,” “role chain.”

**Structural workflow changes**

- Move ODK awareness from Tool Commands into **Step 0: Determine project build regime**: standalone POD vs ODK-managed.
- Add **Step 2.5: Import/declaration preflight**.
- Replace Step 3 with **Bulk term creation via ROBOT or DOSDP**.
- Add **Step 3.5: ROBOT template preflight** before execution.
- Expand SHACL into **Step 6.5: Generate SHACL shapes from property-design intent**.
- Add **Step 7.1: Profile-specific reasoner gate**.
- Add **Step 8: Handoff packaging** with raw logs and generated artifact list.

**New shared-reference dependencies**

- `_shared/odk-integration.md`
- `_shared/dosdp-patterns.md`
- `_shared/robot-template-preflight.md`
- `_shared/shacl-patterns.md`
- `_shared/reasoner-strategy.md`
- `_shared/imports-management.md`
- `_shared/llm-verification-patterns.md`

**Worked examples to add**

- `StringQuartet-qualified-cardinality-ELK-silent-ignore-HermiT-fix.md`
- `ROBOT-template-empty-cell-partial-term.md`
- `domain-range-vs-shacl-prescribes.md`
- `property-chain-hasSeries-implementsVariable-hasVariable.md`
- `DOSDP-instrument-family-pattern.md`

**Handoff-checklist changes**

Add:

- [ ] Project build regime recorded: standalone POD or ODK.
- [ ] ROBOT/DOSDP templates pass preflight before execution.
- [ ] `robot validate-profile` output attached.
- [ ] Reasoner choice matches axiom expressivity; HermiT/Pellet/Openllet used for DL features before release.
- [ ] SHACL shapes generated for all validation-intent constraints.
- [ ] `cq-implementation-matrix.csv` maps Must CQs to implemented axioms/tests.

**Anti-patterns to add/remove**

Add:

- **ELK-only validation of DL axioms:** Any qualified cardinality, complement, or universal-heavy modeling requires full-DL release gate.
- **SHACL as afterthought:** If conceptualizer marked validation intent, architect must generate shapes.
- **Template without preflight:** Running `robot template` without header/CURIE/required-cell checks is a safety violation.

Remove or soften:

- Replace “NEVER hand-edit ontology files” with “Never hand-edit structural axioms; annotation-only edits require validation,” matching the already-refined convention.

---

#### A.5 `ontology-mapper`

**Proposed description field**

```yaml
description: >
  Generates, verifies, evaluates, and maintains cross-ontology mappings and
  bridge ontologies using SSSOM, oaklib lexmatch, LLM-assisted semantic review,
  OAEI-style precision/recall/F1 metrics, exactMatch clique checks, identity
  risk controls, and version-refresh workflows. Use for alignment, xrefs,
  mapping QA, validating mappings, remapping obsolete terms, publishing bridge
  ontologies, or reviewing exactMatch/sameAs safety.
```

**Activation triggers**

- “Map ontology A to B,” “alignment,” “xref,” “SSSOM.”
- “Validate mapping quality,” “mapping QA,” “precision/recall.”
- “Check exactMatch clique,” “sameAs risk,” “bridge ontology.”
- “Update mappings after upstream release,” “obsolete target term.”
- “Lexical match candidates,” “LLM verify mappings.”

**Structural workflow changes**

- Add **Step 0: Mapping context classification**: same-domain, cross-domain, bridge, identity, lexical synonym, replacement.
- Expand Step 3 into **LLM verification with evidence rubric**.
- Add **Step 5.1: Entity existence and obsolete-term check**.
- Add **Step 5.6: OAEI-style evaluation when gold/dev set exists**.
- Add **Step 7: Mapping maintenance workflow** for source/target version changes.
- Add **Step 8: Bridge ontology safety gate**.

**New shared-reference dependencies**

- `_shared/mapping-evaluation.md`
- `_shared/bridge-ontology-lifecycle.md`
- `_shared/llm-verification-patterns.md`
- `_shared/imports-management.md`
- `_shared/reasoner-strategy.md`

**Worked examples to add**

- `solar-pv-closeMatch-vs-exactMatch.md`
- `exactMatch-clique-contamination.md`
- `obsolete-target-remap-with-replacement.md`
- `sssom-to-bridge-owl-reasoning-failure.md`

**Handoff-checklist changes**

Add:

- [ ] Mapping context type recorded.
- [ ] Entity existence and obsolete-term report generated.
- [ ] exactMatch clique report generated; cliques >3 reviewed.
- [ ] Gold/dev-set metrics reported when available.
- [ ] Bridge ontology, if generated, reasoned with source and target imports.
- [ ] Every LLM-reviewed mapping has evidence: labels, definitions, parents, decision, confidence, justification.

**Anti-patterns to add/remove**

Add:

- **Metric-free mapping QA:** For a maintained mapping set, validation is not enough; evaluate against gold/dev set where possible.
- **Bridge without joint reasoning:** A bridge ontology that has not been reasoned with both source and target is unpublished.
- **Unscoped exactMatch:** exactMatch across domains requires explicit proof or reviewer approval.

Remove none.

---

#### A.6 `ontology-validator`

**Proposed description field**

```yaml
description: >
  Runs ontology and mapping quality gates: OWL reasoning, OWL profile checks,
  ROBOT report, SHACL/pyshacl, CQ acceptance tests, anti-pattern SPARQL,
  SSSOM validation, coverage metrics, diffs, and release/audit reports. Use
  before commits or releases, after structural changes, when auditing an
  existing ontology, validating mappings, debugging reasoner/SHACL/CQ failures,
  or checking CI readiness.
```

**Activation triggers**

- “Validate ontology,” “quality check,” “audit existing ontology.”
- “Run reasoner,” “ROBOT report,” “validate profile,” “SHACL.”
- “Run CQ tests,” “why did CQ fail?”
- “Validate SSSOM mappings.”
- “Prepare release validation report,” “CI check.”

**Structural workflow changes**

- Add **Step 0: Determine artifact type**: ontology, mapping set, bridge ontology, import closure, release artifact.
- Add **Level 0: Syntax/profile/import closure preflight** before reasoning.
- Add **Level 3.5: SHACL shape coverage check**.
- Add **Level 4.5: CQ manifest integrity and stale CQ detection**.
- Add **Level 5.5: Anti-pattern detection pack**.
- Add **Level 8: Loopback routing** with owner skill and required fix artifact.

**New shared-reference dependencies**

- `_shared/reasoner-strategy.md`
- `_shared/shacl-patterns.md`
- `_shared/mapping-evaluation.md`
- `_shared/iteration-loopbacks.md`
- `_shared/github-actions-template.md`
- `_shared/obo-dashboard-profile.md`

**Worked examples to add**

- `CQ-count-query-row-count-bug.md`
- `missing-import-declaration-profile-violations.md`
- `shacl-pass-owl-fail-example.md`
- `robot-report-warning-policy.md`

**Handoff-checklist changes**

Add:

- [ ] Raw logs/results attached for every level.
- [ ] Validation report includes exact commands and tool versions.
- [ ] Failures route to a named upstream skill with required artifact.
- [ ] SHACL missing is a FAIL unless explicitly waived in `validation-waivers.yaml`.
- [ ] Mapping validation includes clique and obsolete-term checks where relevant.
- [ ] Release validation includes diff and publication metadata checks.

**Anti-patterns to add/remove**

Add:

- **Validation by assertion:** Never report PASS unless command output exists.
- **Waiver without owner:** Every waived warning needs owner, rationale, and expiry.
- **Wrong reasoner confidence:** ELK pass is not DL pass when non-EL axioms exist.

Remove or revise:

- Revise “Create minimal shapes or defer SHACL check” to “loop back to architect unless temporary validator-generated shapes are explicitly marked provisional.”

---

#### A.7 `ontology-curator`

**Proposed description field**

```yaml
description: >
  Maintains existing ontologies through KGCL change proposals, deprecation/
  obsoletion, import refresh, versioning, release preparation, FAIR/OBO
  publication checks, bridge/mapping maintenance handoffs, changelogs, and
  consumer-facing release notes. Use for renames, reparenting, deprecations,
  upstream ontology changes, refresh-imports, release artifacts, PURLs,
  content negotiation, or communicating ontology changes.
```

**Activation triggers**

- “Deprecate/obsolete term,” “rename,” “reparent,” “change definition.”
- “Release ontology,” “version bump,” “prepare release,” “changelog.”
- “Refresh imports,” “upstream ontology changed,” “stale term.”
- “Update mappings after import refresh.”
- “Publish ontology,” “PURL,” “content negotiation,” “FAIR check.”
- “Consumer-facing release notes.”

**Structural workflow changes**

- Add **Step 0: Change intake and impact scope**: annotation, structural, semantic, mapping, import, release.
- Add **Step 1.5: CQ and mapping impact analysis**.
- Add **Step 3.5: Approval artifact** before applying patch.
- Add **Step 5.6: OBO/PURL publication metadata check**.
- Add **Step 6.5: Consumer release notes**.
- Expand import refresh into a first-class workflow routing to scout/mapper/validator.

**New shared-reference dependencies**

- `_shared/imports-management.md`
- `_shared/imports-manifest.md`
- `_shared/odk-integration.md`
- `_shared/publication-content-negotiation.md`
- `_shared/jsonld-schema-export.md`
- `_shared/fair-release.md`
- `_shared/bridge-ontology-lifecycle.md`
- `_shared/iteration-loopbacks.md`

**Worked examples to add**

- `deprecate-term-with-replacement-and-cq-impact.md`
- `refresh-imports-obsolete-term-remap.md`
- `date-versioned-obo-release.md`
- `consumer-release-notes-for-renames.md`

**Handoff-checklist changes**

Add:

- [ ] `change-impact.md` covers affected CQs, mappings, imports, and consumers.
- [ ] `change-approval.yaml` records reviewer approval or waiver.
- [ ] Import refresh updates `imports-manifest.yaml`.
- [ ] Mapping refresh handoff created when source/target terms changed.
- [ ] Release notes include breaking changes, deprecations, replacements, and migration guidance.
- [ ] Publication metadata and content-negotiation checks completed.

**Anti-patterns to add/remove**

Add:

- **Import refresh without mapping refresh:** If imported terms changed, mapper must revalidate mappings.
- **Release without migration guidance:** Deprecations and semantic changes require consumer-facing notes.
- **Unrecorded approval:** A reviewed KGCL patch needs an approval artifact, not just chat context.

Remove none.

---

#### A.8 `sparql-expert`

**Proposed description field**

```yaml
description: >
  Designs, validates, runs, and debugs SPARQL 1.1/SPARQL-star queries for
  ontology engineering: CQ tests, anti-pattern checks, coverage metrics,
  mapping clique analysis, import diagnostics, ROBOT query, rdflib, and
  endpoint queries across GraphDB, Stardog, Fuseki, and local files. Use when
  writing SPARQL, converting CQs to queries, validating query syntax,
  specifying expected results, checking entailment regimes, optimizing
  property paths, or debugging empty/slow query results.
```

**Activation triggers**

- “Write SPARQL,” “debug query,” “query returns empty,” “optimize query.”
- “Convert this CQ to SPARQL.”
- “Create anti-pattern detection query.”
- “Coverage metric query,” “orphan class query,” “missing definition query.”
- “Mapping clique check.”
- “ROBOT query,” “rdflib query,” “GraphDB/Stardog/Fuseki endpoint.”

**Structural workflow changes**

- Add **Step 0: Determine ontology-engineering query purpose**: CQ, anti-pattern, metric, mapping, import, exploratory.
- Add **Step 2.5: Entailment regime selection** before query drafting.
- Add **Step 4.5: Expected-result contract** for CQ/validation queries.
- Add **Step 5.5: Result sanity check**: row count vs aggregate result semantics.
- Add endpoint authentication and named-graph discovery guidance.

**New shared-reference dependencies**

- `_shared/cq-fixture-patterns.md`
- `_shared/anti-pattern-query-library.md`
- `_shared/mapping-evaluation.md`
- `_shared/namespaces.json`

**Worked examples to add**

- `CQ-aggregate-count-vs-row-count.md`
- `exactMatch-clique-property-path.md`
- `orphan-class-query-with-blank-node-filter.md`
- `asserted-vs-reasoned-query-results.md`

**Handoff-checklist changes**

Add:

- [ ] Query purpose declared.
- [ ] Target graph/source and entailment regime declared.
- [ ] Syntax parsed successfully.
- [ ] Expected-result contract specified where query is a test.
- [ ] Query executed against fixture or target graph unless exploratory only.
- [ ] Result sanity check performed for aggregates and property paths.

**Anti-patterns to add/remove**

Add:

- **Aggregate row-count mismatch:** A `COUNT` query usually returns one row; do not use it when manifest expects N result rows.
- **Entailment-implicit CQ:** A CQ that requires inferred triples must say so.
- **Unanchored property path:** Transitive property paths need anchors and limits for diagnostics.

Remove none.

---

### B. Shared-material changes

#### Existing shared files

##### `_shared/methodology-backbone.md`

**Keep:** lifecycle map, pipelines, CQ through-line, phase boundaries.

**Expand:** add loopback protocols, named workflows beyond A/B/C, and progress criteria per phase.

**Extract:** move pipelines and loopbacks into `_shared/workflow-pipelines.md` if the file grows beyond easy navigation.

##### `_shared/tool-decision-tree.md`

**Keep:** tool priority and known limitations.

**Expand:** add ODK/DOSDP, ROBOT template preflight, mandatory tool gates, and tool availability checks.

**Extract:** reasoner guidance into `_shared/reasoner-strategy.md`; ROBOT template preflight into `_shared/robot-template-preflight.md`; ODK into `_shared/odk-integration.md`.

##### `_shared/bfo-categories.md`

**Keep:** decision tree, common mistakes, relations, temporal indexing, GDC pattern, known ambiguities.

**Expand:** add worked ambiguity examples with reviewer decisions and uncertainty codes.

**Extract:** move examples into `worked-examples/bfo-alignment/` if they become lengthy.

##### `_shared/axiom-patterns.md`

**Keep:** the 16-pattern catalog and selection guide.

**Expand:** add profile compatibility, reasoner requirements, SHACL counterpart, closure discipline, and DOSDP equivalents.

**Extract:** DOSDP into `_shared/dosdp-patterns.md`; profile/reasoner compatibility into `_shared/reasoner-strategy.md`.

##### `_shared/anti-patterns.md`

**Keep:** the 16 anti-patterns.

**Expand:** add severity, detection mode, false-positive notes, and responsible skill for remediation.

**Extract:** SPARQL files into `sparql/anti-patterns/` plus `_shared/anti-pattern-query-library.md`.

##### `_shared/naming-conventions.md`

**Keep:** class/property/individual naming, ID minting, IRI governance, labels, synonyms, genus-differentia definitions.

**Expand:** add OBO metadata profile, annotation-language tags, definition-source policy, context-specific synonyms, and schema.org/JSON-LD label export notes.

**Extract:** publication metadata into `_shared/metadata-profile.md` if it grows.

##### `_shared/quality-checklist.md`

**Keep:** OWL, ROBOT, SHACL, CQ, coverage, succinctness, and evaluation dimensions.

**Expand:** add result artifact requirements, validation waivers, CI/CD mapping, SSSOM clique checks, import freshness checks, and release gates.

**Extract:** CI into `_shared/github-actions-template.md`; SHACL into `_shared/shacl-patterns.md`; mapping QA into `_shared/mapping-evaluation.md`.

##### `_shared/namespaces.json`

**Keep:** canonical prefix map.

**Expand:** add optional project-level prefix overlay convention, not hard-coded project prefixes.

**Extract:** none.

#### New shared-reference files

##### `_shared/llm-verification-patterns.md`

Defines where LLM output is allowed, where it is risky, required verification gates, recovery workflow, and the standard “LLM Verification Required” block. Referenced by all eight skills.

##### `_shared/iteration-loopbacks.md`

Defines downstream rejection, loopback triggers, owner skill, required failure artifact, retry criteria, and waiver handling. Referenced by all lifecycle skills and `CONVENTIONS.md`.

##### `_shared/reasoner-strategy.md`

Unifies OWL profile selection, ELK/HermiT/Pellet/Openllet use, profile validation, materialization decisions, time budgets, and non-EL feature detection. Referenced by conceptualizer, architect, validator, mapper, curator.

##### `_shared/robot-template-preflight.md`

Provides header syntax checks, CURIE resolution, required-cell checks, multi-value `SPLIT`, language tags, merge/replace safety, and a preflight script outline. Referenced by architect and validator. ROBOT’s official template syntax around `%` substitution and `SPLIT=|` should be cited in this file. ([GitHub][14])

##### `_shared/shacl-patterns.md`

Provides SHACL templates for required labels, recommended definitions, datatype constraints, class constraints, cardinality, scheme membership, no-orphan checks, and SHACL-SPARQL examples. Referenced by conceptualizer, architect, validator, sparql-expert. SHACL’s data graph / shapes graph model should be cited. ([W3C][4])

##### `_shared/odk-integration.md`

Defines standalone POD vs ODK-managed project behavior, edit-release split, `run.sh make`, dynamic imports, `prepare_release`, DOSDP, and ODK CI. Referenced by scout, architect, validator, curator. ([Inca Tools][15])

##### `_shared/imports-management.md`

Defines import selection, term files, MIREOT/STAR/BOT/TOP trade-offs, version pinning, stale term detection, circular imports, import closure validation, and refresh workflow. Referenced by scout, architect, validator, curator, mapper.

##### `_shared/imports-manifest.md`

Specifies `imports-manifest.yaml`: source ontology, version IRI, retrieval URL, extraction method, term file, module file, refresh cadence, last refresh, and known obsolete mappings. Referenced by scout and curator.

##### `_shared/dosdp-patterns.md`

Introduces DOSDP pattern files, TSV fillers, validation, documentation, and when to prefer DOSDP over raw ROBOT templates. Referenced by scout and architect. ([Springer][9])

##### `_shared/mapping-evaluation.md`

Defines mapping QA: SSSOM validation, entity existence, predicate conflicts, exactMatch cliques, OAEI-style metrics, gold/dev sets, and human review queues. Referenced by mapper and validator. ([CEUR-WS][10])

##### `_shared/bridge-ontology-lifecycle.md`

Defines bridge ontology generation, review, reasoning with source/target imports, release, versioning, and refresh after upstream changes. Referenced by mapper, architect, validator, curator.

##### `_shared/provenance-patterns.md`

Defines term, axiom, mapping, import, build, release, and dataset provenance using PROV-O at realistic granularity. Referenced by scout, architect, mapper, curator. ([W3C][11])

##### `_shared/publication-content-negotiation.md`

Defines dereferenceable IRI, PURL, content negotiation, release artifact formats, landing pages, and endpoint publication. Referenced by curator and sparql-expert.

##### `_shared/jsonld-schema-export.md`

Defines JSON-LD context strategy, schema.org landing-page metadata, SEO/discoverability export, and validation. Referenced by architect and curator. ([Schema.org][12])

##### `_shared/github-actions-template.md`

Provides GitHub Actions examples for standalone POD and ODK-managed projects: lint, build, reason, report, SHACL, CQ tests, SSSOM validation, release artifacts. Referenced by validator and curator.

##### `worked-examples/`

A worked-example library with domain-specific walkthroughs and expected outputs. Referenced by every skill.

---

### C. Governance changes

#### C.1 `CONVENTIONS.md`: safety rules

Keep the current ten safety rules, but revise and add rules.

**Revise Rule 2.**

Current: “Always run the reasoner after any structural change.”

Proposed:

> Always run an appropriate reasoner before handoff, commit, or release after structural changes. Use ELK for fast EL-profile development checks; use HermiT/Pellet/Openllet before release or whenever non-EL constructs are present. Record the reasoner and profile assumptions in the validation report.

**Add Rule 11.**

> LLM-generated OWL axioms, SHACL shapes, ROBOT templates, KGCL patches, SPARQL tests, and SSSOM mappings must pass their required tool gates before handoff. No generated artifact is accepted on LLM confidence alone.

**Add Rule 12.**

> Cross-ontology `skos:exactMatch`, `owl:equivalentClass`, and `owl:sameAs` mappings must pass clique/identity-risk checks before merge or bridge publication.

**Add Rule 13.**

> CQ SPARQL tests must parse successfully and declare expected-result semantics before requirements handoff. Must-Have CQs should run against a fixture or representative graph where feasible.

**Add Rule 14.**

> Import term lists must be validated against the pinned upstream ontology version before import refresh or release.

**Add Rule 15.**

> Human approval gates must be recorded in repository artifacts, not only in chat context.

**Tighten Rule 5.**

KGCL patches should be proposed before applying to shared ontologies, but for private/local ontologies the skill may apply after creating a checkpoint and recording the change log. The current wording is right for shared ontologies but ambiguous for local work.

**Loosen only where already justified.**

The hand-edit exception for annotation-only changes is correct. Do not loosen structural-edit rules.

#### C.2 Add “Iteration and loopback” section

Add to `CONVENTIONS.md` after Cross-Skill Handoff Specification:

```markdown
## Iteration and Loopback Protocol

Downstream skills may reject an inbound handoff when required artifacts are
missing, tool gates fail, or semantic ambiguity blocks safe continuation.

Every rejection MUST produce a loopback record:

| Field           | Meaning                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------- |
| rejecting_skill | Skill that found the issue                                                                            |
| source_skill    | Skill responsible for the fix                                                                         |
| artifact        | File/path that failed                                                                                 |
| failure_type    | missing_artifact, syntax, profile, reasoner, shacl, cq, mapping, import, approval, semantic_ambiguity |
| evidence        | Command output, report path, or quoted section                                                        |
| required_fix    | Concrete action required                                                                              |
| retry_gate      | Command/check that must pass before returning                                                         |

Default routing:

- Missing/invalid CQs -> ontology-requirements
- Reuse/import gaps -> ontology-scout
- BFO/category/property design ambiguity -> ontology-conceptualizer
- OWL/SHACL/template/KGCL formalization failure -> ontology-architect
- Mapping/bridge failure -> ontology-mapper
- Release/import-refresh/deprecation issue -> ontology-curator
- SPARQL syntax/query semantics -> sparql-expert
```

#### C.3 Add required authoring sections

Update `CONVENTIONS.md` §Skill Authoring Standard to require:

1. YAML Front Matter
2. Role Statement
3. When to Activate
4. Shared Reference Materials
5. Core Workflow
6. **Progress Criteria**
7. **LLM Verification Required**
8. Tool Commands
9. Outputs
10. Handoff
11. **Loopback Triggers**
12. Anti-Patterns to Avoid
13. Error Handling
14. **Worked Examples**

This directly matches Anthropic guidance that complex workflows should have clear sequential steps, validation loops, concrete examples, and feedback mechanisms. ([Claude][1])

#### C.4 Updated `SKILL-TEMPLATE.md` boilerplate

````markdown
---
name: { skill-name }
description: >
  {Third-person description. Include what the skill does AND when to use it.
  Include concrete trigger phrases users will say. Maximum 1024 characters.}
---

# {Skill Title}

## Role Statement

{Responsibilities, non-responsibilities, and phase ownership.}

## When to Activate

- {Natural-language user trigger}
- {Pipeline/workflow trigger}
- {Artifact or failure trigger}

## Shared Reference Materials

Read these files from `_shared/` before beginning work:

- `_shared/methodology-backbone.md` — lifecycle context
- `_shared/iteration-loopbacks.md` — loopback protocol
- `_shared/llm-verification-patterns.md` — verification gates for LLM output
- `_shared/{relevant}.md` — {why needed}

## Core Workflow

### Step 0: Verify Entry Conditions

Required inbound artifacts:

- `{path}` — {expected format}
- `{path}` — {expected format}

If missing, create a loopback record and stop.

### Step 1: {Step Name}

{Actionable instruction.}

```bash
{command}
```
````

### Step N: {Step Name}

{Actionable instruction.}

## Progress Criteria

Proceed only when:

- [ ] {machine-verifiable criterion}
- [ ] {review/approval artifact exists if required}
- [ ] {all mandatory tool gates pass}

## LLM Verification Required

Use this block for any LLM-generated ontology content:

| Generated artifact | Risk   | Mandatory verification | Accept only if |
| ------------------ | ------ | ---------------------- | -------------- |
| {artifact}         | {risk} | `{command}`            | {condition}    |

If verification fails, follow `_shared/iteration-loopbacks.md`.

## Tool Commands

### {Operation}

```bash
{exact command}
```

## Outputs

| Artifact   | Location | Format   | Description   |
| ---------- | -------- | -------- | ------------- |
| {artifact} | `{path}` | {format} | {description} |

## Handoff

**Receives from**: {previous skill} — {artifacts}

**Passes to**: {next skill} — {artifacts}

**Handoff checklist**:

- [ ] {artifact exists}
- [ ] {tool gate passed}
- [ ] {approval/waiver recorded}

## Loopback Triggers

| Trigger   | Return to | Required artifact |
| --------- | --------- | ----------------- |
| {failure} | {skill}   | {file/report}     |

## Anti-Patterns to Avoid

- **{Anti-pattern}**: {detection and correction}

## Error Handling

| Error   | Likely Cause | Recovery   | Loopback |
| ------- | ------------ | ---------- | -------- |
| {error} | {cause}      | {recovery} | {skill}  |

## Worked Examples

- `worked-examples/{example}.md` — {what it demonstrates}

````

---

### D. New or merged skills

#### D.1 Recommendation: no immediate top-level skill split or merge

Do not split the eight skills now. Keep the current set:

- `ontology-requirements`
- `ontology-scout`
- `ontology-conceptualizer`
- `ontology-architect`
- `ontology-mapper`
- `ontology-validator`
- `sparql-expert`
- `ontology-curator`

**Reason.** These are phase/process boundaries, not just tool boundaries. Splitting `ontology-architect` into ROBOT/KGCL/reasoning skills would improve implementation focus but harm routing and user mental model. A user says “add these classes” or “formalize this model,” not “activate ROBOT-template skill.” The better fix is shared references plus progress gates.

#### D.2 Handoff diff

No artifacts move between top-level skills. Add artifacts to existing handoffs:

- Requirements → Conceptualizer: add `requirements-approval.yaml`, `cq-quality-report.md`.
- Scout → Conceptualizer/Architect/Curator: add `imports-manifest.yaml`.
- Conceptualizer → Architect: add `anti-pattern-review.md`, `conceptual-model-review.md`, `bfo-ambiguity-register.yaml`.
- Architect → Validator: add `profile-report.txt`, `reasoner.log`, `cq-implementation-matrix.csv`, `template-preflight-report.md`.
- Mapper → Validator/Curator: add `clique-report.csv`, `obsolete-term-report.csv`, `mapping-evaluation.md`.
- Curator → Validator/Mapper: add `change-impact.md`, `change-approval.yaml`, `import-refresh-report.md`, `release-notes.md`.

#### D.3 Migration plan

1. Extract ROBOT pitfalls from `ontology-architect/SKILL.md` to `_shared/robot-template-preflight.md`.
2. Extract reasoner strategy from `ontology-architect`, `ontology-validator`, and `tool-decision-tree` into `_shared/reasoner-strategy.md`.
3. Extract ODK awareness from `ontology-architect` into `_shared/odk-integration.md`.
4. Extract import refresh from `ontology-curator` and module extraction from `ontology-scout` into `_shared/imports-management.md`.
5. Extract mapping quality/clique/bridge guidance from `ontology-mapper` into `_shared/mapping-evaluation.md` and `_shared/bridge-ontology-lifecycle.md`.
6. Add new handoff artifacts to skill checklists.
7. Add routing tests to evaluation harness.

#### D.4 Optional future split, not recommended for first implementation wave

If the repo later supports nested implementation skills, add them as **helper skills**, not replacements:

```yaml
---
name: ontology-build-engineer
description: >
  Implements ontology build mechanics for ROBOT templates, DOSDP, ODK make
  targets, import modules, and serialization normalization. Use only when
  ontology-architect or ontology-curator delegates build-pipeline execution.
---
````

```yaml
---
name: ontology-reasoning-debugger
description: >
  Diagnoses OWL profile, reasoner, unsatisfiable-class, and import-closure
  failures using ROBOT, ELK, HermiT, Pellet/Openllet, and explanation logs.
  Use only when ontology-validator or ontology-architect delegates a failed
  reasoning gate.
---
```

Migration would move no lifecycle ownership, only detailed examples and scripts.

---

### E. Worked-example library design

#### E.1 Demo domain

Use a **Music Ensemble Ontology** demo.

Why this domain works:

- Small and intuitive.
- Naturally covers BFO Object, Object Aggregate, Role, Quality, Process, Site, and GDC.
- Supports qualified cardinality with `StringQuartet`.
- Supports property chain with ensemble membership and instrument use.
- Supports disjoint union with instrument families.
- Supports value partition with condition or pitch range.
- Avoids biomedical-specific assumptions while still exercising BFO.

#### E.2 Seed term list

Target ≤30 classes.

**BFO Object / Material Entity**

1. `MusicalInstrument`
2. `StringInstrument`
3. `WindInstrument`
4. `PercussionInstrument`
5. `KeyboardInstrument`
6. `Violin`
7. `Viola`
8. `Cello`
9. `Piano`
10. `Bow`
11. `Person`

**Object Aggregate**

12. `MusicalEnsemble`
13. `StringQuartet`

**Role**

14. `PerformerRole`
15. `ConductorRole`
16. `StudentRole`

**Quality / value partitions**

17. `InstrumentCondition`
18. `GoodCondition`
19. `FairCondition`
20. `PoorCondition`
21. `PitchRange`
22. `HighPitchRange`
23. `MediumPitchRange`
24. `LowPitchRange`

**Process / Site**

25. `MusicalPerformance`
26. `Rehearsal`
27. `ConcertVenueSite`

**GDC / information**

28. `MusicalWork`
29. `MusicalScore`
30. `ScoreEdition`

#### E.3 Five highest-priority CQs

1. **CQ-001:** Which instruments are string instruments, and what instrument family do they belong to?
   Exercises taxonomy, disjoint union, labels.

2. **CQ-002:** Which ensembles qualify as string quartets by having exactly four performer members?
   Exercises qualified cardinality and full-DL reasoner gate.

3. **CQ-003:** Which musical performances realize a musical work and have performers at a venue?
   Exercises n-ary/process modeling and participation.

4. **CQ-004:** Which instruments have poor condition and therefore require maintenance review?
   Exercises value partition and SHACL validation.

5. **CQ-005:** Which instruments does an ensemble use, inferred from its members and the instruments those members play?
   Exercises property chain.

#### E.4 Axiom patterns exercised

- **Simple SubClassOf:** `Violin SubClassOf StringInstrument`.
- **Existential restriction:** `MusicalPerformance SubClassOf hasParticipant some Person`.
- **Closure axiom:** `StringQuartet SubClassOf hasMember only Musician`.
- **Equivalent class:** `StringInstrument EquivalentTo MusicalInstrument and hasPart some String`.
- **Disjoint classes:** string/wind/percussion/keyboard families.
- **Disjoint union:** `InstrumentFamily DisjointUnionOf StringInstrument, WindInstrument, PercussionInstrument, KeyboardInstrument` or, better, a value-class partition depending on modeling choice.
- **Qualified cardinality:** `StringQuartet SubClassOf hasMember exactly 4 Person`.
- **Value partition:** `InstrumentCondition DisjointUnionOf GoodCondition, FairCondition, PoorCondition`.
- **N-ary relation:** `MusicalPerformance` with performer, work, venue, time.
- **Property chain:** `hasMember o playsInstrument SubPropertyOf ensembleUsesInstrument`.
- **GDC pattern:** `MusicalScore SubClassOf GenericallyDependentContinuant`; score edition/concretization example.
- **SHACL:** condition required for inventory individuals; `playsInstrument` target constraints.

#### E.5 How it supports all 8 skills

- Requirements: write five CQs, use cases, SPARQL tests.
- Scout: reuse BFO, RO, IAO, SKOS, PROV; decide no large music ontology import for the core demo.
- Conceptualizer: BFO alignment and ambiguity for ensemble/object aggregate and score/GDC.
- Architect: ROBOT template for classes, rdflib/OWL API for cardinality/property chain, SHACL shapes.
- Mapper: map demo terms to Wikidata or Music Ontology terms using SSSOM with conservative predicates.
- Validator: reasoner/profile/SHACL/CQ tests and planted anti-patterns.
- SPARQL expert: CQ queries, anti-pattern queries, property-chain diagnostics.
- Curator: deprecate a term, refresh mapping, release v0.1.0.

---

### F. Evaluation harness design

#### F.1 Minimum viable held-out task set

Create `evals/ontology-skills/` with frozen current skills as baseline and revised skills as candidate.

**Task group 1: Skill routing**

- 80 user prompts.
- Expected skill(s), including cross-cutting calls.
- Examples: “Write a CQ test for this requirement,” “Refresh GO imports,” “Check this exactMatch mapping,” “Why did HermiT fail?”

**Score:** top-1 and top-2 routing accuracy.

**Task group 2: Requirements**

- Given 20 natural-language stakeholder needs, generate CQs, SPARQL, manifest, traceability.
- Include 5 deliberately vague/compound CQs.

**Score:** CQ quality rubric, SPARQL parse rate, expected-result correctness, traceability completeness.

**Task group 3: Scout**

- Given a pre-glossary, produce reuse report and import term list.
- Include terms with known OBO reuse candidates and terms that should be new.

**Score:** term reuse precision/recall, license check accuracy, import manifest completeness.

**Task group 4: Conceptualizer**

- Given CQs and reuse report, produce BFO alignment, property design, axiom plan.
- Include ambiguous cases: organization, software, score, role, disposition.

**Score:** BFO category accuracy against gold, ambiguity detection recall, axiom-plan coverage.

**Task group 5: Architect**

- Given axiom plan, generate TTL/templates/shapes.
- Include qualified cardinality, property chain, disjoint union, value partition.

**Score:** Turtle parse, OWL profile report, reasoner pass, ROBOT report errors, SHACL conformance, CQ pass rate.

**Task group 6: Mapper**

- Given 100 candidate mapping pairs with labels/definitions/parents and gold labels.
- Include homonyms and exactMatch traps.

**Score:** predicate precision/recall/F1, exactMatch false-positive rate, clique detection recall, SSSOM validation.

**Task group 7: Validator**

- Given ontologies with planted issues: orphan classes, missing labels, narrow domain/range, unsatisfiable class, stale import, bad CQ aggregate query, invalid SSSOM.

**Score:** anti-pattern detection F1, root-cause classification accuracy, loopback routing accuracy.

**Task group 8: Curator**

- Given change requests: deprecate with replacement, rename, reparent, refresh import, prepare release.

**Score:** KGCL validity, deprecation metadata completeness, version update correctness, diff generation, validation handoff completeness.

**Task group 9: SPARQL**

- Given 30 CQs/diagnostic intents, generate SPARQL.

**Score:** parse rate, execution correctness on fixtures, expected-result contract correctness, performance safeguards.

#### F.2 Automated scoring

Use:

- `rdflib` parse for TTL.
- `prepareQuery` for SPARQL parse.
- ROBOT reason/report/verify/diff.
- `robot validate-profile`.
- `pyshacl`.
- `sssom validate`.
- Custom Python scorers for artifact schemas, traceability, and expected-result contracts.
- Mapping metrics: precision, recall, F1, exactMatch false positives, clique recall.
- Anti-pattern metrics: precision, recall, F1 against planted issues.
- Routing metrics: top-k accuracy.

#### F.3 Baseline

Freeze current skills as `evals/baselines/skills-2026-04-21/`.

Run the same task set against:

1. Baseline current suite.
2. Revised descriptions only.
3. Revised descriptions + governance.
4. Full revised suite + shared references + examples.

This isolates whether the largest gains come from routing metadata, verification gates, or examples.

---

### G. Prioritized roadmap

| Rank | File(s)                                                                                  | Change                                                                                        | Effort | Blocking dependencies                                   |
| ---: | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------- |
|    1 | all `SKILL.md` frontmatter                                                               | Replace descriptions with redlined routing-rich descriptions                                  | XS     | none                                                    |
|    2 | `CONVENTIONS.md`, `SKILL-TEMPLATE.md`                                                    | Add Progress Criteria, LLM Verification Required, Loopback Triggers, Worked Examples sections | S      | none                                                    |
|    3 | `_shared/llm-verification-patterns.md`; all skills                                       | Add standard LLM verification gates                                                           | S      | #2                                                      |
|    4 | `_shared/iteration-loopbacks.md`; `CONVENTIONS.md`; validator                            | Add downstream rejection/loopback protocol                                                    | S      | #2                                                      |
|    5 | `ontology-requirements/SKILL.md`; `sparql-expert/SKILL.md`                               | Add CQ quality scoring, SPARQL parse/run gate, requirements approval artifact                 | S      | #2                                                      |
|    6 | `_shared/reasoner-strategy.md`; architect, validator, tool tree                          | Unify profile/reasoner strategy and HermiT/ELK gates                                          | S      | #2                                                      |
|    7 | `_shared/robot-template-preflight.md`; architect                                         | Extract template gotchas and add preflight gate                                               | S      | #6                                                      |
|    8 | `_shared/shacl-patterns.md`; architect, validator, conceptualizer                        | Add SHACL authoring patterns and shape coverage checks                                        | M      | #2                                                      |
|    9 | `_shared/imports-management.md`; `_shared/imports-manifest.md`; scout, curator           | Add import manifest and refresh workflow                                                      | M      | #4                                                      |
|   10 | `_shared/odk-integration.md`; architect, validator, curator, scout                       | Add ODK-managed vs standalone POD workflow                                                    | M      | #9                                                      |
|   11 | `_shared/mapping-evaluation.md`; mapper, validator                                       | Add OAEI-style metrics, clique checks, obsolete-term report                                   | S/M    | #4                                                      |
|   12 | `_shared/bridge-ontology-lifecycle.md`; mapper, curator, validator                       | Add bridge ontology generation/reasoning/publication workflow                                 | M      | #11                                                     |
|   13 | conceptualizer; `_shared/bfo-categories.md`; worked examples                             | Add BFO ambiguity register and worked examples                                                | S/M    | #3                                                      |
|   14 | `_shared/dosdp-patterns.md`; scout, architect                                            | Add DOSDP/ODP pattern-based modeling                                                          | M      | #10                                                     |
|   15 | `sparql/anti-patterns/`; `_shared/anti-pattern-query-library.md`; validator              | Externalize anti-pattern SPARQL and add severity/detection modes                              | M      | #8                                                      |
|   16 | `worked-examples/music-ensemble/`                                                        | Build end-to-end demo domain covering all 8 skills                                            | L      | #5–#14                                                  |
|   17 | `evals/ontology-skills/`                                                                 | Implement MVP evaluation harness and freeze baseline                                          | M/L    | #16 for end-to-end tests; can start earlier for routing |
|   18 | curator; `_shared/publication-content-negotiation.md`; `_shared/jsonld-schema-export.md` | Add publication, PURL/content negotiation, schema.org JSON-LD guidance                        | M      | #10                                                     |
|   19 | `_shared/provenance-patterns.md`; architect, scout, mapper, curator                      | Add PROV-O granularity patterns                                                               | S/M    | #8                                                      |
|   20 | `_shared/github-actions-template.md`; validator, curator                                 | Add CI/CD templates for standalone POD and ODK                                                | M      | #6, #8, #10                                             |

---

## Appendix — Open questions back to the repo owner

1. Should approval artifacts be lightweight YAML files committed to the repo, or are GitHub PR review states acceptable as approval records?

2. Is the workspace intended to support ODK-managed projects directly, or only to be ODK-aware while keeping the current POD layout?

3. Should the Skygest energy exemplar remain the primary worked example, or should the new music-ensemble demo be the canonical small example while Skygest remains the production-scale exemplar?

4. What is the expected deployment model for published ontologies: GitHub Pages, PURL/OBO-style release, internal API, SPARQL endpoint, or all of these?

5. Should SHACL warnings block release or remain tracked technical debt? The current quality checklist treats definition warnings as non-blocking, but release policy should be explicit.

6. Should full-DL reasoner validation be mandatory for every release, or only when the axiom inventory contains non-EL features?

7. What mapping gold sets exist, if any, for current projects? If none, the mapper evaluation harness should first create small curated gold/dev sets.

8. Should the repository adopt date-based versioning everywhere, or allow semver for non-OBO project ontologies and date-based IRIs for OBO-style releases?

9. Should `skos:definition` continue as the canonical definition property, or should build scripts mirror it to `IAO:0000115` to align with ROBOT/OBO report expectations?

10. Should future helper skills be allowed, or should the project intentionally keep exactly eight skills and use shared references for all implementation detail?

[1]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices "Skill authoring best practices - Claude API Docs"
[2]: https://www.w3.org/TR/owl2-profiles/ "OWL 2 Web Ontology Language Profiles (Second Edition)"
[3]: https://mapping-commons.github.io/sssom/linkml-index/ "LinkML documentation - A Simple Standard for Sharing Ontology Mappings (SSSOM)"
[4]: https://www.w3.org/TR/shacl/ "Shapes Constraint Language (SHACL)"
[5]: https://oa.upm.es/5484/1/METHONTOLOGY_.pdf "Methontology: From Ontological Art Towards Ontological Engineering"
[6]: https://link.springer.com/chapter/10.1007/978-0-387-34847-6_3 "The Role of Competency Questions in Enterprise Engineering | Springer Nature Link"
[7]: https://oeg.fi.upm.es/index.php/en/methodologies/59-neon-methodology/index.html "The NeOn Methodology"
[8]: https://www.iso.org/standard/74572.html " ISO/IEC 21838-2:2021 - Information technology — Top-level ontologies (TLO) — Part 2: Basic Formal Ontology (BFO)"
[9]: https://link.springer.com/article/10.1186/s13326-017-0126-0 "Dead simple OWL design patterns | Journal of Biomedical Semantics | Springer Nature Link"
[10]: https://ceur-ws.org/Vol-4144/om2025-oaei-paper0.pdf "Results of the Ontology Alignment Evaluation \\\\ Initiative 2025"
[11]: https://www.w3.org/TR/prov-o/ "PROV-O: The PROV Ontology"
[12]: https://schema.org/ "Schema.org - Schema.org "
[13]: https://obofoundry.org/principles/fp-000-summary.html "OBO Foundry"
[14]: https://github.com/ontodev/robot/blob/master/docs/template.md "robot/docs/template.md at master · ontodev/robot · GitHub"
[15]: https://incatools.github.io/ontology-development-kit/ "Ontology Development Kit (ODK)"
