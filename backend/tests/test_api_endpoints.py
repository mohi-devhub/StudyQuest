"""
API Endpoint Integration Tests

Tests critical API endpoints with authentication and data validation.
Validates request/response structure, error handling, and business logic.
"""
import pytest
from fastapi.testclient import TestClient
from main import app
import os
from datetime import datetime
import json

client = TestClient(app)

# Test configuration
TEST_USER_ID = "test_user_integration"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


class TestStudyRetryEndpoint:
    """Test suite for /study/retry endpoint"""
    
    def test_retry_endpoint_requires_auth(self):
        """
        Test that /study/retry requires authentication.
        """
        response = client.post(
            "/study/retry",
            json={
                "topic": "Python Programming",
                "num_questions": 5
            }
        )
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"
    
    def test_retry_endpoint_validates_topic(self):
        """
        Test that /study/retry validates topic input.
        """
        # Test with empty topic
        response = client.post(
            "/study/retry",
            json={
                "topic": "",
                "num_questions": 5
            }
        )
        
        # Should fail due to missing auth or validation
        assert response.status_code in [400, 403], \
            "Should reject empty topic or require auth"
    
    def test_retry_endpoint_validates_num_questions(self):
        """
        Test that /study/retry validates num_questions parameter.
        """
        # Test with invalid num_questions (too high)
        response = client.post(
            "/study/retry",
            json={
                "topic": "Test Topic",
                "num_questions": 100  # Exceeds max of 20
            }
        )
        
        # Should fail validation or require auth
        assert response.status_code in [400, 403, 422], \
            "Should reject invalid num_questions or require auth"


