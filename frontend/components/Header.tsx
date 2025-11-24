import { motion } from "framer-motion";
import Link from "next/link";
import { BlinkingCursor } from "./TypingText";

export default function Header() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-b border-terminal-white pb-4"
    >
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight inline-flex items-baseline">
            StudyQuest
            <BlinkingCursor className="ml-1 text-3xl" />
          </h1>
          <p className="text-terminal-gray text-sm mt-1">
            // Developer Dashboard
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <Link
            href="/progress"
            className="border border-terminal-gray px-4 py-2 hover:border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors text-sm"
          >
            📊 PROGRESS
          </Link>
          <Link
            href="/achievements"
            className="border border-terminal-gray px-4 py-2 hover:border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors text-sm"
          >
            [★] ACHIEVEMENTS
          </Link>
          <Link
            href="/leaderboard"
            className="border border-terminal-gray px-4 py-2 hover:border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors text-sm"
          >
            🏆 LEADERBOARD
          </Link>
          <Link
            href="/profile"
            className="border border-terminal-gray px-4 py-2 hover:border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors text-sm"
          >
            👤 PROFILE
          </Link>
          <div className="text-right">
            <div className="text-terminal-gray text-xs">SYSTEM_STATUS</div>
            <div className="text-terminal-white font-mono">
              <span className="inline-block w-2 h-2 bg-terminal-white mr-2 animate-pulse"></span>
              ONLINE
            </div>
          </div>
        </div>
      </div>
    </motion.header>
  );
}
