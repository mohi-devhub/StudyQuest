describe('Authentication Flow', () => {
  const testEmail = 'test@studyquest.dev'
  const testPassword = 'testuser123'

  beforeEach(() => {
    cy.visit('/login')
  })

  it('should display login page correctly', () => {
    cy.contains('LOGIN()').should('be.visible')
    cy.get('input[type="email"]').should('be.visible')
    cy.get('input[type="password"]').should('be.visible')
  })

  it('should show error for invalid credentials', () => {
    cy.get('input[type="email"]').type('invalid@email.com')
    cy.get('input[type="password"]').type('wrongpassword')
    cy.contains('button', 'LOGIN').click()

    // Should show error message
    cy.contains(/error|invalid/i, { timeout: 10000 }).should('be.visible')
  })

  it('should successfully login with valid credentials', () => {
    cy.get('input[type="email"]').type(testEmail)
    cy.get('input[type="password"]').type(testPassword)
    cy.contains('button', 'LOGIN').click()

    // Should redirect to dashboard
    cy.url({ timeout: 10000 }).should('eq', Cypress.config().baseUrl + '/')
    cy.contains('DASHBOARD', { timeout: 10000 }).should('be.visible')
  })

  it('should navigate to signup page', () => {
    cy.contains('Sign up').click()
    cy.url().should('include', '/signup')
    cy.contains('SIGNUP()').should('be.visible')
  })
})
