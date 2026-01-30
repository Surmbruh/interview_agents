import sys
try:
    print("🔍 Testing imports...")
    import graph
    print("✅ Graph compiled successfully")
    import main
    print("✅ Main logic loaded")
    print("🚀 All smoke tests passed!")
except Exception as e:
    print(f"❌ Smoke test failed: {e}")
    sys.exit(1)
