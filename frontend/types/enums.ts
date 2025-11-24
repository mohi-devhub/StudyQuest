/**
 * Quiz difficulty levels
 */
export enum QuizDifficulty {
  EASY = "easy",
  MEDIUM = "medium",
  HARD = "hard",
  EXPERT = "expert",
}

/**
 * Quiz generation modes
 */
export enum QuizMode {
  SELECT = "select",
  SAVED = "saved",
  UPLOAD = "upload",
  TOPIC = "topic",
  QUIZ = "quiz",
}

/**
 * Topic mastery status
 */
export enum TopicStatus {
  NOT_STARTED = "not_started",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  MASTERED = "mastered",
}

/**
 * Badge tier levels
 */
export enum BadgeTier {
  BRONZE = "bronze",
  SILVER = "silver",
  GOLD = "gold",
  PLATINUM = "platinum",
}

/**
 * XP gain types
 */
export enum XPType {
  STUDY_SESSION = "study_session",
  QUIZ_COMPLETE = "quiz_complete",
  QUIZ_PERFECT = "quiz_perfect",
  TOPIC_RETRY = "topic_retry",
  ACHIEVEMENT = "achievement",
  STREAK = "streak",
}

/**
 * XP constants
 */
export const XP_VALUES = {
  STUDY_SESSION: 50,
  QUIZ_EASY: 100,
  QUIZ_MEDIUM: 150,
  QUIZ_HARD: 200,
  QUIZ_EXPERT: 250,
  TOPIC_RETRY: 10,
  PERFECT_SCORE_BONUS: 50,
  XP_PER_LEVEL: 500,
} as const;

/**
 * Score thresholds
 */
export const SCORE_THRESHOLDS = {
  MASTERED: 95,
  COMPLETED: 80,
  PASSING: 70,
} as const;
