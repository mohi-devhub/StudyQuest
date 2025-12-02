"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import FeatureCard from "@/components/FeatureCard";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white">
      {/* Hero Section with Waitlist */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ 
          duration: 0.6,
          ease: [0.22, 1, 0.36, 1] // Custom easing
        }}
        className="container mx-auto px-6 py-12 md:py-20"
        style={{ transform: 'translateZ(0)' }} // Hardware acceleration
      >
        <div className="max-w-4xl mx-auto text-center">
          {/* Title with blinking cursor */}
          <motion.h1 
            className="text-4xl md:text-6xl font-bold mb-6"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="inline-block">StudyQuest</span>
            <span className="inline-block animate-blink ml-1">_</span>
          </motion.h1>

          {/* Tagline */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="text-lg md:text-xl text-terminal-gray mb-4"
            style={{ transform: 'translateZ(0)' }}
          >
            // Your AI-Powered Adaptive Learning Platform
          </motion.p>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="text-sm md:text-base text-terminal-muted max-w-2xl mx-auto mb-12"
            style={{ transform: 'translateZ(0)' }}
          >
            Master any subject with personalized AI-generated study materials,
            adaptive quizzes, and gamified progress tracking.
          </motion.p>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="flex justify-center"
          >
            <Link href="/login">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="border-2 border-terminal-white bg-terminal-white text-terminal-black px-10 py-5 font-mono text-xl font-bold hover:bg-terminal-black hover:text-terminal-white transition-all duration-200"
                style={{ transform: 'translateZ(0)' }}
              >
                &gt; BEGIN YOUR QUEST_
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Why It's Unique Section */}
      <section className="container mx-auto px-6 py-16 border-t border-terminal-gray">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="text-2xl md:text-3xl font-bold text-center mb-12"
          style={{ transform: 'translateZ(0)' }}
        >
          // WHY_STUDYQUEST
        </motion.h2>

        <div className="max-w-4xl mx-auto space-y-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.0, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-xl font-bold mb-3 text-terminal-white">
              &gt; Truly Adaptive AI
            </h3>
            <p className="text-terminal-gray">
              Unlike static learning platforms, StudyQuest uses advanced AI to generate personalized content that adapts to your learning style and pace. Every quiz, every note, tailored just for you.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.1, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-xl font-bold mb-3 text-terminal-white">
              &gt; Learn Anything, Anytime
            </h3>
            <p className="text-terminal-gray">
              From programming to philosophy, from calculus to cooking - if you can think it, you can learn it. No pre-made courses, no limitations. Just pure, on-demand knowledge.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-xl font-bold mb-3 text-terminal-white">
              &gt; Gamification That Actually Works
            </h3>
            <p className="text-terminal-gray">
              Earn XP, level up, and compete on leaderboards. But unlike other platforms, our gamification is designed to enhance learning, not distract from it. Every point earned represents real knowledge gained.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-16 border-t border-terminal-gray">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="text-2xl md:text-3xl font-bold text-center mb-12"
          style={{ transform: 'translateZ(0)' }}
        >
          // KEY_FEATURES
        </motion.h2>

        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            title="AI-Powered Learning"
            description="Generate personalized study notes and quizzes on any topic using advanced AI. Adaptive difficulty ensures you're always challenged at the right level."
            icon="🤖"
            delay={1.4}
          />

          <FeatureCard
            title="Progress Tracking"
            description="Monitor your learning journey with detailed analytics. Track XP, levels, and performance across all topics in real-time."
            icon="📊"
            delay={1.5}
          />

          <FeatureCard
            title="Gamification"
            description="Earn XP, level up, and unlock badges as you learn. Stay motivated with achievements and compete on the leaderboard."
            icon="🎮"
            delay={1.6}
          />
        </div>
      </section>

      {/* FAQ Section */}
      <section className="container mx-auto px-6 py-16 border-t border-terminal-gray">
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.2, duration: 0.5 }}
          className="text-2xl md:text-3xl font-bold text-center mb-12"
        >
          // FREQUENTLY_ASKED_QUESTIONS
        </motion.h2>

        <div className="max-w-3xl mx-auto space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.3, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-lg font-bold mb-2 text-terminal-white">
              &gt; How do I get started?
            </h3>
            <p className="text-terminal-gray text-sm">
              Simply sign up for a free account and start learning immediately. No credit card required for the free tier.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.4, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-lg font-bold mb-2 text-terminal-white">
              &gt; Will it be free?
            </h3>
            <p className="text-terminal-gray text-sm">
              StudyQuest has a free tier with core features, and a premium tier with advanced AI capabilities, unlimited quizzes, and priority support.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.5, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-lg font-bold mb-2 text-terminal-white">
              &gt; What subjects can I study?
            </h3>
            <p className="text-terminal-gray text-sm">
              Literally anything! Our AI can generate study materials on any topic you can think of - from programming and mathematics to history, languages, and creative skills.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.6, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-lg font-bold mb-2 text-terminal-white">
              &gt; How does the adaptive learning work?
            </h3>
            <p className="text-terminal-gray text-sm">
              Our AI analyzes your performance, learning patterns, and preferences to adjust difficulty levels, recommend topics, and generate personalized content that matches your current skill level.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 2.7, duration: 0.5 }}
            className="border border-terminal-gray p-6"
          >
            <h3 className="text-lg font-bold mb-2 text-terminal-white">
              &gt; Is my data private?
            </h3>
            <p className="text-terminal-gray text-sm">
              Absolutely. We take privacy seriously. We never sell your data, and all learning progress is encrypted and secure.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="container mx-auto px-6 py-12 border-t border-terminal-gray">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4, duration: 0.5 }}
          className="max-w-4xl mx-auto"
        >
          <div className="flex flex-col items-center gap-4">
            {/* Version Info */}
            <div className="text-center text-terminal-muted text-sm">
              <p>StudyQuest v1.0</p>
              <p className="mt-1">// Monochrome Terminal Edition</p>
            </div>

            {/* Copyright */}
            <div className="text-center text-terminal-muted text-xs">
              <p>&copy; 2025 StudyQuest. All rights reserved.</p>
            </div>
          </div>
        </motion.div>
      </footer>
    </div>
  );
}
