"use client";

import React, { useState, useCallback } from "react";
import { Rnd } from "react-rnd";
import { cn } from "@/lib/utils";
import { GripHorizontal, Maximize2, Minimize2 } from "lucide-react";

interface DraggablePanelProps {
  children: React.ReactNode;
  title?: string;
  defaultWidth?: string | number;
  defaultHeight?: string | number;
  defaultX?: number;
  defaultY?: number;
  minWidth?: string | number;
  minHeight?: string | number;
  onClose?: () => void;
  className?: string;
}

export function DraggablePanel({
  children,
  title = "Panel",
  defaultWidth = 600,
  defaultHeight = 500,
  defaultX = 50,
  defaultY = 50,
  minWidth = 300,
  minHeight = 300,
  onClose,
  className,
}: DraggablePanelProps) {
  const [isMaximized, setIsMaximized] = useState(false);
  const [prevState, setPrevState] = useState<{
    width: string | number;
    height: string | number;
    x: number;
    y: number;
  } | null>(null);

  const handleMaximize = useCallback(() => {
    if (isMaximized && prevState) {
      setIsMaximized(false);
    } else {
      setPrevState({
        width: defaultWidth,
        height: defaultHeight,
        x: defaultX,
        y: defaultY,
      });
      setIsMaximized(true);
    }
  }, [isMaximized, prevState, defaultWidth, defaultHeight, defaultX, defaultY]);

  return (
    <Rnd
      default={{
        x: defaultX,
        y: defaultY,
        width: defaultWidth,
        height: defaultHeight,
      }}
      minWidth={minWidth}
      minHeight={minHeight}
      dragHandleClassName="drag-handle"
      bounds="window"
      style={isMaximized ? { zIndex: 9999 } : {}}
      {...(isMaximized && {
        x: 0,
        y: 0,
        width: "100vw",
        height: "100vh",
      })}
      disableDragging={isMaximized}
    >
      <div
        className={cn(
          "flex h-full w-full flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg",
          isMaximized && "rounded-none",
          className,
        )}
      >
        {/* Header */}
        <div className="drag-handle flex cursor-move items-center justify-between gap-3 border-b bg-gradient-to-r from-gray-50 to-white p-4 transition-colors hover:bg-gray-100">
          <div className="flex flex-1 items-center gap-2">
            <GripHorizontal className="h-4 w-4 text-gray-400" />
            <h3 className="font-semibold text-gray-800">{title}</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleMaximize}
              className="rounded p-1.5 transition-colors hover:bg-gray-200"
              title={isMaximized ? "Restore" : "Maximize"}
            >
              {isMaximized ? (
                <Minimize2 className="h-4 w-4 text-gray-600" />
              ) : (
                <Maximize2 className="h-4 w-4 text-gray-600" />
              )}
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="rounded p-1.5 transition-colors hover:bg-red-100"
                title="Close"
              >
                <svg
                  className="h-4 w-4 text-gray-600 hover:text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto bg-white">{children}</div>
      </div>
    </Rnd>
  );
}
