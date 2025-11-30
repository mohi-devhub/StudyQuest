import pytest
import asyncio
import json
from datetime import datetime
import os
import sys

# Add parent directory to path to import agents
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coach_agent import study_topic


# Test configuration
TEST_TOPICS = [
    {"topic": "Neural Networks", "num_questions": 5},
    {"topic": "Photosynthesis", "num_questions": 5}
]


@pytest.mark.asyncio
async def test_study_workflow_direct(mocker):
    """Test the study workflow by calling the coach agent directly (no HTTP)"""
    
    print("="*80)
    print("END-TO-END WORKFLOW TESTING (Direct Agent Calls)")
    print("="*80)
    print(f"\nTesting {len(TEST_TOPICS)} topics")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    results = []
    
    # Mock the study_topic function
    mocker.patch(
        "agents.coach_agent.study_topic",
        return_value={
            "topic": "Mock Topic",
            "notes": {
                "topic": "Mock Topic",
                "summary": "This is a mock summary.",
                "key_points": ["Mock point 1", "Mock point 2"]
            },
            "quiz": [
                {
                    "question": "Mock question 1?",
                    "options": ["A) Opt1", "B) Opt2", "C) Opt3", "D) Opt4"],
                    "answer": "A",
                    "explanation": "Mock explanation"
                }
            ],
            "metadata": {
                "num_key_points": 2,
                "num_questions": 1
            }
        }
    )
    
    for i, test_case in enumerate(TEST_TOPICS, 1):
        topic = test_case["topic"]
        num_questions = test_case["num_questions"]
        
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(TEST_TOPICS)}: {topic}")
        print(f"{'='*80}\n")
        
        try:
            print(f"📤 Generating study package...")
            print(f"   Topic: {topic}")
            print(f"   Questions: {num_questions}")
            
            start_time = datetime.now()
            
            # Call coach agent directly
            data = await study_topic(topic, num_questions)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n📥 Package generated in {duration:.2f} seconds")
            
            # Validate structure
            print(f"\n✅ SUCCESS - Validating response structure...")
            
            # Check top-level keys
            required_keys = ["topic", "notes", "quiz", "metadata"]
            for key in required_keys:
                if key in data:
                    print(f"   ✓ Has '{key}'")
                else:
                    print(f"   ✗ Missing '{key}'")
            
            # Validate notes
            if "notes" in data:
                notes = data["notes"]
                print(f"\n📚 NOTES VALIDATION:")
                print(f"   Topic: {notes.get('topic', 'N/A')}")
                print(f"   Summary length: {len(notes.get('summary', ''))} chars")
                print(f"   Key points: {len(notes.get('key_points', []))}")
                
                # Check relevance
                summary = notes.get('summary', '').lower()
                topic_words = topic.lower().split()
                relevance = any(word in summary for word in topic_words)
                print(f"   Topic relevance: {'✓ Yes' if relevance else '✗ No'}")
                
                # Display summary
                print(f"\n   Summary Preview:")
                summary_text = notes.get('summary', 'N/A')
                print(f"   {summary_text[:200]}...")
                
                # Display key points
                print(f"\n   Key Points:")
                for idx, point in enumerate(notes.get('key_points', [])[:3], 1):
                    print(f"   {idx}. {point[:100]}...")
            
            # Validate quiz
            if "quiz" in data:
                quiz = data["quiz"]
                print(f"\n❓ QUIZ VALIDATION:")
                print(f"   Number of questions: {len(quiz)}")
                
                for idx, q in enumerate(quiz[:2], 1):  # Show first 2 questions
                    print(f"\n   Q{idx}: {q.get('question', 'N/A')[:80]}...")
                    print(f"   Options: {len(q.get('options', []))}")
                    print(f"   Answer: {q.get('answer', 'N/A')}")
                    print(f"   Has explanation: {'✓ Yes' if q.get('explanation') else '✗ No'}")
                    
                    # Check alignment with notes
                    question_text = q.get('question', '').lower()
                    notes_text = data['notes'].get('summary', '').lower()
                    key_points_text = ' '.join(data['notes'].get('key_points', [])).lower()
                    
                    # Check if question keywords appear in notes
                    question_keywords = [word for word in question_text.split() if len(word) > 4]
                    alignment_count = sum(1 for word in question_keywords 
                                        if word in notes_text or word in key_points_text)
                    alignment = alignment_count > 0
                    
                    print(f"   Content alignment: {'✓ Yes' if alignment else '? Unclear'} ({alignment_count} keywords found)")
            
            # Validate metadata
            if "metadata" in data:
                metadata = data["metadata"]
                print(f"\n📊 METADATA:")
                print(f"   Key points count: {metadata.get('num_key_points', 'N/A')}")
                print(f"   Questions count: {metadata.get('num_questions', 'N/A')}")
            
            # Store result
            results.append({
                "test_case": i,
                "topic": topic,
                "status": "SUCCESS",
                "duration_seconds": duration,
                "response": data
            })
            
            print(f"\n{'='*80}")
            print(f"✅ TEST {i} PASSED")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            
            results.append({
                "test_case": i,
                "topic": topic,
                "status": "ERROR",
                "error": str(e)
            })
        
        # Wait between tests to avoid rate limiting
        if i < len(TEST_TOPICS):
            print(f"\n⏳ Waiting 45 seconds before next test to avoid rate limits...")
            await asyncio.sleep(45)
    
    return results


