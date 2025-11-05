#!/usr/bin/env python3
"""
Test script for Progress API endpoints
Tests the new endpoints: GET /{user_id}, POST /update, POST /reset
"""

import asyncio
import httpx
import json
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"


async def test_progress_endpoints():
    """Test all progress endpoints"""
    
    print("=" * 80)
    print("PROGRESS API ENDPOINTS TEST")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient() as client:
        # Step 1: Login to get JWT token
        print("Step 1: Authenticating user...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            print("\n⚠️  Make sure to:")
            print("   1. Create a test user first")
            print("   2. Backend server is running (uvicorn main:app --reload)")
            return
        
        auth_data = login_response.json()
        token = auth_data['access_token']
        user_id = auth_data['user']['id']
        
        print(f"✅ Authenticated as {TEST_USER_EMAIL}")
        print(f"   User ID: {user_id}")
        print()
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Test GET /progress/{user_id}
        print("=" * 80)
        print("Step 2: Testing GET /progress/{user_id}")
        print("=" * 80)
        
        response = await client.get(
            f"{BASE_URL}/progress/{user_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully fetched user progress and XP")
            print(f"   Total Topics: {data['statistics']['total_topics']}")
            print(f"   Completed Topics: {data['statistics']['completed_topics']}")
            print(f"   Average Score: {data['statistics']['average_score']}%")
            print(f"   Total XP: {data['xp']['total_xp']}")
            print(f"   Total Activities: {data['xp']['total_activities']}")
            print()
            
            if data['topics']:
                print("   Topics Progress:")
                for topic in data['topics'][:3]:  # Show first 3
                    print(f"      - {topic['topic']}: {topic['completion_status']} ({topic['avg_score']}%)")
                print()
        else:
            print(f"❌ Failed to fetch progress: {response.status_code}")
            print(f"   {response.text}")
            print()
        
        # Step 3: Test GET /progress/{wrong_user_id} (should fail with 403)
        print("=" * 80)
        print("Step 3: Testing GET /progress/{wrong_user_id} (Security Test)")
        print("=" * 80)
        
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(
            f"{BASE_URL}/progress/{fake_user_id}",
            headers=headers
        )
        
        if response.status_code == 403:
            print("✅ Security check passed: Cannot access other user's data")
            print(f"   Status: {response.status_code} Forbidden")
            print()
        else:
            print(f"⚠️  Security issue: Got status {response.status_code}")
            print()
        
        # Step 4: Test POST /progress/update
        print("=" * 80)
        print("Step 4: Testing POST /progress/update")
        print("=" * 80)
        
        xp_update_data = {
            "points": 50,
            "reason": "daily_streak",
            "metadata": {
                "streak_days": 7,
                "bonus_type": "weekly",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        response = await client.post(
            f"{BASE_URL}/progress/update",
            headers=headers,
            json=xp_update_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully awarded XP")
            print(f"   Points Awarded: {data['xp_log']['points']}")
            print(f"   Reason: {data['xp_log']['reason']}")
            print(f"   Total XP: {data['total_xp']}")
            print(f"   Message: {data['message']}")
            print()
        else:
            print(f"❌ Failed to update XP: {response.status_code}")
            print(f"   {response.text}")
            print()
        
        # Step 5: Test POST /progress/update with custom activity
        print("=" * 80)
        print("Step 5: Testing POST /progress/update (Custom Activity)")
        print("=" * 80)
        
        custom_xp_data = {
            "points": 100,
            "reason": "achievement_unlocked",
            "metadata": {
                "achievement": "First Perfect Score",
                "category": "quiz_mastery"
            }
        }
        
        response = await client.post(
            f"{BASE_URL}/progress/update",
            headers=headers,
            json=custom_xp_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully awarded custom XP")
            print(f"   Points: {data['xp_log']['points']}")
            print(f"   Reason: {data['xp_log']['reason']}")
            print(f"   New Total XP: {data['total_xp']}")
            print()
        else:
            print(f"❌ Failed: {response.status_code}")
            print()
        
        # Step 6: Create a test topic progress (if none exists)
        print("=" * 80)
        print("Step 6: Creating test topic progress")
        print("=" * 80)
        
        test_topic = "API Test Topic"
        
        # Check if topic exists
        response = await client.get(
            f"{BASE_URL}/progress/topics",
            headers=headers
        )
        
        existing_topics = response.json()['topics'] if response.status_code == 200 else []
        test_topic_exists = any(t['topic'] == test_topic for t in existing_topics)
        
        if not test_topic_exists:
            # Create progress by completing a mock quiz
            from utils.progress_tracker import ProgressTracker
            
            print(f"   Creating progress for '{test_topic}'...")
            # Note: In production, this would come from /progress/evaluate
            # For testing, we'll call the tracker directly
            print("   (Progress would be created via quiz completion)")
            print()
        else:
            print(f"✅ Test topic '{test_topic}' already exists")
            print()
        
        # Step 7: Test POST /progress/reset
        print("=" * 80)
        print("Step 7: Testing POST /progress/reset")
        print("=" * 80)
        
        if existing_topics:
            # Use the first available topic for reset test
            topic_to_reset = existing_topics[0]['topic']
            
            reset_data = {
                "topic": topic_to_reset
            }
            
            response = await client.post(
                f"{BASE_URL}/progress/reset",
                headers=headers,
                json=reset_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Successfully reset topic progress")
                print(f"   Topic: {data['topic']}")
                print(f"   Message: {data['message']}")
                print(f"   Note: {data['note']}")
                print()
                
                # Verify it's gone
                verify_response = await client.get(
                    f"{BASE_URL}/progress/topics/{topic_to_reset}",
                    headers=headers
                )
                
                if verify_response.status_code == 404:
                    print("✅ Verified: Progress successfully deleted")
                    print()
                else:
                    print("⚠️  Warning: Progress still exists after reset")
                    print()
            else:
                print(f"❌ Failed to reset progress: {response.status_code}")
                print(f"   {response.text}")
                print()
        else:
            print("ℹ️  Skipping reset test (no topics available)")
            print("   Create progress by completing a quiz first")
            print()
        
        # Step 8: Test resetting non-existent topic
        print("=" * 80)
        print("Step 8: Testing POST /progress/reset (Non-existent Topic)")
        print("=" * 80)
        
        reset_data = {
            "topic": "Non-Existent Topic 12345"
        }
        
        response = await client.post(
            f"{BASE_URL}/progress/reset",
            headers=headers,
            json=reset_data
        )
        
        if response.status_code == 404:
            print("✅ Correctly returns 404 for non-existent topic")
            print(f"   Message: {response.json()['detail']}")
            print()
        else:
            print(f"⚠️  Expected 404, got {response.status_code}")
            print()
        
        # Final Summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        response = await client.get(
            f"{BASE_URL}/progress/{user_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            final_data = response.json()
            print(f"✅ Final User State:")
            print(f"   Total XP: {final_data['xp']['total_xp']}")
            print(f"   Total Topics: {final_data['statistics']['total_topics']}")
            print(f"   Total Activities: {final_data['xp']['total_activities']}")
            print()
            
            print("Recent XP Logs:")
            for log in final_data['recent_xp_logs'][:5]:
                print(f"   - {log['points']} XP for {log['reason']} at {log['timestamp']}")
            print()
        
        print("=" * 80)
        print("ALL TESTS COMPLETED")
        print("=" * 80)


async def test_validation():
    """Test input validation"""
    
    print("\n")
    print("=" * 80)
    print("VALIDATION TESTS")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient() as client:
        # Login first
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if login_response.status_code != 200:
            print("❌ Cannot proceed without authentication")
            return
        
        token = login_response.json()['access_token']
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 1: Invalid XP points (too high)
        print("Test 1: Invalid XP points (exceeds max)")
        response = await client.post(
            f"{BASE_URL}/progress/update",
            headers=headers,
            json={
                "points": 5000,  # Max is 1000
                "reason": "test"
            }
        )
        
        if response.status_code == 422:
            print("✅ Validation passed: Rejected points > 1000")
        else:
            print(f"⚠️  Expected 422, got {response.status_code}")
        print()
        
        # Test 2: Invalid XP points (negative)
        print("Test 2: Invalid XP points (negative)")
        response = await client.post(
            f"{BASE_URL}/progress/update",
            headers=headers,
            json={
                "points": -50,
                "reason": "test"
            }
        )
        
        if response.status_code == 422:
            print("✅ Validation passed: Rejected negative points")
        else:
            print(f"⚠️  Expected 422, got {response.status_code}")
        print()
        
        # Test 3: Empty topic in reset
        print("Test 3: Empty topic in reset")
        response = await client.post(
            f"{BASE_URL}/progress/reset",
            headers=headers,
            json={
                "topic": ""
            }
        )
        
        if response.status_code == 422:
            print("✅ Validation passed: Rejected empty topic")
        else:
            print(f"⚠️  Expected 422, got {response.status_code}")
        print()


async def main():
    """Run all tests"""
    print("\n")
    print("🚀 Starting Progress API Tests")
    print("Make sure:")
    print("   1. Backend server is running: uvicorn main:app --reload")
    print("   2. Supabase tables are created (run migration)")
    print("   3. Test user exists (email: test@example.com)")
    print("\n")
    
    try:
        await test_progress_endpoints()
        await test_validation()
        
        print("\n✅ All tests completed successfully!")
        print("Check docs/progress-tracking.md for API documentation")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
