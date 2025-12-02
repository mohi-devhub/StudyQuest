# Design Document

## Overview

The landing page with waitlist functionality serves as the public entry point for StudyQuest. It introduces the platform to new visitors, showcases key features, and provides a mechanism for interested users to join a waitlist. The design maintains the existing monochrome terminal aesthetic while being accessible to users unfamiliar with the application.

The implementation consists of:
- A new frontend page component at the root route for unauthenticated users
- A waitlist form component with client-side validation
- A new backend API endpoint for waitlist submissions
- A new Supabase database table for storing waitlist entries
- Routing logic to show the landing page to unauthenticated users and redirect authenticated users to the dashboard

## Architecture

### Component Structure

```
Landing Page
├── Hero Section
│   ├── Title & Tagline
│   └── Blinking Cursor Animation
├── Features Section
│   ├── Feature Card 1: AI-Powered Learning
│   ├── Feature Card 2: Progress Tracking
│   └── Feature Card 3: Gamification
├── Waitlist Section
│   ├── Waitlist Form
│   │   ├── Name Input
│   │   ├── Email Input
│   │   └── Submit Button
│   └── Success/Error Messages
└── Footer
    ├── Login Link
    └── Version Info
```

### Data Flow

```
User Input → Client Validation → API Request → Backend Validation → Database Insert → Success Response → UI Update
                ↓                                      ↓
            Error Display                        Error Response
```

### Routing Logic

```
User visits "/" 
    ├── Authenticated? 
    │   ├── Yes → Redirect to Dashboard (/dashboard or existing home)
    │   └── No → Show Landing Page
    └── User clicks "Login" → Navigate to /login
```

## Components and Interfaces

### Frontend Components

#### LandingPage Component (`frontend/app/landing/page.tsx`)

Main landing page component that orchestrates all sections.

**Props:** None (root page component)

**State:**
- None (stateless presentation component)

**Responsibilities:**
- Render hero section with title and tagline
- Display feature cards
- Render waitlist form component
- Provide navigation to login page

#### WaitlistForm Component (`frontend/components/WaitlistForm.tsx`)

Form component for collecting waitlist entries.

**Props:** None

**State:**
```typescript
interface WaitlistFormState {
  name: string;
  email: string;
  loading: boolean;
  error: string | null;
  success: boolean;
}
```

**Responsibilities:**
- Manage form input state
- Validate user input (client-side)
- Submit data to backend API
- Display loading, success, and error states
- Reset form after successful submission

#### FeatureCard Component (`frontend/components/FeatureCard.tsx`)

Reusable component for displaying feature information.

**Props:**
```typescript
interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
  delay?: number; // For staggered animations
}
```

**Responsibilities:**
- Display feature information with consistent styling
- Animate on scroll/load

### Backend API

#### Waitlist Endpoint

**Route:** `POST /api/waitlist`

**Request Body:**
```typescript
{
  name: string;      // 1-100 characters, required
  email: string;     // Valid email format, required
}
```

**Response (Success - 201):**
```typescript
{
  success: true;
  message: string;
  id: string;        // UUID of created entry
}
```

**Response (Error - 400):**
```typescript
{
  success: false;
  error: string;
  details?: object;  // Validation errors
}
```

**Response (Error - 409):**
```typescript
{
  success: false;
  error: "Email already registered"
}
```

**Response (Error - 500):**
```typescript
{
  success: false;
  error: "Internal server error"
}
```

**Rate Limiting:** 5 requests per minute per IP address

**Validation Rules:**
- Name: Required, 1-100 characters, trimmed
- Email: Required, valid email format, lowercase, trimmed
- Duplicate check: Email must be unique in database

### API Client Function

**Location:** `frontend/utils/api.ts`

```typescript
export async function submitWaitlist(
  name: string, 
  email: string
): Promise<{ success: boolean; message?: string; error?: string }> {
  // Implementation details in tasks
}
```

## Data Models

### Waitlist Table Schema

**Table Name:** `waitlist`

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid_generate_v4() | Unique identifier |
| name | TEXT | NOT NULL | User's name |
| email | TEXT | NOT NULL, UNIQUE | User's email address |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Timestamp of entry creation |
| updated_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Timestamp of last update |

**Indexes:**
- Primary key index on `id`
- Unique index on `email` (for duplicate prevention)
- Index on `created_at` (for sorting/analytics)

**Row Level Security (RLS):**
- INSERT: Allow anonymous inserts (public can join waitlist)
- SELECT: Restrict to authenticated admin users only
- UPDATE/DELETE: Restrict to authenticated admin users only

