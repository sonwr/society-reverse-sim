# society-reverse-sim

Forward + inverse social simulation for causal hypothesis generation.

<p align="center">
  <img src="./docs/assets/readme/hero.svg" alt="society-reverse-sim hero" width="100%"/>
</p>

## Concept

Most simulators answer: “What happens if we start here?”

This project also answers: “Given what we observe now, what likely produced it?”

## Modes

- **Forward simulation**: rules and initial states → outcomes
- **Inverse mode**: outcomes → top-k plausible origin scenarios

## Screenshots

Sanitized terminal check:

![society-reverse-sim terminal](./docs/assets/screenshots/terminal.svg)

## MVP scope

- Forward state model
- Outcome signature model
- Baseline simulator
- Inverse search over parameter space
- Ranked scenario candidate output

## Operations check

```bash
chmod +x scripts/ops-check.sh
./scripts/ops-check.sh
```

Optional:

```bash
SRS_REPORT_FILE=/tmp/society-reverse-sim-report.json ./scripts/ops-check.sh
SRS_HISTORY_FILE=/tmp/society-reverse-sim-history.jsonl ./scripts/ops-check.sh
```

## Status

- [x] Bootstrap + roadmap
- [ ] Forward simulator baseline
- [ ] Inverse search core
- [ ] Explainable scoring layer

## License

MIT (or project-defined license)
