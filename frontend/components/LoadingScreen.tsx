'use client'

import { motion } from 'framer-motion'

export default function LoadingScreen() {
  return (
    <div className="min-h-screen bg-terminal-black flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center"
      >
        {/* Animated loading bars */}
        <div className="flex items-end justify-center space-x-2 mb-8">
          {[...Array(5)].map((_, i) => (
            <motion.div
              key={i}
              initial={{ height: 8 }}
              animate={{ 
                height: [8, 32, 8],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: i * 0.1,
                ease: 'easeInOut'
              }}
              className="w-2 bg-terminal-white"
            />
          ))}
        </div>

        {/* Loading text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ 
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
          className="text-terminal-white text-xl font-mono"
        >
          LOADING<span className="animate-pulse">...</span>
        </motion.div>

        {/* Subtext */}
        <div className="mt-4 text-terminal-gray text-sm">
          // Loading your progress...
        </div>
      </motion.div>
    </div>
  )
}
