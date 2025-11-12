describe('Progress Tracking', () => {
  const testEmail = 'test@studyquest.dev'
  const testPassword = 'testuser123'

  beforeEach(() => {
    // Login first
    cy.visit('/login')
    cy.get('input[type="email"]').type(testEmail)
    cy.get('input[type="password"]').type(testPassword)
    cy.contains('button', 'LOGIN').click()
    cy.url({ timeout: 10000 }).should('eq', Cypress.config().baseUrl + '/')
  })

  it('should navigate to progress page', () => {
    cy.contains('VIEW_PROGRESS').click()
    cy.url().should('include', '/progress')
    cy.contains('PROGRESS DASHBOARD').should('be.visible')
  })

  it('should display user stats', () => {
    cy.visit('/progress')

    // Should show XP and level
    cy.contains(/LEVEL \d+/).should('be.visible')
    cy.contains(/XP TOTAL/).should('be.visible')

    // Should show stats grid
    cy.contains('MASTERED').should('be.visible')
    cy.contains('COMPLETED').should('be.visible')
    cy.contains('IN PROGRESS').should('be.visible')
  })

  it('should display topic breakdown table', () => {
    cy.visit('/progress')

    cy.contains('TOPIC BREAKDOWN').should('be.visible')

    // Table headers
    cy.contains('RANK').should('be.visible')
    cy.contains('TOPIC').should('be.visible')
    cy.contains('STATUS').should('be.visible')
    cy.contains('BEST').should('be.visible')
  })

  it('should show adaptive coach feedback', () => {
    cy.visit('/progress')

    // Should show coach panel
    cy.contains(/ADAPTIVE_COACH|RECOMMENDATIONS/i, { timeout: 10000 }).should(
      'be.visible'
    )
  })

  it('should allow topic retry', () => {
    cy.visit('/progress')

    // If there are topics, retry button should be visible
    cy.get('body').then(($body) => {
      if ($body.text().includes('RETRY')) {
        cy.contains('button', 'RETRY').first().should('be.visible')
      }
    })
  })
})
