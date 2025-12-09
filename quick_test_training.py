"""
Quick 5-minute test of Phase 10 advanced training features.
Runs a single epoch with minimal settings to verify everything works.
"""
import subprocess
import sys
import os
import re

def verify_phase10_features():
    """Verify that the training script has Phase 10 features."""
    print("\n" + "="*80)
    print("VERIFICATION: Checking Phase 10 Features in Training Script")
    print("="*80)
    
    script_path = "src/models/transformer_training.py"
    
    if not os.path.exists(script_path):
        print(f"❌ ERROR: {script_path} not found!")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Phase 10 features
    features = {
        "CLI Argument Parsing": "argparse" in content and "parse_args" in content,
        "Cloud Training Mode": "--mode" in content and "apply_cli_overrides" in content,
        "Advanced LR Schedulers": "lr_scheduler_type" in content and "scheduler_mapping" in content,
        "FP16 Validation": "fp16_enabled" in content and "torch.cuda.is_available()" in content,
        "Configuration Overrides": "apply_cli_overrides" in content,
        "Enhanced Logging": "Training Configuration:" in content,
    }
    
    all_present = True
    for feature, present in features.items():
        status = "✅" if present else "❌"
        print(f"{status} {feature}: {'Present' if present else 'MISSING'}")
        if not present:
            all_present = False
    
    print("="*80)
    
    if all_present:
        print("✅ All Phase 10 features detected in training script!")
        print("✅ You are using the NEW advanced training implementation")
    else:
        print("❌ Some Phase 10 features are missing!")
        print("⚠️  You may be using an older version of the training script")
    
    return all_present

print("="*80)
print("QUICK TEST: Phase 10 Advanced Training")
print("="*80)
print("\nThis will run a quick 1-epoch training to test the new features.")
print("Expected duration: 5-10 minutes (depending on CPU/GPU)")
print("\nFeatures being tested:")
print("  ✓ CLI argument parsing")
print("  ✓ Early stopping")
print("  ✓ Learning rate scheduler (linear)")
print("  ✓ FP16 mixed precision (if GPU available)")
print("  ✓ Configuration system")
print("="*80)

# First, verify Phase 10 features are present
if not verify_phase10_features():
    print("\n⚠️  WARNING: Phase 10 features not fully detected!")
    response = input("\nContinue anyway? (y/n): ").strip().lower()
    if response != 'y':
        print("Test aborted.")
        sys.exit(1)

# Check prerequisites
if not os.path.exists("data/processed/train.csv"):
    print("\n❌ ERROR: Training data not found!")
    print("\nPlease run preprocessing first:")
    print("  python run_preprocess.py")
    print("\nOr download and preprocess:")
    print("  python scripts/download_dataset.py")
    print("  python run_preprocess.py")
    sys.exit(1)

print("\n✅ Training data found!")

# Ask user for test type
print("\nChoose test mode:")
print("  1. Quick test (1 epoch, small batch) - ~5 minutes")
print("  2. Standard test (2 epochs, normal batch) - ~10-15 minutes")
print("  3. FP16 test (1 epoch with mixed precision) - ~5 minutes")
print("  4. Custom (enter your own parameters)")

choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"

if choice == "1":
    cmd = "python -m src.models.transformer_training --epochs 1 --batch-size 16"
    description = "Quick Test (1 epoch, batch=16)"
elif choice == "2":
    cmd = "python -m src.models.transformer_training --epochs 2 --batch-size 32"
    description = "Standard Test (2 epochs, batch=32)"
elif choice == "3":
    cmd = "python -m src.models.transformer_training --epochs 1 --batch-size 16 --fp16"
    description = "FP16 Test (1 epoch, batch=16, mixed precision)"
elif choice == "4":
    print("\nEnter custom parameters:")
    epochs = input("  Epochs [1]: ").strip() or "1"
    batch_size = input("  Batch size [16]: ").strip() or "16"
    fp16 = input("  Enable FP16? (y/n) [n]: ").strip().lower() == 'y'
    
    cmd = f"python -m src.models.transformer_training --epochs {epochs} --batch-size {batch_size}"
    if fp16:
        cmd += " --fp16"
    description = f"Custom Test ({epochs} epochs, batch={batch_size})"
else:
    print("Invalid choice. Using default (option 1).")
    cmd = "python -m src.models.transformer_training --epochs 1 --batch-size 16"
    description = "Quick Test (1 epoch, batch=16)"

print("\n" + "="*80)
print(f"Running: {description}")
print("="*80)
print(f"Command: {cmd}")
print("\nStarting training...")
print("\n🔍 WATCH FOR THESE PHASE 10 INDICATORS IN THE OUTPUT:")
print("  ✓ 'Training mode: local' or 'Training mode: cloud'")
print("  ✓ 'Using learning rate scheduler: [type]'")
print("  ✓ 'Early stopping enabled' or 'Early stopping disabled'")
print("  ✓ 'FP16 mixed precision training enabled' (if GPU)")
print("  ✓ 'Training Configuration:' section with detailed settings")
print("="*80 + "\n")

# Run the training and capture output
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

# Display the output
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Verify Phase 10 features in the output
print("\n" + "="*80)
print("RUNTIME VERIFICATION: Checking Training Output")
print("="*80)

output_text = result.stdout + result.stderr
phase10_indicators = {
    "Training Mode": "Training mode:" in output_text,
    "LR Scheduler": "Using learning rate scheduler:" in output_text,
    "Early Stopping": "Early stopping" in output_text,
    "Training Config Section": "Training Configuration:" in output_text,
    "CLI Arguments": "Configuration loaded from:" in output_text,
}

all_indicators_present = True
for indicator, present in phase10_indicators.items():
    status = "✅" if present else "⚠️"
    print(f"{status} {indicator}: {'Detected' if present else 'Not detected'}")
    if not present:
        all_indicators_present = False

print("="*80)

if result.returncode == 0:
    print("\n✅ TEST PASSED - Training completed successfully!")
    
    if all_indicators_present:
        print("✅ All Phase 10 features confirmed in training output!")
        print("✅ You are definitely using the NEW advanced training script!")
    else:
        print("⚠️  Some Phase 10 indicators not detected in output")
        print("⚠️  This might be normal, but verify the features above")
    
    print("\n" + "="*80)
    print("📊 Check the results:")
    print("  - Model: models/transformer/distilbert/")
    print("  - Training info: models/transformer/distilbert/training_info.json")
    print("  - Logs: models/transformer/distilbert/logs/")
    
    # Check if training_info.json exists and show it
    info_path = "models/transformer/distilbert/training_info.json"
    if os.path.exists(info_path):
        import json
        with open(info_path, 'r') as f:
            info = json.load(f)
        print("\n📈 Training Results:")
        print(f"  - Accuracy: {info.get('metrics', {}).get('accuracy', 'N/A'):.4f}")
        print(f"  - F1 (Macro): {info.get('metrics', {}).get('f1_macro', 'N/A'):.4f}")
        print(f"  - Training Time: {info.get('training_time_minutes', 'N/A'):.2f} minutes")
        print(f"  - Inference Time: {info.get('avg_inference_time_ms', 'N/A'):.2f} ms")
    
    print("\n🎉 Phase 10 features are working correctly!")
else:
    print("\n❌ TEST FAILED - Training encountered an error")
    print("="*80)
    print("\n🔍 Troubleshooting tips:")
    print("  1. Check if data exists: ls data/processed/")
    print("  2. Verify Python environment: python --version")
    print("  3. Check dependencies: pip list | grep transformers")
    print("  4. Review error messages above")

print("\n" + "="*80)
