# AI

## Interface
`packages/ai/src/interfaces.ts` defines `AIProvider`:

| Method | Purpose | Validated by |
| --- | --- | --- |
| `generatePlan(GoalPromptInput)` | 14/30-day plan + milestones | `GoalAIPlan` (types) |
| `generateLesson` | lesson copy from uploaded material | inline contract |
| `generateQuiz(QuizPromptInput)` | quiz questions | `aiQuizOutput` (validation) |
| `summarizeMaterial` | topics + summary for uploads | inline |
| `generateCoachMessage` | one-line duck motivation | `aiCoachOutput` |
| `generateGroupMessage` | group-chat interjection | `aiGroupMessageOutput` |
| `analyzeProof(ProofPromptInput)` | verdict + confidence + reason | `aiProofVerdict` |
| `generateRescueMission` | comeback mission after a miss | inline |
| `generateGame` | battle/streak-game prompts | inline |

## Providers

### DemoProvider (`packages/ai/src/demo.ts`)
Deterministic, zero-dependency, always returns schema-valid output. Used by CI, demo
mode, and as the production fallback when `AI_API_KEY` is absent. It exercises the
entire pipeline (validation, mission generation, proof verification, coaching) with no
network.

### HttpProvider (`packages/ai/src/http.ts`)
OpenAI-compatible `POST {baseUrl}/chat/completions`. Construct with
`createHttpProvider({ baseUrl, apiKey, model })`. Every method:
1. builds a prompt requesting strict JSON,
2. calls the model once (with a JSON response format when supported),
3. validates the reply with the matching zod schema and throws `ValidationFailure` on
   malformed output list — a provider never lets bad AI output corrupt state.

## Where AI is used
- Plan generation when a goal is created (`goals.ts`).
- Quiz questions for learning materials (`learning.ts`).
- Coach messages (`social.ts requestCoachMessage`).
- Group interjections (`simulateGroupAIMessage`).
- Proof triage for media (photo/video/audio/screenshot) in `verifyProofAutomatic`-style gates
  (media types go to `analyzeProof`; the verdict feeds human verification queue).
- Rescue missions after a broken streak.

## Prompt contract
Prompts are versioned inline in `http.ts`. Keep output schemas in `@quacko/validation`
so DemoProvider and HttpProvider stay structurally identical.