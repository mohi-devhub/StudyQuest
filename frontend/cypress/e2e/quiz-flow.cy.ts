describe("Quiz Flow", () => {
  const testEmail = "test@studyquest.dev";
  const testPassword = "testuser123";

  beforeEach(() => {
    // Login first
    cy.visit("/login");
    cy.get('input[type="email"]').type(testEmail);
    cy.get('input[type="password"]').type(testPassword);
    cy.contains("button", "LOGIN").click();
    cy.url({ timeout: 10000 }).should("eq", Cypress.config().baseUrl + "/");
  });

  it("should navigate to quiz page", () => {
    cy.contains("TAKE_QUIZ").click();
    cy.url().should("include", "/quiz");
    cy.contains("QUIZ_GENERATOR()").should("be.visible");
  });

  it("should show quiz generation options", () => {
    cy.visit("/quiz");
    cy.contains("FROM_SAVED_NOTES()").should("be.visible");
    cy.contains("UPLOAD_PDF()").should("be.visible");
    cy.contains("CUSTOM_TOPIC()").should("be.visible");
  });

  it("should generate quiz from custom topic", () => {
    cy.visit("/quiz");
    cy.contains("CUSTOM_TOPIC()").click();

    // Enter topic
    cy.get('input[type="text"]').type("JavaScript Arrays");
    cy.contains("button", "GENERATE_QUIZ").click();

    // Wait for quiz to generate
    cy.contains("QUESTION_1", { timeout: 30000 }).should("be.visible");

    // Answer questions
    cy.get("button")
      .contains(/^[A-D]\./)
      .first()
      .click();
    cy.contains("button", "NEXT").click();

    // Continue through quiz...
    cy.get("button")
      .contains(/^[A-D]\./)
      .first()
      .click();
  });

  it("should navigate from saved notes to quiz", () => {
    cy.visit("/quiz");
    cy.contains("FROM_SAVED_NOTES()").click();

    // Should show saved sessions or empty state
    cy.contains(/NO_SAVED_SESSIONS|TOPIC/i).should("be.visible");
  });

  it("should show file upload for PDF option", () => {
    cy.visit("/quiz");
    cy.contains("UPLOAD_PDF()").click();

    cy.contains("SELECT_PDF_FILE()").should("be.visible");
    cy.get('input[type="file"]').should("exist");
  });
});
