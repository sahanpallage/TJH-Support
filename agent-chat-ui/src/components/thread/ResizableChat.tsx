"use client";

import React, { useState, useRef, useEffect } from "react";
import { cn } from "@/lib/utils";
import { GripHorizontal } from "lucide-react";

interface ResizableChatProps {
  children: React.ReactNode;
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
}

export function ResizableChat({
  children,
  defaultWidth = 600,
  minWidth = 300,
  maxWidth = 1000,
}: ResizableChatProps) {
  const [width, setWidth] = useState(defaultWidth);
  const [isDragging, setIsDragging] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = () => {
    setIsDragging(true);
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;

      const container = containerRef.current;
      const rect = container.getBoundingClientRect();

      // Calculate new width based on mouse position
      const newWidth = rect.right - e.clientX;

      // Constrain width between min and max
      if (newWidth >= minWidth && newWidth <= maxWidth) {
        setWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);

    return () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, minWidth, maxWidth]);

  return (
    <div className="flex h-screen w-full">
      {/* Main content area */}
      <div className="flex-1 overflow-hidden bg-gray-50" />

      {/* Resizable chat panel */}
      <div
        ref={containerRef}
        style={{ width }}
        className="relative flex flex-col border-l border-gray-200 bg-white shadow-lg"
      >
        {/* Resize handle on the left */}
        <div
          onMouseDown={handleMouseDown}
          className={cn(
            "group absolute top-0 left-0 h-full w-1.5 cursor-col-resize transition-colors",
            isDragging ? "bg-blue-500" : "bg-gray-300 hover:bg-blue-400",
          )}
          title="Drag to resize chat panel"
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 transition-opacity group-hover:opacity-100">
            <GripHorizontal className="h-5 w-5 text-blue-500" />
          </div>
        </div>

        {/* Chat content */}
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
