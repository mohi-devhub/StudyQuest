"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState, useCallback } from "react";

interface Toast {
  id: string;
  message: string;
  xp?: number;
  type: "xp" | "info" | "success" | "error";
}

interface XPToastProps {
  toast: Toast;
  onDismiss: (id: string) => void;
}

function XPToast({ toast, onDismiss }: XPToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id);
    }, 2000);

    return () => clearTimeout(timer);
  }, [toast.id, onDismiss]);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20, x: "-50%" }}
      animate={{ opacity: 1, y: 0, x: "-50%" }}
      exit={{ opacity: 0, y: -20, x: "-50%" }}
      transition={{ duration: 0.3 }}
      className="fixed top-8 left-1/2 z-50 bg-terminal-black border border-terminal-gray px-6 py-3 font-mono"
    >
      <div className="flex items-center space-x-3">
        {toast.type === "xp" && toast.xp && (
          <>
            <motion.span
              initial={{ scale: 1 }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5 }}
              className="text-terminal-white text-xl font-bold"
            >
              +{toast.xp}
            </motion.span>
            <span className="text-terminal-gray">XP</span>
            <span className="text-terminal-white">|</span>
          </>
        )}
        <span className="text-terminal-white">{toast.message}</span>
      </div>
    </motion.div>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  onDismiss: (id: string) => void;
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  return (
    <AnimatePresence mode="popLayout">
      {toasts.map((toast, index) => (
        <motion.div
          key={toast.id}
          style={{
            position: "fixed",
            top: `${32 + index * 80}px`,
            left: "50%",
            zIndex: 50,
          }}
        >
          <XPToast toast={toast} onDismiss={onDismiss} />
        </motion.div>
      ))}
    </AnimatePresence>
  );
}

let toastCounter = 0;

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback(
    (message: string, xp?: number, type: Toast["type"] = "info") => {
      const id = `toast-${Date.now()}-${toastCounter++}`;
      const newToast: Toast = { id, message, xp, type };
      setToasts((prev) => [...prev, newToast]);
    },
    [],
  );

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return { showToast, toasts, dismissToast };
}
