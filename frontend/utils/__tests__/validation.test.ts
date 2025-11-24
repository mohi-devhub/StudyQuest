import {
  validateTopic,
  validatePDFFile,
  validateEmail,
  validatePassword,
  validateUsername,
} from "../validation";

describe("Validation Utilities", () => {
  describe("validateTopic", () => {
    it("validates correct topic", () => {
      expect(validateTopic("JavaScript")).toEqual({ valid: true });
    });

    it("rejects empty topic", () => {
      expect(validateTopic("")).toEqual({
        valid: false,
        error: "Please enter a topic",
      });
    });

    it("rejects topic that is too long", () => {
      const longTopic = "a".repeat(51);
      expect(validateTopic(longTopic)).toEqual({
        valid: false,
        error: "Topic must be 50 characters or less",
      });
    });
  });

  describe("validatePDFFile", () => {
    it("validates correct PDF file", () => {
      const file = new File(["content"], "test.pdf", {
        type: "application/pdf",
      });
      expect(validatePDFFile(file)).toEqual({ valid: true });
    });

    it("rejects non-PDF file", () => {
      const file = new File(["content"], "test.txt", { type: "text/plain" });
      expect(validatePDFFile(file)).toEqual({
        valid: false,
        error: "Please select a PDF file",
      });
    });

    it("rejects file that is too large", () => {
      const largeContent = new Array(11 * 1024 * 1024).join("a");
      const file = new File([largeContent], "test.pdf", {
        type: "application/pdf",
      });
      expect(validatePDFFile(file)).toEqual({
        valid: false,
        error: "File size must be less than 10MB",
      });
    });
  });

  describe("validateEmail", () => {
    it("validates correct email", () => {
      expect(validateEmail("test@example.com")).toEqual({ valid: true });
    });

    it("rejects empty email", () => {
      expect(validateEmail("")).toEqual({
        valid: false,
        error: "Email is required",
      });
    });

    it("rejects invalid email format", () => {
      expect(validateEmail("invalid-email")).toEqual({
        valid: false,
        error: "Please enter a valid email",
      });
    });
  });

  describe("validatePassword", () => {
    it("validates correct password", () => {
      expect(validatePassword("password123")).toEqual({ valid: true });
    });

    it("rejects empty password", () => {
      expect(validatePassword("")).toEqual({
        valid: false,
        error: "Password is required",
      });
    });

    it("rejects password that is too short", () => {
      expect(validatePassword("short")).toEqual({
        valid: false,
        error: "Password must be at least 8 characters",
      });
    });
  });

  describe("validateUsername", () => {
    it("validates correct username", () => {
      expect(validateUsername("user123")).toEqual({ valid: true });
    });

    it("rejects empty username", () => {
      expect(validateUsername("")).toEqual({
        valid: false,
        error: "Username is required",
      });
    });

    it("rejects username that is too short", () => {
      expect(validateUsername("ab")).toEqual({
        valid: false,
        error: "Username must be at least 3 characters",
      });
    });

    it("rejects username that is too long", () => {
      const longUsername = "a".repeat(21);
      expect(validateUsername(longUsername)).toEqual({
        valid: false,
        error: "Username must be 20 characters or less",
      });
    });

    it("rejects username with invalid characters", () => {
      expect(validateUsername("user@123")).toEqual({
        valid: false,
        error:
          "Username can only contain letters, numbers, hyphens, and underscores",
      });
    });
  });
});
