"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { createLogger } from "@/lib/logger";

const logger = createLogger("TerminalError");

interface TerminalErrorProps {
  error: string;
  details?: string;
  onRetry?: () => void;
  dismissible?: boolean;
}

export default function TerminalError({
  error,
  details,
  onRetry,
  dismissible = false,
}: TerminalErrorProps) {
  const [dismissed, setDismissed] = useState(false);
  const [timestamp] = useState(new Date().toISOString());

  useEffect(() => {
    // Log error with structured logging
    logger.error("Terminal error displayed", { error, details, timestamp });
  }, [error, details, timestamp]);

  if (dismissed) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="border-2 border-terminal-white bg-terminal-black p-6 font-mono"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center space-x-2 mb-2">
            <div className="text-2xl">✕</div>
            <div className="text-xl font-bold">ERROR</div>
          </div>
          <div className="text-terminal-gray text-xs">
            {timestamp.split("T")[0]} {timestamp.split("T")[1].split(".")[0]}
          </div>
        </div>
        {dismissible && (
          <button
            onClick={() => setDismissed(true)}
            className="text-terminal-gray hover:text-terminal-white transition-colors"
            aria-label="Dismiss error"
          >
            [DISMISS]
          </button>
        )}
      </div>

      {/* Error Message */}
      <div className="mb-4">
        <div className="text-terminal-gray text-xs mb-1">MESSAGE:</div>
        <div className="text-terminal-white font-semibold">{error}</div>
      </div>

      {/* Details */}
      {details && (
        <div className="mb-4">
          <div className="text-terminal-gray text-xs mb-1">DETAILS:</div>
          <div className="text-terminal-gray text-sm font-mono bg-terminal-white bg-opacity-5 p-3 border border-terminal-white border-opacity-20">
            {details}
          </div>
        </div>
      )}

      {/* Stack trace hint */}
      <div className="text-terminal-gray text-xs mb-4">
        → Check browser console for full error stack trace
      </div>

      {/* Actions */}
      <div className="flex items-center space-x-4">
        {onRetry && (
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onRetry}
            className="px-6 py-2 border border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-all"
          >
            RETRY()
          </motion.button>
        )}
        <button
          onClick={() => window.location.reload()}
          className="px-6 py-2 border border-terminal-white border-opacity-30 hover:border-opacity-100 transition-all text-terminal-gray hover:text-terminal-white"
        >
          RELOAD_PAGE()
        </button>
      </div>

      {/* Corner decorations */}
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-terminal-white opacity-50" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-terminal-white opacity-50" />
    </motion.div>
  );
}

/**
 * Inline error display for smaller contexts
 */
export function InlineError({ message }: { message: string }) {
  return (
    <div className="inline-flex items-center space-x-2 text-terminal-gray text-sm font-mono border border-terminal-white border-opacity-30 px-3 py-1">
      <span>✕</span>
      <span>ERROR:</span>
      <span>{message}</span>
    </div>
  );
}

/**
 * Full-page error display
 */
export function FullPageError({
  error,
  details,
}: {
  error: string;
  details?: string;
}) {
  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center p-8">
      <div className="max-w-2xl w-full">
        <TerminalError
          error={error}
          details={details}
          onRetry={() => window.location.reload()}
        />
      </div>
    </div>
  );
}
