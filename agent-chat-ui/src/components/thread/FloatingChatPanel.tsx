"use client";

import React, { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { DraggablePanel } from "./DraggablePanel";

interface FloatingChatPanelProps {
  children: React.ReactNode;
  title?: string;
  defaultOpen?: boolean;
  onClose?: () => void;
  className?: string;
}

export function FloatingChatPanel({
  children,
  title = "Chat",
  defaultOpen = true,
  onClose,
  className,
}: FloatingChatPanelProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  const handleClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-50"
        >
          <DraggablePanel
            title={title}
            onClose={handleClose}
            className={className}
            defaultWidth={600}
            defaultHeight={700}
            defaultX={window.innerWidth - 650}
            defaultY={50}
          >
            {children}
          </DraggablePanel>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
