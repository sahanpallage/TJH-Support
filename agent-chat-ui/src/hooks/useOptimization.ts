/**
 * useDebounce Hook - Debounces a value with a specified delay
 * Prevents excessive function calls during rapid updates (e.g., typing)
 */
import { useEffect, useState } from "react";

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

/**
 * useThrottle Hook - Throttles a callback function
 * Useful for scroll events, resize events, or rapid API calls
 */
export function useThrottle<T extends (...args: never[]) => void>(
  callback: T,
  delay: number = 300,
): (...args: Parameters<T>) => void {
  const [lastRun, setLastRun] = useState(Date.now());

  return (...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastRun >= delay) {
      callback(...args);
      setLastRun(now);
    }
  };
}

/**
 * usePrevious Hook - Keep track of previous value
 * Useful for comparing before/after states
 */
export function usePrevious<T>(value: T): T | undefined {
  const [prev, setPrev] = useState<T | undefined>();

  useEffect(() => {
    setPrev(value);
  }, [value]);

  return prev;
}

/**
 * useLocalStorage Hook - Persist state in localStorage
 * Useful for caching user preferences and chat history
 */
export function useLocalStorage<T>(
  key: string,
  initialValue: T,
): [T, (value: T | ((val: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore =
        value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}

/**
 * useAsync Hook - Handle async operations with loading/error states
 * Reduces boilerplate for API calls
 */
export function useAsync<T, E = string>(
  asyncFunction: () => Promise<T>,
  immediate: boolean = true,
) {
  const [status, setStatus] = useState<
    "idle" | "pending" | "success" | "error"
  >("idle");
  const [value, setValue] = useState<T | null>(null);
  const [error, setError] = useState<E | null>(null);

  const execute = async () => {
    setStatus("pending");
    setValue(null);
    setError(null);
    try {
      const response = await asyncFunction();
      setValue(response);
      setStatus("success");
      return response;
    } catch (error) {
      setError(error as E);
      setStatus("error");
    }
  };

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, []);

  return { execute, status, value, error };
}
