"use client";

import { motion } from "framer-motion";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  delay?: number;
}

export default function FeatureCard({
  title,
  description,
  icon,
  delay = 0,
}: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ 
        delay, 
        duration: 0.5,
        ease: [0.22, 1, 0.36, 1] // Custom easing for smooth animation
      }}
      whileHover={{ 
        scale: 1.02,
        borderColor: "#ffffff",
        transition: { duration: 0.2 }
      }}
      className="border border-terminal-gray p-6 bg-terminal-black transition-colors duration-200"
      style={{ 
        backgroundColor: "#000000",
        transform: 'translateZ(0)', // Hardware acceleration
        willChange: 'transform'
      }}
    >
      {/* Icon */}
      <motion.div 
        className="text-4xl mb-4"
        whileHover={{ scale: 1.1, rotate: 5 }}
        transition={{ duration: 0.2 }}
      >
        {icon}
      </motion.div>

      {/* Title */}
      <h3 className="text-xl font-bold mb-3 text-terminal-white">{title}</h3>

      {/* Description */}
      <p className="text-terminal-gray text-sm leading-relaxed">
        {description}
      </p>
    </motion.div>
  );
}
