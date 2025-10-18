"""
Test script for Medical FAQ Bot RAG Pipeline
Tests the /ask endpoint directly for debugging and validation
"""

import requests
import json
import time

# Configuration
API_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_query(query):
    """Test a single query"""
    print("\n" + "=" * 60)
    print(f"Testing Query: {query}")
    print("=" * 60)
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        
        elapsed_time = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Client-side Latency: {elapsed_time:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\nAnswer: {data.get('answer', 'N/A')}")
            print(f"\nConfidence: {data.get('confidence', 'N/A')}")
            print(f"Server Latency: {data.get('latency', 'N/A')}s")
            print(f"Cached: {data.get('cached', False)}")
            
            sources = data.get('sources', [])
            if sources:
                print(f"\nSources ({len(sources)}):")
                for source in sources:
                    print(f"  {source['id']}. {source['content'][:100]}...")
            
            return True
        else:
            print(f"Error Response: {json.dumps(response.json(), indent=2)}")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def test_multiple_queries():
    """Test multiple diverse queries"""
    test_queries = [
        "What are the symptoms of diabetes?",
        "How can I prevent heart disease?",
        "What is hypertension?",
        "How much sleep do adults need?",
        "What are the symptoms of diabetes?",  # Duplicate to test caching
        "What foods help lower cholesterol?",
        "What are the warning signs of a stroke?",
    ]
    
    results = []
    
    for query in test_queries:
        result = test_query(query)
        results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total Queries: {len(results)}")
    print(f"Successful: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    print(f"Success Rate: {(sum(results) / len(results) * 100):.1f}%")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("Testing Edge Cases")
    print("=" * 60)
    
    # Empty query
    print("\n1. Testing empty query...")
    response = requests.post(f"{API_URL}/ask", json={"query": ""})
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Very long query
    print("\n2. Testing very long query...")
    long_query = "What are symptoms? " * 100
    response = requests.post(f"{API_URL}/ask", json={"query": long_query})
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Missing query field
    print("\n3. Testing missing query field...")
    response = requests.post(f"{API_URL}/ask", json={})
    print(f"Status: {response.status_code} (Expected: 400)")
    
    # Non-medical query
    print("\n4. Testing non-medical query...")
    test_query("What is the capital of France?")

def main():
    """Main test runner"""
    print("\n")
    print("*" * 60)
    print("Medical FAQ Bot - RAG Pipeline Test Suite")
    print("*" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Server is not running. Please start the Flask backend first.")
        print("Run: cd backend && python main.py")
        return
    
    print("\n✅ Server is running!")
    
    # Test 2: Multiple queries
    test_multiple_queries()
    
    # Test 3: Edge cases
    test_edge_cases()
    
    print("\n" + "*" * 60)
    print("Testing Complete!")
    print("*" * 60 + "\n")

if __name__ == "__main__":
    main()
