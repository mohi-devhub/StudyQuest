import { XP_VALUES } from "@/types/enums";

/**
 * Calculate level from total XP
 */
export function calculateLevel(totalXP: number): number {
  return Math.floor(totalXP / XP_VALUES.XP_PER_LEVEL) + 1;
}

/**
 * Calculate XP in current level
 */
export function calculateXPInCurrentLevel(totalXP: number): number {
  return totalXP % XP_VALUES.XP_PER_LEVEL;
}

/**
 * Calculate XP needed for next level
 */
export function calculateXPToNextLevel(totalXP: number): number {
  return XP_VALUES.XP_PER_LEVEL - calculateXPInCurrentLevel(totalXP);
}

/**
 * Generate XP progress bar (20 blocks)
 */
export function generateXPBar(totalXP: number): string {
  const xpInCurrentLevel = calculateXPInCurrentLevel(totalXP);
  const progress = (xpInCurrentLevel / XP_VALUES.XP_PER_LEVEL) * 20;
  const filled = Math.floor(progress);
  const empty = 20 - filled;

  return "[" + "█".repeat(filled) + "░".repeat(empty) + "]";
}

/**
 * Calculate progress percentage (0-100)
 */
export function calculateXPProgress(totalXP: number): number {
  const xpInCurrentLevel = calculateXPInCurrentLevel(totalXP);
  return (xpInCurrentLevel / XP_VALUES.XP_PER_LEVEL) * 100;
}
