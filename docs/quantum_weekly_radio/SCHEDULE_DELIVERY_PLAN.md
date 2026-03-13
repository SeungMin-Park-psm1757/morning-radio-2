# Schedule and Delivery Plan

## 1. Schedule target

Desired local time:
- Monday 06:30 KST

Equivalent UTC cron target:
- Sunday 21:30 UTC

## 2. Why use 30 minutes past the hour

GitHub Actions scheduled workflows can be delayed during high-load periods, especially around the top of the hour.
Choosing a half-hour slot reduces collision with common schedule spikes.

## 3. Public repository risk

Public repositories can have scheduled workflows automatically disabled after inactivity.
Treat the GitHub workflow as good MVP infrastructure, but not as the only long-term reliability layer.

## 4. MVP recommendation

### Phase 1
Use GitHub Actions schedule plus manual dispatch.

### Phase 2
Add heartbeat / monitoring and a missed-run alert.

### Phase 3
If timing becomes critical, move scheduling to an external scheduler while keeping GitHub as the source repo.

## 5. Delivery bundle

Telegram bundle per successful weekly run:
1. weekly text digest
2. weekly full MP3
3. weekly headlines MP3

## 6. Manual backfill

Support a manual CLI mode:
- explicit `window_start`
- explicit `window_end`
- optional `--dry-run`
- optional `--skip-telegram`
- optional `--skip-tts`
