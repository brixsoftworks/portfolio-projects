# Social & Battles

## Groups & chat
- `createGroup(name, memberUids)` creates the group + `groupMembers` docs (owner) and
  joins the provided users.
- `sendMessage` appends to `messages` with `authorId`; the store keeps it listed.
- `simulateGroupAIMessage` calls `AIProvider.generateGroupMessage` — the duck posts a
  neutral-or-nudging interjection so a quiet week feels alive.

## Battles
- `startBattle(uid, goalId, otherUids)` — resolves the selected goal per owner, creates a
  `battle` with `scheduledWindowTimes`-based deadline, and per-participant `battleTicks`.
- `battleCheckIn(uid, battleId)` appends the day's completed-mission count to the
  participant's tick (`streakTarget: dailyContribution`).
- `resolveBattle(uid, battleId)` closes a battle; `domain/battle.ts` computes the
  winner/loser, winner XP bonus, and stakes resolution.

### Battle math (`packages/domain/src/battle.ts`)
- `scheduledNowAwareProgress(battle, nowMs)` returns `{ self, opponents, countdown }`
  with the Duck's own tick as the zero index.
- `claimBattleReward(battle, selfUid)` → `{ winnerId, xp }`, `result` keyed by
  participant. Base XP split: winner/allowedSplit, others split the remainder.

## Punishment council
- `createPunishment(uid, type, deadlineAt)` queues a faux punishment document
  (`punishments` + `punishmentVotes`).
- `submitPunishmentVote(uid, punishmentId, sentenceScore)` adds a vote (owner votes
  last): once a quorum/count is reached the council renders a verdict the user has to
  live with — ship self-sabotage app or sink into debt — and locks the punishment.

## Coach
- `requestCoachMessage(uid, context)` → `AIProvider.generateCoachMessage` seeded with the
  user's streak snapshot; replies render as the Quacko duck on the chat tab.
- `getChatHistory` returns the sent messages for the chat UI.

## Enemies & gifting
- `getEnemies` resolves "enemies" from follower-adjacent social pointers in the user
  profile (MVP: demo roster). Group gifting/blob events are stubbed behind `groups`.