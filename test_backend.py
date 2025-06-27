#!/usr/bin/env python3
"""
Simple test script to verify backend functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from backend.app.config import settings
        print("✅ Config imported successfully")
        
        from backend.app.agents import Cara, Penny, Eva
        print("✅ Agents imported successfully")
        
        from backend.app.schemas import ChatRequest, ChatResponse
        print("✅ Schemas imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_agent_creation():
    """Test agent creation (without OpenAI API)"""
    try:
        from backend.app.agents import Cara, Penny, Eva
        
        # Test agent instantiation (will fail without OpenAI key, but should create objects)
        cara = Cara()
        penny = Penny()
        eva = Eva()
        
        print("✅ Agent objects created successfully")
        print(f"   Cara prompt length: {len(cara.system_prompt)} characters")
        print(f"   Penny prompt length: {len(penny.system_prompt)} characters")
        print(f"   Eva prompt length: {len(eva.system_prompt)} characters")
        
        return True
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False

def test_schemas():
    """Test Pydantic schemas"""
    try:
        from backend.app.schemas import ChatRequest, ChatResponse, NoteRequest
        
        # Test schema creation
        chat_req = ChatRequest(message="Hello", context="Test")
        note_req = NoteRequest(content="Test note", metadata={"test": True})
        
        print("✅ Schemas created successfully")
        print(f"   ChatRequest: {chat_req.message}")
        print(f"   NoteRequest: {note_req.content}")
        
        return True
    except Exception as e:
        print(f"❌ Schema test failed: {e}")
        return False

def main():
    print("🧪 Testing AI Assistant Platform Backend")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Agent Creation Test", test_agent_creation),
        ("Schema Test", test_schemas),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is ready.")
        print("\n📝 Next steps:")
        print("1. Set your OPENAI_API_KEY in .env file")
        print("2. Ensure PostgreSQL is running at postgres.home.lan:5432")
        print("3. Run: ./start.sh")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 