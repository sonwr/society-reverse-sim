# society-reverse-sim

Forward + inverse social simulation with generative agents.

## Concept

This project supports two modes:

1. **Forward simulation**
   - Given initial conditions and rules,
   - simulate emergent social outcomes.

2. **Reverse simulation (inverse mode)**
   - Given observed outcomes,
   - infer plausible initial conditions/rule sets that could produce them.

## Why inverse mode matters

Most simulators answer: "What happens if we start here?"
This project also asks: "Given what we see now, what likely led us here?"

The inverse problem is non-unique by nature, so outputs are represented as:
- scenario candidates,
- confidence/probability bands,
- sensitivity notes.

## MVP scope (v0)

- Define forward state model
- Define outcome signature model
- Implement baseline forward simulator (small toy world)
- Implement inverse search over parameter space
- Output top-k plausible scenario sets

## Repo plan

See `docs/ROADMAP.md`.

## Status

- [x] Repository bootstrap
- [ ] Baseline forward simulator
- [ ] Inverse search engine
- [ ] Scenario scoring + explainability
