"""
Quick test script for Phase 10 advanced training features.
Tests the new CLI interface, schedulers, and optimizations with minimal training.
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print results."""
    print("\n" + "="*80)
    print(f"TEST: {description}")
    print("="*80)
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
    
    if result.returncode == 0:
        print(f"\n✅ {description} - PASSED")
    else:
        print(f"\n❌ {description} - FAILED")
    
    return result.returncode == 0

def main():
    print("\n" + "="*80)
    print("PHASE 10 ADVANCED TRAINING - LOCAL TEST SUITE")
    print("="*80)
    print("\nThis will test the new training features with minimal epochs.")
    print("Each test should complete in 5-15 minutes depending on your hardware.\n")
    
    # Check if data exists
    if not os.path.exists("data/processed/train.csv"):
        print("❌ ERROR: Training data not found!")
        print("Please run preprocessing first:")
        print("  python run_preprocess.py")
        sys.exit(1)
    
    tests = []
    
    # Test 1: Basic training with new CLI
    print("\n📝 Test 1: Basic training with CLI interface")
    print("   - Tests: CLI argument parsing, default settings")
    print("   - Duration: ~5-10 minutes")
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --epochs 1 --batch-size 16",
        "Test 1: Basic CLI Training (1 epoch)"
    )
    tests.append(("Basic CLI Training", success))
    
    # Test 2: FP16 mixed precision (if GPU available)
    print("\n📝 Test 2: Mixed precision training (FP16)")
    print("   - Tests: FP16 support, automatic GPU detection")
    print("   - Duration: ~5-10 minutes")
    print("   - Note: Will auto-fallback to FP32 if no GPU")
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --epochs 1 --batch-size 16 --fp16",
        "Test 2: FP16 Mixed Precision (1 epoch)"
    )
    tests.append(("FP16 Mixed Precision", success))
    
    # Test 3: Different learning rate scheduler
    print("\n📝 Test 3: Cosine learning rate scheduler")
    print("   - Tests: LR scheduler configuration")
    print("   - Duration: ~5-10 minutes")
    print("   - Note: Edit config to use cosine scheduler")
    
    # Create a temporary config with cosine scheduler
    import yaml
    with open("config/config_transformer.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    original_scheduler = config['training']['lr_scheduler']['type']
    config['training']['lr_scheduler']['type'] = 'cosine'
    
    with open("config/config_transformer_test.yaml", 'w') as f:
        yaml.dump(config, f)
    
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --config config/config_transformer_test.yaml --epochs 1 --batch-size 16",
        "Test 3: Cosine LR Scheduler (1 epoch)"
    )
    tests.append(("Cosine LR Scheduler", success))
    
    # Cleanup temp config
    if os.path.exists("config/config_transformer_test.yaml"):
        os.remove("config/config_transformer_test.yaml")
    
    # Test 4: Cloud configuration locally
    print("\n📝 Test 4: Cloud configuration (local mode)")
    print("   - Tests: Cloud config with local mode")
    print("   - Duration: ~5-10 minutes")
    print("   - Note: Uses cloud settings but runs locally")
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --config config/config_transformer_cloud.yaml --mode local --epochs 1 --batch-size 16",
        "Test 4: Cloud Config Local Mode (1 epoch)"
    )
    tests.append(("Cloud Config Local Mode", success))
    
    # Test 5: Custom parameters
    print("\n📝 Test 5: Custom hyperparameters via CLI")
    print("   - Tests: CLI overrides for all parameters")
    print("   - Duration: ~5-10 minutes")
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --epochs 1 --batch-size 16 --learning-rate 3e-5 --output-dir models/transformer/test_custom",
        "Test 5: Custom Hyperparameters (1 epoch)"
    )
    tests.append(("Custom Hyperparameters", success))
    
    # Test 6: Early stopping disabled
    print("\n📝 Test 6: Training without early stopping")
    print("   - Tests: Early stopping disable flag")
    print("   - Duration: ~5-10 minutes")
    input("   Press Enter to continue...")
    
    success = run_command(
        "python -m src.models.transformer_training --epochs 1 --batch-size 16 --no-early-stopping",
        "Test 6: No Early Stopping (1 epoch)"
    )
    tests.append(("No Early Stopping", success))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in tests if success)
    total = len(tests)
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    print(f"Results: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 All tests passed! Phase 10 features are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
    
    print("\n📁 Trained models saved to:")
    print("   - models/transformer/distilbert/")
    print("   - models/transformer/distilbert_cloud/")
    print("   - models/transformer/test_custom/")

if __name__ == "__main__":
    main()
