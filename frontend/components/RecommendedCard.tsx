import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { QuizDifficulty } from "@/types/enums";

interface Recommendation {
  topic: string;
  reason: string;
  priority: string;
  category: string;
  current_score: number | null;
  recommended_difficulty: string;
  estimated_xp_gain: number;
  urgency: string;
}

interface RecommendedCardProps {
  recommendation: Recommendation;
}

export default function RecommendedCard({
  recommendation,
}: RecommendedCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const router = useRouter();

  const handleStartStudy = () => {
    router.push(
      `/study?topic=${encodeURIComponent(recommendation.topic)}&difficulty=${recommendation.recommended_difficulty}&autoStart=true`,
    );
  };

  const getPriorityBorder = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "border-2";
      case "medium":
        return "border";
      default:
        return "border";
    }
  };

  const getDifficultyLabel = (difficulty: string) => {
    const labels: { [key in QuizDifficulty]: string } = {
      [QuizDifficulty.EASY]: "█░░░",
      [QuizDifficulty.MEDIUM]: "██░░",
      [QuizDifficulty.HARD]: "███░",
      [QuizDifficulty.EXPERT]: "████",
    };
    return labels[difficulty.toLowerCase() as QuizDifficulty] || "░░░░";
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.01, transition: { duration: 0.1 } }}
      transition={{ duration: 0.2 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={`${getPriorityBorder(recommendation.priority)} border-terminal-white p-8 cursor-pointer relative overflow-hidden bg-terminal-black`}
    >
      {/* Removed background hover effect */}

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="text-terminal-gray text-xs mb-2 flex items-center space-x-2">
              <span>[{recommendation.priority.toUpperCase()}]</span>
              <span>·</span>
              <span>{recommendation.category}</span>
            </div>
            <h2 className="text-3xl font-bold mb-2">{recommendation.topic}</h2>
            <p className="text-terminal-gray">{recommendation.reason}</p>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 mb-6">
          <div className="border border-terminal-gray p-3">
            <div className="text-terminal-gray text-xs mb-1">// CURRENT_SCORE</div>
            <div className="text-xl font-bold">
              {recommendation.current_score !== null && recommendation.current_score !== undefined
                ? `${recommendation.current_score.toFixed(1)}%`
                : "[NEW]"}
            </div>
          </div>

          <div className="border border-terminal-gray p-3">
            <div className="text-terminal-gray text-xs mb-1">// DIFFICULTY</div>
            <div className="text-lg font-bold font-mono">
              {getDifficultyLabel(recommendation.recommended_difficulty)}
            </div>
            <div className="text-xs text-terminal-gray mt-1">
              {recommendation.recommended_difficulty.toUpperCase()}
            </div>
          </div>

          <div className="border border-terminal-gray p-3">
            <div className="text-terminal-gray text-xs mb-1">// EST_XP_GAIN</div>
            <div className="text-xl font-bold text-terminal-white">
              +{recommendation.estimated_xp_gain} XP
            </div>
          </div>

          <div className="border border-terminal-gray p-3">
            <div className="text-terminal-gray text-xs mb-1">// PRIORITY</div>
            <div className="text-sm font-bold">
              [{recommendation.priority.toUpperCase()}]
            </div>
            <div className="text-xs text-terminal-gray mt-1">
              {recommendation.category.replace(/_/g, ' ').toUpperCase()}
            </div>
          </div>
        </div>
        
        {/* Urgency Banner */}
        <div className="border-l-4 border-terminal-white bg-terminal-black bg-opacity-50 p-3 mb-6">
          <div className="text-xs text-terminal-gray mb-1">// WHY NOW?</div>
          <div className="text-sm">{recommendation.urgency}</div>
        </div>

        {/* Action Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleStartStudy}
          className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-8 py-4 hover:bg-terminal-white hover:text-terminal-black transition-all font-bold text-lg"
        >
          GENERATE_NOTES() →
        </motion.button>
      </div>

      {/* Corner decorations */}
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-terminal-white opacity-50" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-terminal-white opacity-50" />
    </motion.div>
  );
}
