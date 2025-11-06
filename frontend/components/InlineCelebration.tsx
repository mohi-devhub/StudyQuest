'use client'

import { motion } from 'framer-motion'

interface InlineCelebrationProps {
  message: string
  symbol?: string
}

export default function InlineCelebration({ message, symbol = '★' }: InlineCelebrationProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.3 }}
      className="my-8 text-center"
    >
      {/* Top border */}
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="border-t border-white mb-4"
      />

      {/* Symbol */}
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ 
          type: 'spring',
          damping: 15,
          stiffness: 200,
          delay: 0.3 
        }}
        className="text-5xl mb-4"
      >
        {symbol}
      </motion.div>

      {/* Message */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="text-2xl font-bold text-white tracking-wider mb-4"
      >
        {message}
      </motion.div>

      {/* Bottom border */}
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: '100%' }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="border-t border-white mt-4"
      />
    </motion.div>
  )
}
