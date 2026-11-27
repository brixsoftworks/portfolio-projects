# SECURITY ACTION REQUIRED

## Findings (Phase 0 audit, 2026-08-22)

| Secret | Location | Status |
|---|---|---|
| Gemini API key (`AQ.Ab8RN6…`) | `.env` (untracked, working tree) AND git history at commit `78331ec3` ("Configure for Render and Vercel deployment"); removed again by `d1aef12d` | LIVE IN HISTORY |
| Vercel OIDC token (short-lived JWT) | `frontend/.env.vercel` (untracked) | Low risk, expired |

## ACTION REQUIRED
1. **Rotate the Gemini key** immediately — it is recoverable from remote
   history on github.com/brixsoftworks/dealhunter-ai-backend via
   `git show 78331ec3:.env`.
2. Recommended follow-up (needs human confirmation): purge the blob with
   `git filter-repo --path .env --invert-paths` (or BFG), then force-push.

## Fixed automatically (this audit)
- Verified `.env` is NOT tracked in HEAD; only `.env.example` is tracked.
- Verified `.gitignore` covers `.env`.
- No code changes required: key is read from env (`dotenv`).