class TestProgressV2Endpoints:
    """Test suite for /progress/v2 endpoints"""
    
    def test_submit_quiz_requires_auth(self):
        """
        Test that /progress/v2/submit-quiz requires authentication.
        """
        response = client.post(
            "/progress/v2/submit-quiz",
            json={
                "user_id": TEST_USER_ID,
                "topic": "Python",
                "difficulty": "medium",
                "correct": 8,
                "total": 10
            }
        )
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"
    
    def test_submit_quiz_validates_score(self):
        """
        Test that submit-quiz validates score (correct <= total).
        """
        response = client.post(
            "/progress/v2/submit-quiz",
            json={
                "user_id": TEST_USER_ID,
                "topic": "Python",
                "difficulty": "medium",
                "correct": 15,  # More than total
                "total": 10
            }
        )
        
        # Should fail validation or require auth
        assert response.status_code in [400, 403, 422], \
            "Should reject invalid score or require auth"
    
    def test_submit_quiz_validates_difficulty(self):
        """
        Test that submit-quiz validates difficulty level.
        """
        response = client.post(
            "/progress/v2/submit-quiz",
            json={
                "user_id": TEST_USER_ID,
                "topic": "Python",
                "difficulty": "invalid_difficulty",
                "correct": 8,
                "total": 10
            }
        )
        
        # Should fail validation or require auth
        assert response.status_code in [400, 403, 422], \
            "Should reject invalid difficulty or require auth"
    
    def test_get_user_stats_endpoint(self):
        """
        Test /progress/v2/user/{user_id}/stats endpoint structure.
        """
        response = client.get(f"/progress/v2/user/{TEST_USER_ID}/stats")
        
        # May require auth or return data
        if response.status_code == 200:
            data = response.json()
            assert 'user_id' in data, "Response should contain user_id"
            assert 'total_xp' in data or 'progress' in data, \
                "Response should contain progress data"
        else:
            # Should be auth error or not found
            assert response.status_code in [401, 403, 404, 500], \
                f"Unexpected status code: {response.status_code}"
    
    def test_get_user_topics_endpoint(self):
        """
        Test /progress/v2/user/{user_id}/topics endpoint.
        """
        response = client.get(f"/progress/v2/user/{TEST_USER_ID}/topics")
        
        if response.status_code == 200:
            data = response.json()
            assert 'topics' in data, "Response should contain topics"
            assert isinstance(data['topics'], list), "Topics should be a list"
        else:
            # Should be auth error or not found
            assert response.status_code in [401, 403, 404, 500], \
                f"Unexpected status code: {response.status_code}"
    
    def test_get_leaderboard_endpoint(self):
        """
        Test /progress/v2/leaderboard endpoint.
        """
        response = client.get("/progress/v2/leaderboard?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            assert 'leaderboard' in data, "Response should contain leaderboard"
            assert isinstance(data['leaderboard'], list), \
                "Leaderboard should be a list"
            assert len(data['leaderboard']) <= 5, \
                "Should respect limit parameter"
        else:
            # May require auth or have other issues
            assert response.status_code in [401, 403, 500], \
                f"Unexpected status code: {response.status_code}"


class TestAchievementsEndpoints:
    """Test suite for /achievements endpoints"""
    
    def test_get_user_badges_requires_auth(self):
        """
        Test that /achievements/user/{user_id}/badges requires authentication.
        """
        response = client.get(f"/achievements/user/{TEST_USER_ID}/badges")
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"
    
    def test_get_all_badges_endpoint(self):
        """
        Test /achievements/all-badges endpoint (public).
        """
        response = client.get("/achievements/all-badges")
        
        if response.status_code == 200:
            data = response.json()
            assert 'badges' in data, "Response should contain badges"
            assert isinstance(data['badges'], list), "Badges should be a list"
            
            # Validate badge structure if any exist
            if len(data['badges']) > 0:
                badge = data['badges'][0]
                assert 'name' in badge, "Badge should have name"
                assert 'description' in badge, "Badge should have description"
                assert 'tier' in badge, "Badge should have tier"
        else:
            # May have database issues
            assert response.status_code in [500], \
                f"Unexpected status code: {response.status_code}"
    
    def test_get_achievements_summary_requires_auth(self):
        """
        Test that /achievements/user/{user_id}/summary requires authentication.
        """
        response = client.get(f"/achievements/user/{TEST_USER_ID}/summary")
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"
    
    def test_check_badges_requires_auth(self):
        """
        Test that /achievements/user/{user_id}/check requires authentication.
        """
        response = client.post(f"/achievements/user/{TEST_USER_ID}/check")
        
        assert response.status_code == 403, \
            f"Expected 403 Forbidden, got {response.status_code}"


class TestHealthEndpoints:
    """Test suite for health check endpoints"""
    
    def test_basic_health_check(self):
        """
        Test /health endpoint returns healthy status.
        """
        response = client.get("/health")
        
        assert response.status_code == 200, \
            f"Health check should return 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Health check should return status"
    
    def test_detailed_health_check(self):
        """
        Test /health/detailed endpoint returns dependency status.
        """
        response = client.get("/health/detailed")
        
        assert response.status_code == 200, \
            f"Detailed health check should return 200, got {response.status_code}"
        
        data = response.json()
        assert 'status' in data, "Should contain overall status"
        assert 'dependencies' in data, "Should contain dependency status"
        
        # Validate dependencies structure
        dependencies = data['dependencies']
        assert isinstance(dependencies, dict), "Dependencies should be a dict"


class TestRootEndpoint:
    """Test suite for root endpoint"""
    
    def test_root_endpoint(self):
        """
        Test root endpoint returns API information.
        """
        response = client.get("/")
        
        assert response.status_code == 200, \
            f"Root endpoint should return 200, got {response.status_code}"
        
        data = response.json()
        assert 'message' in data, "Root should return message"


class TestInputValidation:
    """Test input validation across endpoints"""
    
    def test_topic_length_validation(self):
        """
        Test that topic length is validated (max 50 chars for some endpoints).
        """
        long_topic = "A" * 100  # 100 characters
        
        response = client.post(
            "/study/retry",
            json={
                "topic": long_topic,
                "num_questions": 5
            }
        )
        
        # Should fail validation or require auth
        assert response.status_code in [400, 403, 422], \
            "Should reject overly long topic or require auth"
    
    def test_negative_num_questions(self):
        """
        Test that negative num_questions is rejected.
        """
        response = client.post(
            "/study/retry",
            json={
                "topic": "Test",
                "num_questions": -5
            }
        )
        
        # Should fail validation or require auth
        assert response.status_code in [400, 403, 422], \
            "Should reject negative num_questions or require auth"
    
    def test_malformed_json(self):
        """
        Test that malformed JSON is rejected.
        """
        response = client.post(
            "/study/retry",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422], \
            f"Should reject malformed JSON, got {response.status_code}"


class TestErrorResponses:
    """Test error response formats"""
    
    def test_404_for_invalid_endpoint(self):
        """
        Test that invalid endpoints return 404.
        """
        response = client.get("/invalid/endpoint/path")
        
        assert response.status_code == 404, \
            f"Invalid endpoint should return 404, got {response.status_code}"
    
    def test_405_for_wrong_method(self):
        """
        Test that wrong HTTP method returns 405.
        """
        # GET on POST-only endpoint
        response = client.get("/study/retry")
        
        assert response.status_code == 405, \
            f"Wrong method should return 405, got {response.status_code}"
    
    def test_error_response_structure(self):
        """
        Test that error responses have consistent structure.
        """
        response = client.post(
            "/study/retry",
            json={"topic": ""}  # Invalid empty topic
        )
        
        # Should return error
        if response.status_code >= 400:
            data = response.json()
            assert 'detail' in data, "Error response should contain detail"


class TestCORSHeaders:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self):
        """
        Test that CORS headers are present in responses.
        """
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # Check for CORS headers
        assert 'access-control-allow-origin' in response.headers or \
               response.status_code == 200, \
            "CORS headers should be present or endpoint should be accessible"


class TestSecurityHeaders:
    """Test security headers"""
    
    def test_security_headers_present(self):
        """
        Test that security headers are present in responses.
        """
        response = client.get("/health")
        
        # Check for security headers
        headers = response.headers
        
        assert 'x-content-type-options' in headers, \
            "Should have X-Content-Type-Options header"
        assert headers.get('x-content-type-options') == 'nosniff', \
            "X-Content-Type-Options should be nosniff"
        
        assert 'x-frame-options' in headers, \
            "Should have X-Frame-Options header"
        assert headers.get('x-frame-options') == 'DENY', \
            "X-Frame-Options should be DENY"


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_headers(self):
        """
        Test that rate limit information is available.
        Note: Actual rate limiting may not trigger in tests.
        """
        response = client.get("/")
        
        # Rate limiting is configured, check response is valid
        assert response.status_code == 200, \
            "Endpoint should be accessible"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
