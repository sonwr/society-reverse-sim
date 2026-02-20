# society-reverse-sim roadmap

## Phase 0 — Bootstrap (Done)
- Repository initialized
- Direction and scope documented

## Phase 1 — Modeling contracts
- Define world state schema
- Define policy/rule schema
- Define outcome signature schema

## Phase 2 — Forward simulator
- Build minimal agent population simulator
- Add deterministic random seed support
- Emit timeline events and summary metrics

## Phase 3 — Inverse engine
- Implement parameter search (grid/heuristic)
- Score candidate initial states against target outcomes
- Return top-k hypotheses with confidence scores

## Phase 4 — Explainability layer
- Add feature sensitivity notes
- Add uncertainty and non-uniqueness annotations
- Add markdown summary for human review

## Phase 5 — Tooling
- CLI runner (`forward`, `inverse`)
- sample datasets
- CI test pipeline
