/**
 * Structured JSON logger for production-ready logging.
 * Replaces console.log statements with structured, contextual logging.
 */

interface LogContext {
  [key: string]: string | number | boolean | null | undefined | object;
}

interface LogEntry {
  timestamp: string;
  level: string;
  logger: string;
  message: string;
  context?: LogContext;
}

type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR";

class StructuredLogger {
  private name: string;
  private globalContext: LogContext = {};

  constructor(name: string) {
    this.name = name;
  }

  /**
   * Set global context that will be included in all log entries
   */
  setGlobalContext(context: LogContext): void {
    this.globalContext = { ...this.globalContext, ...context };
  }

  /**
   * Clear global context
   */
  clearGlobalContext(): void {
    this.globalContext = {};
  }

  /**
   * Internal logging method
   */
  private log(level: LogLevel, message: string, context?: LogContext): void {
    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      logger: this.name,
      message,
    };

    // Merge global context with local context
    const mergedContext = { ...this.globalContext, ...context };
    if (Object.keys(mergedContext).length > 0) {
      logEntry.context = mergedContext;
    }

    // In production, send to logging service
    if (process.env.NODE_ENV === "production") {
      this.sendToLoggingService(logEntry);
    } else {
      // Development: pretty print to console
      this.logToConsole(level, logEntry);
    }
  }

  /**
   * Log to console in development mode
   */
  private logToConsole(level: LogLevel, logEntry: LogEntry): void {
    const formattedLog = JSON.stringify(logEntry, null, 2);

    switch (level) {
      case "DEBUG":
        console.debug(formattedLog);
        break;
      case "INFO":
        console.info(formattedLog);
        break;
      case "WARN":
        console.warn(formattedLog);
        break;
      case "ERROR":
        console.error(formattedLog);
        break;
    }
  }

  /**
   * Send logs to external logging service in production
   * This can be integrated with services like Datadog, LogRocket, Sentry, etc.
   */
  private sendToLoggingService(logEntry: LogEntry): void {
    // TODO: Integrate with logging service
    // Example integrations:
    // - Datadog: datadogLogs.logger.log(logEntry.message, logEntry)
    // - LogRocket: LogRocket.log(logEntry)
    // - Sentry: Sentry.captureMessage(logEntry.message, { extra: logEntry.context })

    // For now, still log to console in production
    console.log(JSON.stringify(logEntry));
  }

  /**
   * Log debug message with optional context
   *
   * @param message - Debug message
   * @param context - Additional context (e.g., { userId: "123", page: "quiz" })
   */
  debug(message: string, context?: LogContext): void {
    this.log("DEBUG", message, context);
  }

  /**
   * Log info message with optional context
   *
   * @param message - Info message
   * @param context - Additional context (e.g., { userId: "123", action: "login" })
   */
  info(message: string, context?: LogContext): void {
    this.log("INFO", message, context);
  }

  /**
   * Log warning message with optional context
   *
   * @param message - Warning message
   * @param context - Additional context (e.g., { userId: "123", issue: "slow_response" })
   */
  warn(message: string, context?: LogContext): void {
    this.log("WARN", message, context);
  }

  /**
   * Log error message with optional context
   *
   * @param message - Error message
   * @param context - Additional context (e.g., { userId: "123", error: "api_timeout" })
   */
  error(message: string, context?: LogContext): void {
    this.log("ERROR", message, context);
  }
}

/**
 * Create a structured logger instance
 *
 * @param name - Logger name (typically the component or module name)
 * @returns StructuredLogger instance
 *
 * @example
 * const logger = createLogger('QuizPage');
 * logger.info('Quiz started', { userId: '123', topic: 'Python' });
 */
export function createLogger(name: string): StructuredLogger {
  return new StructuredLogger(name);
}

/**
 * Default logger instance for general use
 */
export const logger = createLogger("App");