**SQL Schema:**
```sql
CREATE TABLE waitlist (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_waitlist_email ON waitlist(email);
CREATE INDEX idx_waitlist_created_at ON waitlist(created_at DESC);

-- Enable RLS
ALTER TABLE waitlist ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts
CREATE POLICY "Allow anonymous waitlist inserts"
  ON waitlist
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Restrict reads to authenticated users
CREATE POLICY "Allow authenticated reads"
  ON waitlist
  FOR SELECT
  TO authenticated
  USING (true);
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid input acceptance

*For any* valid name (non-empty, 1-100 characters, non-whitespace) and valid email (proper format), submitting the waitlist form should result in a successful database entry and success message display.

**Validates: Requirements 2.2, 2.3, 2.4, 2.5**

### Property 2: Invalid input rejection

*For any* invalid input (empty name, invalid email format, or whitespace-only name), submitting the waitlist form should be rejected with an appropriate error message and no database entry created.

**Validates: Requirements 2.2, 2.3**

### Property 3: Duplicate email prevention

*For any* email address that already exists in the waitlist table, attempting to submit a new entry with that email should be rejected with a duplicate error message.

**Validates: Requirements 3.3**

### Property 4: Form state consistency during submission

*For any* form submission, while the submission is in progress, the submit button should be disabled and display a loading state, preventing multiple simultaneous submissions.

**Validates: Requirements 3.4**

### Property 5: Database persistence with correct data types

*For any* successfully submitted waitlist entry, querying the database immediately after submission should return the entry with matching name (text), email (text), a unique UUID identifier, and a valid timestamp.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 6: UI monochrome consistency

*For any* rendered element on the landing page, the computed styles should use only colors from the monochrome palette (black #000000, white #ffffff, and grayscale values between) and the JetBrains Mono font family.

**Validates: Requirements 1.3, 1.4, 1.5**

### Property 7: Login navigation functionality

*For any* click event on the login navigation element, the application should navigate to the "/login" route.

**Validates: Requirements 6.2**

### Property 8: Error recovery and form state preservation

*For any* failed submission due to server error, the form should display an error message with retry instructions and remain in a state where the user can resubmit with the same input values without refreshing the page.

**Validates: Requirements 3.5**

## Error Handling

### Client-Side Errors

**Validation Errors:**
- Empty name: "Name is required"
- Invalid email format: "Please enter a valid email address"
- Whitespace-only name: "Name cannot be empty"

**Network Errors:**
- Timeout: "Request timed out. Please try again."
- No connection: "Unable to connect. Please check your internet connection."
- Server error: "Something went wrong. Please try again later."

**Handling Strategy:**
- Display errors inline below the relevant form field
- Use terminal-style error formatting (e.g., "[ERROR] message")
- Maintain form state so users don't lose their input
- Provide clear actionable instructions

### Backend Errors

**Validation Errors (400):**
- Missing required fields
- Invalid email format
- Name too long (>100 characters)

**Duplicate Entry (409):**
- Email already exists in database

**Server Errors (500):**
- Database connection failure
- Unexpected errors

**Handling Strategy:**
- Return appropriate HTTP status codes
- Include descriptive error messages
- Log errors for debugging
- Never expose sensitive system information

### Error Logging

**Frontend:**
- Log errors to console in development
- Use structured logging with context (user action, timestamp, error details)

**Backend:**
- Log all errors with request context
- Include stack traces for 500 errors
- Log rate limit violations
- Use structured JSON logging format

## Testing Strategy

### Unit Testing

**Frontend Unit Tests:**
- WaitlistForm component rendering
- Form validation logic (empty fields, invalid email)
- Success/error message display
- Loading state behavior
- Form reset after successful submission
- FeatureCard component rendering
- LandingPage component structure

**Backend Unit Tests:**
- Input validation (name, email)
- Email format validation
- Duplicate email detection
- Error response formatting
- Rate limiting behavior

**Testing Framework:** Jest with React Testing Library (frontend), pytest (backend)

### Property-Based Testing

**Property-Based Testing Library:** fast-check (JavaScript/TypeScript)

**Configuration:** Each property test should run a minimum of 100 iterations

**Test Tagging:** Each property-based test must include a comment with the format:
`// Feature: landing-page-waitlist, Property {number}: {property_text}`

**Property Tests:**

1. **Valid Input Acceptance Test**
   - Generate random valid names (1-100 chars, non-whitespace)
   - Generate random valid emails
   - Verify successful submission and database entry
   - Tag: `// Feature: landing-page-waitlist, Property 1: Valid input acceptance`

2. **Invalid Input Rejection Test**
   - Generate random invalid inputs (empty strings, whitespace, invalid emails)
   - Verify rejection with appropriate error messages
   - Verify no database entries created
   - Tag: `// Feature: landing-page-waitlist, Property 2: Invalid input rejection`

3. **Duplicate Email Prevention Test**
   - Generate random email
   - Submit twice with different names
   - Verify second submission is rejected
   - Tag: `// Feature: landing-page-waitlist, Property 3: Duplicate email prevention`

4. **Form State Consistency Test**
   - Generate random valid inputs
   - Verify button disabled during submission
   - Verify loading state displayed
   - Tag: `// Feature: landing-page-waitlist, Property 4: Form state consistency`

5. **Database Persistence Test**
   - Generate random valid entries
   - Submit and immediately query database
   - Verify entry exists with correct data
   - Tag: `// Feature: landing-page-waitlist, Property 5: Database persistence`

6. **UI Consistency Test**
   - Render landing page components
   - Verify all elements use monochrome colors
   - Verify JetBrains Mono font usage
   - Tag: `// Feature: landing-page-waitlist, Property 6: UI consistency`

7. **Authentication-Based Routing Test**
   - Test with authenticated and unauthenticated states
   - Verify correct page display/redirect
   - Tag: `// Feature: landing-page-waitlist, Property 7: Authentication-based routing`

8. **Error Recovery Test**
   - Simulate server errors
   - Verify error message display
   - Verify form remains functional for retry
   - Tag: `// Feature: landing-page-waitlist, Property 8: Error recovery`

### Integration Testing

- End-to-end form submission flow
- Database integration with Supabase
- API endpoint integration
- Authentication routing integration

### Manual Testing Checklist

- Visual consistency with existing pages
- Responsive design on mobile/tablet/desktop
- Form accessibility (keyboard navigation, screen readers)
- Animation smoothness
- Error message clarity
- Success flow user experience
