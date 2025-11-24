describe("Full User Journey", () => {
  const testEmail = "test@studyquest.dev";
  const testPassword = "testuser123";

  it("should allow a user to login, take a quiz, and see their progress", () => {
    // 1. Login
    cy.visit("/login");
    cy.wait(1000); // Wait for the page to load
    cy.get('input[type="email"]').type(testEmail);
    cy.get('input[type="password"]').type(testPassword);
    cy.contains("button", "LOGIN").click();
    cy.url({ timeout: 10000 }).should("eq", Cypress.config().baseUrl + "/");
    cy.contains("DASHBOARD", { timeout: 10000 }).should("be.visible");

    // 2. Start a quiz from a recommended topic
    cy.contains("// NEXT_RECOMMENDED").should("be.visible");
    cy.get("body").then(($body) => {
      if ($body.find('button:contains("START_QUIZ")').length > 0) {
        cy.contains("button", "START_QUIZ").click();
      } else {
        cy.contains("TAKE_QUIZ").click();
        cy.contains("CUSTOM_TOPIC()").click();
        cy.get('input[type="text"]').type("React Hooks");
        cy.contains("button", "GENERATE_QUIZ").click();
      }
    });

    // 3. Complete the quiz
    cy.contains("QUESTION_1", { timeout: 30000 }).should("be.visible");

    for (let i = 0; i < 5; i++) {
      cy.get("button")
        .contains(/^[A-D]\./)
        .first()
        .click();
      cy.contains("button", "NEXT").click();
    }

    cy.contains("button", "FINISH").click();

    // 4. View quiz results and see XP gain
    cy.contains("QUIZ_COMPLETE", { timeout: 15000 }).should("be.visible");
    cy.contains(/[0-9]+ \/ [0-9]+/).should("be.visible");
    cy.contains(/\\+([0-9]+) XP/).should("be.visible");

    // 5. Return to Dashboard
    cy.contains("button", "CONTINUE").click();
    cy.url().should("eq", Cypress.config().baseUrl + "/");

    // 6. Navigate to Progress page and verify update
    cy.contains("VIEW_PROGRESS").click();
    cy.url().should("include", "/progress");
    cy.contains("PROGRESS DASHBOARD").should("be.visible");

    // Check for updated stats (this is a simple check, could be more specific)
    cy.contains(/LEVEL [0-9]+/).should("be.visible");
    cy.contains("React Hooks").should("be.visible");
  });
});
