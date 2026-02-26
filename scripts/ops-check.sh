#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_FILE="${SRS_REPORT_FILE:-}"
HISTORY_FILE="${SRS_HISTORY_FILE:-}"
STALE_HOURS_THRESHOLD="${SRS_STALE_HOURS:-168}"
STRICT_STALE_FAIL="${SRS_STRICT_STALE_FAIL:-0}"
FAILURES=0
STALE_ALERT=false
REPO_ACTIVITY_STATUS="fresh"
REPO_ACTIVITY_REASON="within_threshold"

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

check_repo_activity() {
  local latest_commit_epoch latest_commit_iso now_epoch age_hours
  latest_commit_epoch="$(git -C "$REPO_ROOT" log -1 --format=%ct 2>/dev/null || echo 0)"
  latest_commit_iso="$(git -C "$REPO_ROOT" log -1 --format=%cI 2>/dev/null || echo unknown)"
  now_epoch="$(date +%s)"

  if [[ "$latest_commit_epoch" =~ ^[0-9]+$ ]] && (( latest_commit_epoch > 0 )); then
    age_hours=$(( (now_epoch - latest_commit_epoch) / 3600 ))
  else
    age_hours=999999
  fi

  if (( age_hours >= STALE_HOURS_THRESHOLD )); then
    STALE_ALERT=true
    REPO_ACTIVITY_STATUS="stale"
    REPO_ACTIVITY_REASON="age_hours_threshold_reached"
    echo "[society-reverse-sim] repo activity: stale (${age_hours}h >= ${STALE_HOURS_THRESHOLD}h, latest=${latest_commit_iso})"
    if [[ "$STRICT_STALE_FAIL" == "1" ]]; then
      FAILURES=$((FAILURES + 1))
    fi
  else
    REPO_ACTIVITY_STATUS="fresh"
    REPO_ACTIVITY_REASON="within_threshold"
    echo "[society-reverse-sim] repo activity: fresh (${age_hours}h < ${STALE_HOURS_THRESHOLD}h, latest=${latest_commit_iso})"
  fi
}

check_file "readme" "${REPO_ROOT}/README.md"
check_file "roadmap" "${REPO_ROOT}/docs/ROADMAP.md"
check_token "concept section" "${REPO_ROOT}/README.md" "##[[:space:]]+.*(Concept|Overview|Background)"
check_token "inverse mode" "${REPO_ROOT}/README.md" "(Reverse simulation|inverse social simulation|Inverse mode)"
check_token "status section" "${REPO_ROOT}/README.md" "##[[:space:]]+.*Status"
check_repo_activity

if (( FAILURES > 0 )); then
  status="fail"
  code=1
else
  status="ok"
  code=0
fi

summary="{\"service\":\"society-reverse-sim\",\"status\":\"${status}\",\"failures\":${FAILURES},\"staleHoursThreshold\":${STALE_HOURS_THRESHOLD},\"staleAlert\":${STALE_ALERT},\"repoActivityStatus\":\"${REPO_ACTIVITY_STATUS}\",\"repoActivityReason\":\"${REPO_ACTIVITY_REASON}\",\"strictStaleFail\":${STRICT_STALE_FAIL},\"ts\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
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
