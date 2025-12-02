/**
 * Validate topic input
 */
export function validateTopic(topic: string): {
  valid: boolean;
  error?: string;
} {
  if (!topic.trim()) {
    return { valid: false, error: "Please enter a topic" };
  }

  if (topic.length > 50) {
    return { valid: false, error: "Topic must be 50 characters or less" };
  }

  return { valid: true };
}

/**
 * Validate PDF file
 */
export function validatePDFFile(file: File): {
  valid: boolean;
  error?: string;
} {
  if (file.type !== "application/pdf") {
    return { valid: false, error: "Please select a PDF file" };
  }

  const maxSize = 10 * 1024 * 1024; // 10MB
  if (file.size > maxSize) {
    return { valid: false, error: "File size must be less than 10MB" };
  }

  return { valid: true };
}

/**
 * Validate name for waitlist
 */
export function validateName(name: string): {
  valid: boolean;
  error?: string;
} {
  const trimmedName = name.trim();
  
  if (!trimmedName) {
    return { valid: false, error: "Name is required" };
  }

  if (name.length > 100) {
    return { valid: false, error: "Name must be 100 characters or less" };
  }

  return { valid: true };
}

/**
 * Validate email format
 */
export function validateEmail(email: string): {
  valid: boolean;
  error?: string;
} {
  if (!email.trim()) {
    return { valid: false, error: "Email is required" };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, error: "Please enter a valid email" };
  }

  return { valid: true };
}

/**
 * Validate password strength
 */
export function validatePassword(password: string): {
  valid: boolean;
  error?: string;
} {
  if (!password) {
    return { valid: false, error: "Password is required" };
  }

  if (password.length < 8) {
    return { valid: false, error: "Password must be at least 8 characters" };
  }

  return { valid: true };
}

/**
 * Validate username
 */
export function validateUsername(username: string): {
  valid: boolean;
  error?: string;
} {
  if (!username.trim()) {
    return { valid: false, error: "Username is required" };
  }

  if (username.length < 3) {
    return { valid: false, error: "Username must be at least 3 characters" };
  }

  if (username.length > 20) {
    return { valid: false, error: "Username must be 20 characters or less" };
  }

  const usernameRegex = /^[a-zA-Z0-9_-]+$/;
  if (!usernameRegex.test(username)) {
    return {
      valid: false,
      error:
        "Username can only contain letters, numbers, hyphens, and underscores",
    };
  }

  return { valid: true };
}
