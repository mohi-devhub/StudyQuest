"use client";

import { useEffect } from "react";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center p-8 font-mono">
      <div className="border border-terminal-white p-8 max-w-md w-full">
        <div className="text-terminal-gray text-xs mb-2">// RUNTIME_ERROR</div>
        <h2 className="text-2xl font-bold mb-4">[!] SOMETHING_WENT_WRONG</h2>
        <p className="text-terminal-gray text-sm mb-6 break-all">
          {error.message || "An unexpected error occurred."}
        </p>
        {error.digest && (
          <p className="text-terminal-gray text-xs mb-6">
            digest: {error.digest}
          </p>
        )}
        <button
          onClick={reset}
          className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors"
        >
          RETRY()
        </button>
      </div>
    </div>
  );
}
