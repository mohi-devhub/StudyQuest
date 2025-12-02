"use client";

import { motion, useMotionValue, useSpring } from "framer-motion";
import { useEffect } from "react";

interface XPProgressBarProps {
  currentXP: number;
  level: number;
}

export default function XPProgressBar({
  currentXP,
  level,
}: XPProgressBarProps) {
  // XP needed for next level: level * 500
  const xpForNextLevel = level * 500;
  const xpProgress = ((currentXP % 500) / 500) * 100;

  // Animated progress value
  const motionProgress = useMotionValue(0);
  const springProgress = useSpring(motionProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001,
  });

  useEffect(() => {
    motionProgress.set(xpProgress);
  }, [xpProgress, motionProgress]);

  return (
    <div className="border border-terminal-white p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="text-terminal-gray text-sm">// CURRENT_LEVEL</div>
          <motion.div
            key={level}
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.5 }}
            className="text-3xl font-bold"
          >
            LEVEL {level}
          </motion.div>
        </div>
        <div className="text-right">
          <div className="text-terminal-gray text-sm">// TOTAL_XP</div>
          <motion.div
            key={currentXP}
            initial={{ scale: 1 }}
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 0.3 }}
            className="text-2xl font-bold"
          >
            {currentXP} XP
          </motion.div>
        </div>
      </div>

      <div className="relative">
        <div className="text-terminal-gray text-xs mb-2">
          {currentXP % 500} / {xpForNextLevel % 500 || 500} XP to Level{" "}
          {level + 1}
        </div>

        {/* Progress bar background */}
        <div
          className="h-8 border border-terminal-white relative overflow-hidden"
          role="progressbar"
          aria-valuenow={xpProgress}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          {/* Progress fill with smooth animation */}
          <motion.div
            style={{
              width: springProgress.get() === 0 ? `${xpProgress}%` : undefined,
            }}
            animate={{ width: `${xpProgress}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full bg-terminal-white"
          />

          {/* Percentage text */}
          <div className="absolute inset-0 flex items-center justify-center text-xs font-bold mix-blend-difference">
            {(xpProgress ?? 0).toFixed(1)}%
          </div>
        </div>

        {/* Grid pattern overlay */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <div
            className="h-full w-full"
            style={{
              backgroundImage:
                "repeating-linear-gradient(90deg, #fff 0px, #fff 1px, transparent 1px, transparent 20px)",
            }}
          />
        </div>
      </div>
    </div>
  );
}
