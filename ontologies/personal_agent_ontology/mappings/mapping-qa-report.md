# PAO Mapping Quality Report

Date: 2026-02-18
Version: 0.2.0
Mapper: ontology-mapper skill

## Summary

| Metric | Value |
|--------|-------|
| Mapping files | 4 |
| Total mappings | 44 |
| PAO classes mapped | 20/46 (43%) |
| PAO properties mapped | 5/60 (8%) |
| exactMatch count | 2 |
| Transitivity conflicts | 0 |
| Validation errors | 0 |

## Mapping Files

### pao-to-schema.sssom.tsv (schema.org)

- **Target**: schema.org vocabulary (web interoperability)
- **Mappings**: 14
- **Predicates**: closeMatch (7), broadMatch (4), exactMatch (2), narrowMatch (1)
- **Confidence**: 0.55 - 0.95 (mean 0.73)
- **exactMatch pairs**:
  - `pao:Conversation` -> `schema:Conversation` (0.95)
  - `pao:Message` -> `schema:Message` (0.92)
- **Rationale**: Schema.org is the primary interoperability target. Action,
  conversation, and message concepts have strong structural overlap. Memory
  operations map to CRUD actions at a broader level.

### pao-to-as2.sssom.tsv (ActivityStreams 2.0)

- **Target**: W3C ActivityStreams 2.0 (activity log interop, Fediverse)
- **Mappings**: 12
- **Predicates**: closeMatch (7), broadMatch (5)
- **Confidence**: 0.55 - 0.85 (mean 0.72)
- **Rationale**: AS2 provides a complementary activity vocabulary. The
  Actor/Activity/Object model maps naturally to PAO's Agent/Action/Entity
  pattern, but AS2's looser semantics prevent exactMatch.

### pao-to-sioc.sssom.tsv (SIOC)

- **Target**: Semantically-Interlinked Online Communities (conversation threading)
- **Mappings**: 10 (including 3 property mappings)
- **Predicates**: closeMatch (8), broadMatch (2)
- **Confidence**: 0.55 - 0.90 (mean 0.78)
- **Rationale**: SIOC's Thread/Post model is the closest structural match
  to PAO's Conversation/Turn pattern. Property mappings (hasTopic, hasContent,
  partOfConversation) strengthen the alignment. SIOC is the highest mean
  confidence mapping set.

### pao-to-dpv.sssom.tsv (Data Privacy Vocabulary)

- **Target**: W3C Data Privacy Vocabulary (privacy compliance)
- **Mappings**: 8 (including 1 property mapping)
- **Predicates**: closeMatch (6), broadMatch (2)
- **Confidence**: 0.55 - 0.85 (mean 0.70)
- **Rationale**: DPV aligns with PAO's governance module (PermissionPolicy,
  SafetyConstraint, ErasureEvent). Essential for privacy compliance
  interoperability in agent systems handling personal data.

## Predicate Distribution

| Predicate | Count | % |
|-----------|-------|---|
| skos:closeMatch | 28 | 63.6% |
| skos:broadMatch | 13 | 29.5% |
| skos:exactMatch | 2 | 4.5% |
| skos:narrowMatch | 1 | 2.3% |

The conservative predicate distribution (64% closeMatch, 30% broadMatch)
reflects the cross-domain nature of these mappings. PAO's BFO-aligned formal
semantics rarely match exactly with the lighter-weight web vocabularies.
Only 2 mappings qualify as exactMatch (Conversation and Message to schema.org).

## Transitivity Analysis

- **exactMatch chains**: None detected. The 2 exactMatch mappings
  (pao:Conversation, pao:Message) only target schema.org and do not
  participate in any transitive chains across mapping files.
- **Clique size**: Maximum clique size is 2 (binary pairs only).

## Coverage Analysis

### Mapped PAO Classes (20/37)

| PAO Class | Mapping Targets |
|-----------|----------------|
| Action | schema, as2 |
| Agent | schema, as2, sioc, dpv |
| AIAgent | schema, as2 |
| Claim | (unmapped) |
| CompactionEvent | (unmapped) |
| ComplianceStatus | (unmapped) |
| Consolidation | as2 |
| Conversation | schema, as2, sioc |
| Encoding | schema, as2 |
| Episode | (unmapped) |
| ErasureEvent | schema, as2, dpv |
| Forgetting | schema, as2 |
| Goal | (unmapped) |
| HumanUser | schema, as2, sioc, dpv |
| MemoryItem | dpv |
| MemoryOperation | (unmapped) |
| MemoryTier | (unmapped) |
| Message | schema, sioc |
| PermissionPolicy | dpv |
| Plan | schema |
| Retrieval | schema, as2 |
| SafetyConstraint | dpv |
| Session | sioc |
| SessionStatus | (unmapped) |
| Status | (unmapped) |
| SubAgent | (unmapped) |
| Task | schema |
| TaskStatus | (unmapped) |
| ToolDefinition | (unmapped) |
| ToolInvocation | schema, as2 |
| Turn | schema, sioc |
| WorkingMemory | (unmapped) |
| EpisodicMemory | (unmapped) |
| SemanticMemory | (unmapped) |
| ProceduralMemory | (unmapped) |
| AgentRole | sioc |

### Unmapped Classes (17/37)

The 17 unmapped classes fall into two categories:

**Domain-specific (no external equivalents)**: Claim, CompactionEvent,
Episode, MemoryOperation, MemoryTier, WorkingMemory, EpisodicMemory,
SemanticMemory, ProceduralMemory, SubAgent, ToolDefinition. These
represent PAO's novel contributions to the AI agent domain.

**Value partitions (not mappable)**: Status, SessionStatus, TaskStatus,
ComplianceStatus, Goal. Status types are PAO-internal value partitions.
Goal has no close match in target vocabularies.

## Methodology

- **Candidate generation**: Manual semantic analysis informed by reuse
  report recommendations (no lexical matching — target vocabularies are
  not OBO-format ontologies).
- **Verification**: LLM-assisted semantic evaluation with definition
  comparison, parent class analysis, and BFO category alignment.
- **Confidence calibration**: Conservative confidence assignments reflecting
  cross-domain semantic distance. Scores below 0.55 were excluded.
- **Justification**: All mappings use `semapv:SemanticSimilarityThresholdMatching`.

## Recommendations

1. **SIOC property mappings could be extended**: Additional property
   pairs (e.g., performedBy/sioc:has_creator, inSession/sioc:has_container)
   could strengthen the conversation threading alignment.

2. **SEM (Simple Event Model) mapping**: Identified as Priority 5 in the
   reuse report but not yet created. Would add 3-4 broadMatch pairs for
   the event hierarchy.

3. **BDI Ontology mapping**: Low priority (Priority 6) due to DOLCE
   alignment mismatch with PAO's BFO foundation. Would use relatedMatch
   only.

4. **Future versions**: As target vocabularies evolve, review mappings
   for upgraded predicates (closeMatch -> exactMatch where definitions
   converge).
