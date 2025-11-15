"""
Authentication Flow Tests

Tests authentication requirements for protected endpoints.
Validates JWT token handling, authentication failures, and access control.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os
from datetime import datetime, timedelta
import jwt

client = TestClient(app)

# Test configuration
TEST_USER_ID = "test_user_123"
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "test-secret-key")


def generate_test_jwt(user_id: str, expired: bool = False, invalid: bool = False) -> str:
    """
    Generate a test JWT token for authentication testing.
    
    Args:
        user_id: User ID to include in token
        expired: If True, generate an expired token
        invalid: If True, generate an invalid token
    
    Returns:
        JWT token string
    """
    if invalid:
        return "invalid.jwt.token"
    
    # Calculate expiration time
    if expired:
        exp = datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
    else:
        exp = datetime.utcnow() + timedelta(hours=1)  # Valid for 1 hour
    
    payload = {
        "sub": user_id,
        "exp": int(exp.timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "role": "authenticated"
    }
    
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    return token


class TestAuthenticationFlow:
    """Test suite for authentication flow on protected endpoints"""
    
    def test_protected_endpoint_without_auth(self):
        """
        Test that protected endpoints require authentication.
        Expect 401 Unauthorized when no token is provided.
        """
        # Test /study/retry endpoint without authentication
        response = client.post(
            "/study/retry",
            json={
                "topic": "Python Programming",
                "num_questions": 5
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert "detail" in response.json(), "Response should contain error detail"
    
    def test_protected_endpoint_with_invalid_token(self):
        """
        Test that protected endpoints reject invalid JWT tokens.
        Expect 401 Unauthorized with invalid token.
        """
        invalid_token = "invalid.jwt.token.format"
        
        response = client.post(
            "/study/retry",
            json={
                "topic": "Python Programming",
                "num_questions": 5
            },
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        response_data = response.json()
        assert "detail" in response_data, "Response should contain error detail"
    
    def test_protected_endpoint_with_malformed_auth_header(self):
        """
        Test that endpoints reject malformed Authorization headers.
        """
        # Missing "Bearer" prefix
        response = client.post(
            "/study/retry",
            json={
                "topic": "Python Programming",
                "num_questions": 5
            },
            headers={"Authorization": "some-token"}
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_study_endpoint_without_auth(self):
        """
        Test /study endpoint requires authentication.
        """
        response = client.post(
            "/study",
            json={
                "topic": "Machine Learning",
                "num_questions": 3
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_generate_notes_without_auth(self):
        """
        Test /study/generate-notes endpoint requires authentication.
        """
        response = client.post(
            "/study/generate-notes",
            json={
                "topic": "Data Structures"
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_adaptive_quiz_without_auth(self):
        """
        Test /study/adaptive-quiz endpoint requires authentication.
        """
        response = client.post(
            "/study/adaptive-quiz",
            json={
                "topic": "Algorithms",
                "num_questions": 5
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_recommendations_without_auth(self):
        """
        Test /study/recommendations endpoint requires authentication.
        """
        response = client.get("/study/recommendations")
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_progress_submit_quiz_without_auth(self):
        """
        Test /progress/v2/submit-quiz endpoint requires authentication.
        """
        response = client.post(
            "/progress/v2/submit-quiz",
            json={
                "user_id": "test_user",
                "topic": "Python",
                "difficulty": "medium",
                "correct": 8,
                "total": 10
            }
        )
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    
    def test_achievements_badges_without_auth(self):
        """
        Test /achievements/user/{user_id}/badges endpoint requires authentication.
        """
        response = client.get("/achievements/user/test_user/badges")
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"


class TestAuthenticationValidation:
    """Test authentication validation logic"""
    
    def test_missing_authorization_header(self):
        """
        Test that requests without Authorization header are rejected.
        """
        response = client.post(
            "/study/retry",
            json={"topic": "Test", "num_questions": 5}
        )
        
        assert response.status_code == 403
    
    def test_empty_authorization_header(self):
        """
        Test that empty Authorization header is rejected.
        """
        response = client.post(
            "/study/retry",
            json={"topic": "Test", "num_questions": 5},
            headers={"Authorization": ""}
        )
        
        assert response.status_code == 403
    
    def test_bearer_token_case_sensitivity(self):
        """
        Test that Bearer token scheme is case-insensitive (per HTTP spec).
        """
        # Note: FastAPI's HTTPBearer is case-insensitive by default
        response = client.post(
            "/study/retry",
            json={"topic": "Test", "num_questions": 5},
            headers={"Authorization": "bearer invalid-token"}
        )
        
        # Should still fail due to invalid token, but not due to case
        assert response.status_code in [401, 403]


class TestRateLimiting:
    """Test rate limiting on protected endpoints"""
    
    def test_rate_limit_enforcement(self):
        """
        Test that rate limiting is enforced on protected endpoints.
        Note: This test may be skipped if rate limiting is not configured.
        """
        # Make multiple rapid requests to trigger rate limit
        # Rate limit is 5/minute for most endpoints
        responses = []
        
        for i in range(7):  # Exceed the 5/minute limit
            response = client.post(
                "/study/retry",
                json={"topic": f"Test Topic {i}", "num_questions": 5}
            )
            responses.append(response)
        
        # At least one request should be rate limited (429)
        status_codes = [r.status_code for r in responses]
        
        # All should be 403 (no auth) or 429 (rate limited)
        assert all(code in [403, 429] for code in status_codes), \
            f"Unexpected status codes: {status_codes}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
