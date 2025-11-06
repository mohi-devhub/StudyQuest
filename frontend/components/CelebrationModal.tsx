'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface CelebrationModalProps {
  type: 'level' | 'badge'
  title: string
  message: string
  symbol?: string
  isOpen: boolean
  onClose: () => void
}

export default function CelebrationModal({
  type,
  title,
  message,
  symbol,
  isOpen,
  onClose,
}: CelebrationModalProps) {
  const [showContent, setShowContent] = useState(false)
  
  useEffect(() => {
    if (isOpen) {
      setShowContent(false)
      const timer = setTimeout(() => setShowContent(true), 300)
      
      // Auto-close after 5 seconds
      const closeTimer = setTimeout(onClose, 5000)
      
      return () => {
        clearTimeout(timer)
        clearTimeout(closeTimer)
      }
    }
  }, [isOpen, onClose])

  const borderLine = '─'.repeat(40)

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.9 }}
            transition={{ 
              type: 'spring',
              damping: 20,
              stiffness: 300
            }}
            className="relative border-2 border-white bg-black p-8 min-w-[400px] max-w-[600px]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Top border */}
            <div className="text-white font-mono text-xs mb-4 overflow-hidden whitespace-nowrap">
              {borderLine}
            </div>

            {/* Symbol (for badges) */}
            {symbol && type === 'badge' && (
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                transition={{ 
                  type: 'spring',
                  damping: 10,
                  stiffness: 100,
                  delay: 0.2 
                }}
                className="text-6xl text-center mb-6"
              >
                {symbol}
              </motion.div>
            )}

            {/* Title with typewriter effect */}
            <div className="text-center mb-4">
              {showContent ? (
                <TypewriterText 
                  text={title} 
                  className="text-3xl font-bold text-white tracking-wider"
                  speed={50}
                />
              ) : (
                <div className="h-12" /> // Placeholder
              )}
            </div>

            {/* Message */}
            {showContent && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: title.length * 0.05 + 0.2 }}
                className="text-center text-lg text-white mb-6"
              >
                {message}
              </motion.div>
            )}

            {/* Bottom border */}
            <div className="text-white font-mono text-xs mt-4 overflow-hidden whitespace-nowrap">
              {borderLine}
            </div>

            {/* Close hint */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2 }}
              className="text-center text-xs text-gray-500 mt-4"
            >
              Click anywhere to dismiss
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// Typewriter effect component
function TypewriterText({ 
  text, 
  className, 
  speed = 100 
}: { 
  text: string
  className?: string
  speed?: number 
}) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)

      return () => clearTimeout(timer)
    }
  }, [currentIndex, text, speed])

  return (
    <div className={className}>
      {displayedText}
      {currentIndex < text.length && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.5, repeat: Infinity }}
          className="ml-1"
        >
          _
        </motion.span>
      )}
    </div>
  )
}
