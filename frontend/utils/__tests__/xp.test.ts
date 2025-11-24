import {
  calculateLevel,
  calculateXPInCurrentLevel,
  calculateXPToNextLevel,
  generateXPBar,
  calculateXPProgress,
} from "../xp";

describe("XP Utilities", () => {
  describe("calculateLevel", () => {
    it("calculates correct level for 0 XP", () => {
      expect(calculateLevel(0)).toBe(1);
    });

    it("calculates correct level for 500 XP (level 2)", () => {
      expect(calculateLevel(500)).toBe(2);
    });

    it("calculates correct level for 1500 XP (level 4)", () => {
      expect(calculateLevel(1500)).toBe(4);
    });
  });

  describe("calculateXPInCurrentLevel", () => {
    it("returns 0 for exact level boundary", () => {
      expect(calculateXPInCurrentLevel(500)).toBe(0);
    });

    it("returns correct XP within level", () => {
      expect(calculateXPInCurrentLevel(250)).toBe(250);
      expect(calculateXPInCurrentLevel(750)).toBe(250);
    });
  });

  describe("calculateXPToNextLevel", () => {
    it("calculates XP needed from 0", () => {
      expect(calculateXPToNextLevel(0)).toBe(500);
    });

    it("calculates XP needed from mid-level", () => {
      expect(calculateXPToNextLevel(250)).toBe(250);
    });

    it("calculates XP needed at level boundary", () => {
      expect(calculateXPToNextLevel(500)).toBe(500);
    });
  });

  describe("generateXPBar", () => {
    it("generates empty bar for 0 XP", () => {
      const bar = generateXPBar(0);
      expect(bar).toBe("[░░░░░░░░░░░░░░░░░░░░]");
    });

    it("generates full bar for 500 XP", () => {
      const bar = generateXPBar(500);
      expect(bar).toBe("[░░░░░░░░░░░░░░░░░░░░]"); // Starts over at new level
    });

    it("generates half bar for 250 XP", () => {
      const bar = generateXPBar(250);
      expect(bar).toContain("█");
      expect(bar).toContain("░");
      expect(bar.length).toBe(22); // [20 blocks]
    });
  });

  describe("calculateXPProgress", () => {
    it("returns 0% for 0 XP", () => {
      expect(calculateXPProgress(0)).toBe(0);
    });

    it("returns 50% for 250 XP", () => {
      expect(calculateXPProgress(250)).toBe(50);
    });

    it("returns 0% for 500 XP (level boundary)", () => {
      expect(calculateXPProgress(500)).toBe(0);
    });
  });
});
