# Learning

## Material ingestion
- `ingestLearningMaterial` stores a material, splits text into chunks
  (`chunkMaterial`), calls `AIProvider.summarizeMaterial` (topics, one-line summary),
  then generates a 14-day plan (`learningPlans`) with lessons.
- `generateLesson` materializes a lesson with content the user actually reads for
  master-y: content, challenges, and a generated quiz from the AI provider.

## Quizzes & mastery
- Quiz generation (`quiz` module in `learning.ts`) uses `AIProvider.generateQuiz`
  validated against `aiQuizOutput` — malformed output is rejected, never stored.
- `nextQuestionIdx(attempt)` seeds the attempt; `gradeAnswer` grades each answer
  against the server-stored question — **the gold answers never leave the backend**.
- On quiz completion, `quizLessonProof` → submits proof through the standard
  `verifyProofAutomatic` quiz path (score ≥ 0.7 = pass) → golden reward path.
- Mastery state lives in `conceptMastery` per (user, topic/concept); weak areas
  surface via `learning.ts` and the Explore screen ranked list.

## Domain (`packages/domain/src/learning.ts`)
Pure helpers: `normalizeTopics`, `rankTopics(attempts, weights)` (recency/score
mixing), and `chunkMaterial`.

## Screens
- Learning Library (`learning-library`) lists ingested materials, topics, and mastery.
- Lesson flow shows content + challenge; finishing a lesson verifies quiz proof.
- Generation is safe: attempts replicating a known lesson id just return it.