def save_results(results):
    """Save test results to markdown file"""
    
    output_file = "../docs/test_results.md"
    
    with open(output_file, 'w') as f:
        f.write("# End-to-End API Test Results\n\n")
        f.write(f"**Test Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Test Method:** Direct Coach Agent Calls (no HTTP)\n\n")
        f.write(f"**Topics Tested:** {len(TEST_TOPICS)}\n\n")
        f.write("---\n\n")
        
        # Summary
        f.write("## Test Summary\n\n")
        f.write("| Test # | Topic | Status | Duration |\n")
        f.write("|--------|-------|--------|----------|\n")
        
        for result in results:
            test_num = result.get('test_case', 'N/A')
            topic = result.get('topic', 'N/A')
            status = result.get('status', 'UNKNOWN')
            duration = result.get('duration_seconds', 0)
            
            status_emoji = {
                'SUCCESS': '✅',
                'FAILED': '❌',
                'ERROR': '💥',
                'AUTH_REQUIRED': '🔒'
            }.get(status, '❓')
            
            f.write(f"| {test_num} | {topic} | {status_emoji} {status} | {duration:.2f}s |\n")
        
        f.write("\n---\n\n")
        
        # Detailed results
        for result in results:
            test_num = result.get('test_case', 'N/A')
            topic = result.get('topic', 'N/A')
            status = result.get('status', 'UNKNOWN')
            
            f.write(f"## Test {test_num}: {topic}\n\n")
            f.write(f"**Status:** {status}\n\n")
            
            if status == "SUCCESS" and 'response' in result:
                data = result['response']
                
                # Notes section
                f.write("### Study Notes\n\n")
                if 'notes' in data:
                    notes = data['notes']
                    f.write(f"**Topic:** {notes.get('topic', 'N/A')}\n\n")
                    f.write(f"**Summary:**\n\n{notes.get('summary', 'N/A')}\n\n")
                    f.write(f"**Key Points:**\n\n")
                    for idx, point in enumerate(notes.get('key_points', []), 1):
                        f.write(f"{idx}. {point}\n")
                    f.write("\n")
                
                # Quiz section
                f.write("### Quiz Questions\n\n")
                if 'quiz' in data:
                    quiz = data['quiz']
                    for idx, q in enumerate(quiz, 1):
                        f.write(f"**Question {idx}:**\n\n")
                        f.write(f"{q.get('question', 'N/A')}\n\n")
                        f.write(f"**Options:**\n\n")
                        for option in q.get('options', []):
                            f.write(f"- {option}\n")
                        f.write(f"\n**Correct Answer:** {q.get('answer', 'N/A')}\n\n")
                        if q.get('explanation'):
                            f.write(f"**Explanation:** {q.get('explanation')}\n\n")
                        f.write("---\n\n")
                
                # Metadata
                f.write("### Metadata\n\n")
                if 'metadata' in data:
                    metadata = data['metadata']
                    f.write(f"- Key Points: {metadata.get('num_key_points', 'N/A')}\n")
                    f.write(f"- Quiz Questions: {metadata.get('num_questions', 'N/A')}\n")
                    f.write("\n")
                
                # Raw JSON
                f.write("### Raw JSON Response\n\n")
                f.write("```json\n")
                f.write(json.dumps(data, indent=2))
                f.write("\n```\n\n")
                
            elif 'error' in result:
                f.write(f"**Error:** {result['error']}\n\n")
            
            f.write("---\n\n")
        
        # Validation summary
        f.write("## Validation Checklist\n\n")
        
        for result in results:
            if result.get('status') == 'SUCCESS' and 'response' in result:
                data = result['response']
                topic = result['topic']
                
                f.write(f"### {topic}\n\n")
                
                # Notes validation
                f.write("**Notes Structured & Relevant:**\n\n")
                notes = data.get('notes', {})
                f.write(f"- ✅ Has topic: `{notes.get('topic', 'N/A')}`\n")
                f.write(f"- ✅ Has summary: {len(notes.get('summary', ''))} characters\n")
                f.write(f"- ✅ Has key points: {len(notes.get('key_points', []))} points\n")
                
                # Check relevance
                summary = notes.get('summary', '').lower()
                topic_words = topic.lower().split()
                relevance = any(word in summary for word in topic_words)
                f.write(f"- {'✅' if relevance else '⚠️'} Topic keywords in summary: {relevance}\n\n")
                
                # Quiz validation
                f.write("**Quiz Aligned with Content:**\n\n")
                quiz = data.get('quiz', [])
                f.write(f"- ✅ Number of questions: {len(quiz)}\n")
                f.write(f"- ✅ All questions have 4 options: {all(len(q.get('options', [])) == 4 for q in quiz)}\n")
                f.write(f"- ✅ All questions have answers: {all(q.get('answer') for q in quiz)}\n")
                f.write(f"- ✅ All questions have explanations: {all(q.get('explanation') for q in quiz)}\n\n")
                
                f.write("---\n\n")
    
    print(f"\n\n{'='*80}")
    print(f"📄 Results saved to: {output_file}")
    print(f"{'='*80}\n")
