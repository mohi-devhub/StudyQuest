# AI Error Handling Tests - README

## Overview

This directory contains comprehensive tests for AI error handling in the StudyQuest platform. The tests validate that all AI agents (Quiz, Recommendation, and Coach) handle errors gracefully and provide user-friendly error messages.

## Task Reference

**Task 8.5: Validate AI Error Handling**
- Test AI endpoints with invalid API key (should use fallback)
- Test AI endpoints with network timeout (should return graceful error)
- Test AI endpoints with rate limit exceeded (should retry with backoff)
- Verify error messages are user-friendly

**Requirement**: 8.4 - AI error handling validation

## Test Files

### 1. `test_ai_quality.py`
Main test suite containing all AI quality and error handling tests.

**Error Handling Test Class**: `TestAIErrorHandling`

**Tests Included**:
- `test_quiz_handles_empty_notes` - Validates empty input rejection
- `test_quiz_fallback_mechanism` - Tests multi-model fallback
- `test_quiz_with_invalid_api_key` - Tests invalid API key handling for quiz
- `test_quiz_with_network_timeout` - Tests timeout handling for quiz
- `test_recommendation_with_invalid_api_key` - Tests invalid API key handling for recommendations
- `test_recommendation_with_network_timeout` - Tests timeout handling for recommendations
- `test_coach_with_invalid_api_key` - Tests invalid API key handling for coach
- `test_error_messages_are_user_friendly` - Validates error message quality
- `test_fallback_with_multiple_model_failures` - Tests behavior when all models fail

### 2. `verify_error_handling.py`
Manual verification script that demonstrates error handling behavior without requiring pytest.

**Tests Included**:
- Empty notes handling
- Missing API key detection
- Recommendation fallback on API failure
- Valid quiz generation (baseline)

### 3. `AI_ERROR_HANDLING_TEST_SUMMARY.md`
Comprehensive documentation of all error handling tests, patterns, and requirements.

## Running the Tests

### Option 1: Using pytest (Recommended)

```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all AI error handling tests
pytest backend/tests/test_ai_quality.py::TestAIErrorHandling -v

# Run specific test
pytest backend/tests/test_ai_quality.py::TestAIErrorHandling::test_quiz_with_invalid_api_key -v

# Run with output
pytest backend/tests/test_ai_quality.py::TestAIErrorHandling -v -s
```

### Option 2: Using the verification script

```bash
# Make sure you're in the backend directory
cd backend

# Run the verification script
python tests/verify_error_handling.py

# Or with python3
python3 tests/verify_error_handling.py
```

The verification script provides a quick way to see error handling in action without pytest.

## Test Coverage

### Error Scenarios Covered

1. **Invalid API Key**
   - Quiz generation with invalid key
   - Recommendation generation with invalid key
   - Coach agent with invalid key
   - Verifies graceful degradation and fallback

2. **Network Timeouts**
   - Quiz generation timeout
   - Recommendation generation timeout
   - Verifies graceful error messages

3. **Empty/Invalid Input**
   - Empty notes rejection
   - Invalid parameters
   - Clear error messages

4. **Fallback Mechanisms**
   - Multi-model fallback chain
   - Graceful degradation
   - Retry logic

5. **User-Friendly Errors**
   - No sensitive data exposure
   - Clear, actionable messages
   - Appropriate error types

## Expected Behavior

### Graceful Degradation
- **Recommendations**: Continue to work without AI enhancement when API fails
- **Quiz**: Attempts multiple fallback models before failing
- **Coach**: Provides clear error when unable to generate content

### Security
- Error messages NEVER expose API keys
- No internal implementation details in user-facing errors
- Sensitive information is sanitized

### User Experience
- All errors are clear and actionable
- Errors explain what went wrong in plain language
- No technical jargon or stack traces

## Error Handling Patterns

### Pattern 1: Try-Catch with Fallback
```python
try:
    result = await primary_method()
except Exception:
    result = await fallback_method()
```

### Pattern 2: Graceful Degradation
```python
try:
    ai_enhanced_result = await ai_method()
    return {'data': result, 'ai_enhanced': True}
except Exception:
    basic_result = basic_method()
    return {'data': result, 'ai_enhanced': False}
```

### Pattern 3: User-Friendly Error Messages
```python
try:
    result = await api_call()
except httpx.TimeoutException:
    raise Exception("Request timed out. Please try again.")
except httpx.HTTPStatusError as e:
    raise Exception(f"API error: {e.response.status_code}")
```

## Mocking Strategy

The tests use `unittest.mock` to simulate error conditions:

```python
from unittest.mock import patch, AsyncMock

# Mock timeout
with patch('httpx.AsyncClient') as mock_client:
    mock_instance = AsyncMock()
    mock_instance.post.side_effect = httpx.TimeoutException("Timeout")
    mock_client.return_value = mock_instance
    # Test code here
```

## Environment Setup

### Required Environment Variables
- `OPENROUTER_API_KEY` - OpenRouter API key (can be invalid for error tests)

### Test Isolation
- Tests save and restore environment variables
- No side effects between tests
- Each test is independent

## Troubleshooting

### Issue: Tests fail with "No module named pytest"
**Solution**: Install pytest
```bash
pip install pytest pytest-asyncio
```

### Issue: Tests fail with "OPENROUTER_API_KEY not found"
**Solution**: This is expected for some tests. The tests specifically test this scenario.

### Issue: Tests timeout
**Solution**: Check network connectivity. Some tests make real API calls for baseline validation.

### Issue: Import errors
**Solution**: Make sure you're running from the correct directory and all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

## CI/CD Integration

These tests should be run in the CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Run AI Error Handling Tests
  run: |
    cd backend
    pytest tests/test_ai_quality.py::TestAIErrorHandling -v
```

## Maintenance

### Adding New Error Handling Tests

1. Add test method to `TestAIErrorHandling` class
2. Use `@pytest.mark.asyncio` decorator for async tests
3. Follow naming convention: `test_<component>_<scenario>`
4. Document the requirement being tested
5. Update this README with new test information

### Updating Error Messages

When updating error messages in the codebase:
1. Update corresponding tests
2. Verify error messages remain user-friendly
3. Ensure no sensitive data is exposed
4. Run full test suite to verify

## Success Criteria

All tests should pass, demonstrating:
- ✅ Invalid API keys are handled gracefully
- ✅ Network timeouts don't crash the application
- ✅ Fallback mechanisms work correctly
- ✅ Error messages are user-friendly
- ✅ No sensitive data is exposed in errors
- ✅ System degrades gracefully under failure conditions

## Related Documentation

- `AI_ERROR_HANDLING_TEST_SUMMARY.md` - Detailed test documentation
- `../agents/adaptive_quiz_agent.py` - Quiz agent implementation
- `../agents/recommendation_agent.py` - Recommendation agent implementation
- `../agents/coach_agent.py` - Coach agent implementation
- `.kiro/specs/production-readiness-audit/tasks.md` - Task 8.5 specification

## Contact

For questions or issues with these tests, refer to the production readiness audit documentation or the main project README.
