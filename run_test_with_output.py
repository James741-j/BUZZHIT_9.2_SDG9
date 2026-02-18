"""
Wrapper script to run tests with captured output
"""
import subprocess
import sys
import os

# Set UTF-8 encoding for output
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("🌍 CLIMATWIN - Running Tests...")
print("=" * 70)

try:
    # Run the test script with UTF-8 encoding
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    result = subprocess.run(
        [sys.executable, "test_platform.py"],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
        encoding='utf-8'
    )
    
    # Print stdout
    print(result.stdout)
    
    # Print stderr if any
    if result.stderr:
        print("\nSTDERR:", result.stderr, file=sys.stderr)
    
    # Exit with same code as the test
    sys.exit(result.returncode)
    
except subprocess.TimeoutExpired:
    print("❌ Tests timed out after 60 seconds")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error running tests: {e}")
    sys.exit(1)
