#!/usr/bin/env python3
"""
Test script for Djinn Council GUI components
"""

import sys
import subprocess
import json
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter - OK")
    except ImportError:
        print("❌ tkinter - FAILED")
        return False
    
    try:
        import ollama
        print("✅ ollama - OK") 
    except ImportError:
        print("❌ ollama - FAILED (run: pip install ollama)")
        return False
    
    try:
        from advanced_djinn_council import AdvancedDjinnCouncil
        print("✅ advanced_djinn_council - OK")
    except ImportError as e:
        print(f"❌ advanced_djinn_council - FAILED: {e}")
        return False
    
    return True

def test_ollama_connection():
    """Test Ollama service connection"""
    print("\n🧪 Testing Ollama connection...")
    
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout.strip().split('\n')[1:]  # Skip header
            model_count = len([line for line in models if line.strip()])
            print(f"✅ Ollama connection - OK ({model_count} models available)")
            
            # Show available models
            print("   Available models:")
            for line in models:
                if line.strip():
                    model_name = line.split()[0]
                    print(f"     - {model_name}")
            return True
        else:
            print("❌ Ollama connection - FAILED (service not running?)")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Ollama connection - TIMEOUT")
        return False
    except FileNotFoundError:
        print("❌ Ollama connection - NOT INSTALLED")
        return False
    except Exception as e:
        print(f"❌ Ollama connection - ERROR: {e}")
        return False

def test_config_files():
    """Test configuration file handling"""
    print("\n🧪 Testing configuration files...")
    
    # Test advanced config
    config_file = Path("advanced_djinn_config.json")
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✅ advanced_djinn_config.json - OK")
            
            # Check required sections
            if 'roles' in config:
                print(f"   Found {len(config['roles'])} djinn roles")
            else:
                print("   ⚠️  No 'roles' section found")
                
        except json.JSONDecodeError as e:
            print(f"❌ advanced_djinn_config.json - INVALID JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ advanced_djinn_config.json - ERROR: {e}")
            return False
    else:
        print("⚠️  advanced_djinn_config.json - NOT FOUND (will be created)")
    
    return True

def test_council_initialization():
    """Test basic council initialization"""
    print("\n🧪 Testing council initialization...")
    
    try:
        from advanced_djinn_council import AdvancedDjinnCouncil
        
        # Try to initialize council
        council = AdvancedDjinnCouncil()
        print("✅ Council initialization - OK")
        
        # Test status
        status = council.get_system_status()
        print(f"   Council state: {status['current_state']}")
        print(f"   Available djinn: {len(status['available_djinn'])}")
        print(f"   Active workers: {status['active_workers']}")
        
        # Cleanup
        council.shutdown()
        print("✅ Council shutdown - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Council initialization - FAILED: {e}")
        return False

def test_gui_components():
    """Test GUI component creation (without showing GUI)"""
    print("\n🧪 Testing GUI components...")
    
    try:
        import tkinter as tk
        from djinn_council_gui import OllamaModelManager, DjinnResponseWidget
        
        # Test model manager
        model_manager = OllamaModelManager()
        print(f"✅ OllamaModelManager - OK ({len(model_manager.available_models)} models)")
        
        # Test widget creation (create but don't show)
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        widget = DjinnResponseWidget(root, "Test Djinn", "test_role")
        print("✅ DjinnResponseWidget - OK")
        
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI components - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("🜂 Djinn Council GUI Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_ollama_connection,
        test_config_files,
        test_council_initialization,
        test_gui_components
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} - EXCEPTION: {e}")
            failed += 1
    
    print("\n" + "=" * 40)
    print(f"🜂 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! Ready to launch GUI.")
        print("\nTo start the GUI, run:")
        print("  python djinn_council_gui.py")
        print("  or")
        print("  launch_djinn_gui.bat")
    else:
        print("❌ Some tests failed. Please resolve issues before launching GUI.")
        
        print("\nCommon solutions:")
        print("1. Install ollama: pip install ollama")
        print("2. Start Ollama service: ollama serve")
        print("3. Install a model: ollama pull llama3.2")
        print("4. Check Python version (3.7+ required)")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)