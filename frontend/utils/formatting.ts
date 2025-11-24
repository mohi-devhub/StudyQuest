import { TopicStatus } from "@/types/enums";

/**
 * Format percentage with fixed decimals and padding
 */
export function formatPercentage(
  num: number,
  decimals: number = 1,
  padding: number = 5,
): string {
  return num.toFixed(decimals).padStart(padding, " ");
}

/**
 * Pad string to the right with spaces
 */
export function padRight(str: string, length: number): string {
  return str.padEnd(length, " ");
}

/**
 * Get status symbol for topic status
 */
export function getStatusSymbol(status: string): string {
  switch (status) {
    case TopicStatus.MASTERED:
      return "★★★";
    case TopicStatus.COMPLETED:
      return "★★☆";
    case TopicStatus.IN_PROGRESS:
      return "★☆☆";
    default:
      return "☆☆☆";
  }
}

/**
 * Get color class based on score
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return "text-terminal-white";
  if (score >= 70) return "text-terminal-gray";
  return "text-terminal-gray opacity-70";
}

/**
 * Format date to relative time (e.g., "2d ago", "Today")
 */
export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  const daysSince = Math.floor(
    (Date.now() - dateObj.getTime()) / (1000 * 60 * 60 * 24),
  );

  if (daysSince === 0) return "Today";
  if (daysSince === 1) return "Yesterday";
  if (daysSince < 7) return `${daysSince}d ago`;
  if (daysSince < 30) return `${Math.floor(daysSince / 7)}w ago`;
  return `${Math.floor(daysSince / 30)}mo ago`;
}

/**
 * Format date to a readable string
 */
export function formatDate(date: string | Date): string {
  const dateObj = typeof date === "string" ? new Date(date) : date;
  return dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Format file size in bytes to human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

/**
 * Truncate string with ellipsis
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + "...";
}
