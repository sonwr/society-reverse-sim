#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="${SRS_REPORT_FILE:-}"
HISTORY_FILE="${SRS_HISTORY_FILE:-}"
FAILURES=0

check_file() {
  local label="$1"
  local path="$2"

  if [[ -f "$path" ]]; then
    echo "[society-reverse-sim] ${label}: ok (${path})"
  else
    echo "[society-reverse-sim] ${label}: missing (${path})"
    FAILURES=$((FAILURES + 1))
  fi
}

check_token() {
  local label="$1"
  local path="$2"
  local pattern="$3"

  if grep -Eqi "$pattern" "$path"; then
    echo "[society-reverse-sim] ${label}: ok (${pattern})"
  else
    echo "[society-reverse-sim] ${label}: missing token (${pattern})"
    FAILURES=$((FAILURES + 1))
  fi
}

check_file "readme" "${REPO_ROOT}/README.md"
check_file "roadmap" "${REPO_ROOT}/docs/ROADMAP.md"
check_token "concept section" "${REPO_ROOT}/README.md" "##[[:space:]]+.*(Concept|Overview|Background)"
check_token "inverse mode" "${REPO_ROOT}/README.md" "(Reverse simulation|inverse social simulation|Inverse mode)"
check_token "status section" "${REPO_ROOT}/README.md" "##[[:space:]]+.*Status"

if (( FAILURES > 0 )); then
  status="fail"
  code=1
else
  status="ok"
  code=0
fi

summary="{\"service\":\"society-reverse-sim\",\"status\":\"${status}\",\"failures\":${FAILURES},\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
echo "${summary}"

if [[ -n "$REPORT_FILE" ]]; then
  printf '%s\n' "$summary" > "$REPORT_FILE"
  echo "[society-reverse-sim] wrote report: ${REPORT_FILE}"
fi

if [[ -n "$HISTORY_FILE" ]]; then
  printf '%s\n' "$summary" >> "$HISTORY_FILE"
  echo "[society-reverse-sim] appended history: ${HISTORY_FILE}"
fi

exit "$code"
