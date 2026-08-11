#!/usr/bin/env bash
# =============================================================================
# job_monitor.sh — submit an Abaqus job, monitor it, and capture the logs
# Usage:
#   ./job_monitor.sh Job-1                # submit background + monitor
#   ./job_monitor.sh Job-1 cpus=8         # pass extra abaqus args
#   ./job_monitor.sh Job-1 --poll-only    # only monitor an existing run
# =============================================================================
set -u

JOB="${1:-Job-1}"
EXTRA="${2:-}"

if [ "${2:-}" = "--poll-only" ]; then
  POLL_ONLY=1
else
  POLL_ONLY=0
fi

POLL_INTERVAL="${ABAQUS_POLL_INTERVAL:-20}"   # seconds

# --- submit --------------------------------------------------------------
if [ "$POLL_ONLY" = "0" ]; then
  echo "[$(date +%H:%M:%S)] submitting job $JOB"
  # shellcheck disable=SC2086
  abaqus job="$JOB" background $EXTRA
  if [ $? -ne 0 ]; then
    echo "ERROR: abaqus submit failed" >&2
    exit 1
  fi
  echo "  submitted (command saved to $JOB.com)"
fi

# --- wait for the lock file to disappear ---------------------------------
if [ ! -f "$JOB.lck" ]; then
  echo "WARNING: no $JOB.lck found — job may have already finished or never started"
fi

echo "[$(date +%H:%M:%S)] monitoring $JOB (poll every ${POLL_INTERVAL}s)..."
LAST_STA=""
while [ -f "$JOB.lck" ]; do
  sleep "$POLL_INTERVAL"
  if [ -f "$JOB.sta" ]; then
    CUR=$(tail -1 "$JOB.sta" 2>/dev/null)
    if [ "$CUR" != "$LAST_STA" ]; then
      echo "[$(date +%H:%M:%S)] $(echo "$CUR" | tr -s ' ' | cut -c1-100)"
      LAST_STA="$CUR"
    fi
  fi
  # abort early if the log says the solver died
  if [ -f "$JOB.log" ] && grep -qiE "aborted|exited with an error" "$JOB.log"; then
    echo "[$(date +%H:%M:%S)] ERROR: solver appears to have aborted" >&2
    break
  fi
done

# --- summary ---------------------------------------------------------------
echo ""
echo "=== $JOB finished at $(date +%H:%M:%S) ==="

if [ -f "$JOB.log" ]; then
  echo "--- last lines of $JOB.log ---"
  tail -8 "$JOB.log"
fi

if grep -q "THE ANALYSIS HAS COMPLETED SUCCESSFULLY" "$JOB.log" 2>/dev/null; then
  echo "STATUS: SUCCESS"
  exit 0
elif grep -qiE "aborted|error" "$JOB.log" 2>/dev/null; then
  echo "STATUS: FAILED"
  echo "--- errors in $JOB.msg (if any) ---"
  grep -iE "^error" "$JOB.msg" 2>/dev/null | head -10 || true
  exit 1
else
  echo "STATUS: UNKNOWN — inspect $JOB.log / $JOB.dat / $JOB.msg manually"
  exit 2
fi
