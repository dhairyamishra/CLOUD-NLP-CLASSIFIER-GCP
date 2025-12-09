"""
Verification script to confirm Phase 10 advanced training features are present.
Run this BEFORE training to ensure you have the new implementation.
"""
import os
import sys

def check_file_features(filepath, features_to_check):
    """Check if a file contains specific features."""
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False, {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    results = {}
    for feature_name, search_terms in features_to_check.items():
        if isinstance(search_terms, str):
            results[feature_name] = search_terms in content
        else:  # list of terms - all must be present
            results[feature_name] = all(term in content for term in search_terms)
    
    return True, results

def main():
    print("="*80)
    print("PHASE 10 VERIFICATION - Advanced Training Features")
    print("="*80)
    print("\nThis script verifies that Phase 10 features are properly installed.")
    print("Run this BEFORE training to ensure you have the new implementation.\n")
    
    all_checks_passed = True
    
    # Check 1: Training script features
    print("="*80)
    print("CHECK 1: Training Script (src/models/transformer_training.py)")
    print("="*80)
    
    training_features = {
        "CLI Argument Parsing (argparse)": ["import argparse", "def parse_args"],
        "Cloud Training Mode": ["--mode", "choices=[\"local\", \"cloud\"]"],
        "Configuration Overrides": "def apply_cli_overrides",
        "Advanced LR Schedulers": ["lr_scheduler_type", "scheduler_mapping"],
        "FP16 Validation": ["fp16_enabled", "torch.cuda.is_available()"],
        "Enhanced Training Logging": "Training Configuration:",
        "Warmup Steps Support": "warmup_steps",
        "DataLoader Optimizations": "dataloader_num_workers",
    }
    
    exists, results = check_file_features("src/models/transformer_training.py", training_features)
    
    if exists:
        for feature, present in results.items():
            status = "✅" if present else "❌"
            print(f"{status} {feature}")
            if not present:
                all_checks_passed = False
    else:
        all_checks_passed = False
    
    # Check 2: Configuration files
    print("\n" + "="*80)
    print("CHECK 2: Configuration Files")
    print("="*80)
    
    config_files = {
        "config/config_transformer.yaml": "Local training config",
        "config/config_transformer_cloud.yaml": "Cloud training config",
    }
    
    for config_file, description in config_files.items():
        if os.path.exists(config_file):
            print(f"✅ {description}: {config_file}")
        else:
            print(f"❌ {description}: {config_file} NOT FOUND")
            all_checks_passed = False
    
    # Check 3: Cloud training scripts
    print("\n" + "="*80)
    print("CHECK 3: Cloud Training Scripts")
    print("="*80)
    
    scripts = {
        "scripts/setup_gcp_training.sh": "GCP setup script",
        "scripts/run_gcp_training.sh": "GCP training script",
        "scripts/run_transformer_cloud.ps1": "Windows cloud script",
    }
    
    for script_file, description in scripts.items():
        if os.path.exists(script_file):
            print(f"✅ {description}: {script_file}")
        else:
            print(f"⚠️  {description}: {script_file} NOT FOUND (optional)")
    
    # Check 4: Documentation
    print("\n" + "="*80)
    print("CHECK 4: Documentation")
    print("="*80)
    
    docs = {
        "docs/PHASE10_ADVANCED_TRAINING_SUMMARY.md": "Phase 10 summary",
        "docs/TESTING_ADVANCED_TRAINING.md": "Testing guide",
    }
    
    for doc_file, description in docs.items():
        if os.path.exists(doc_file):
            print(f"✅ {description}: {doc_file}")
        else:
            print(f"⚠️  {description}: {doc_file} NOT FOUND (optional)")
    
    # Check 5: Test scripts
    print("\n" + "="*80)
    print("CHECK 5: Test Scripts")
    print("="*80)
    
    test_scripts = {
        "quick_test_training.py": "Quick test script",
        "test_advanced_training.py": "Full test suite",
    }
    
    for test_file, description in test_scripts.items():
        if os.path.exists(test_file):
            print(f"✅ {description}: {test_file}")
        else:
            print(f"⚠️  {description}: {test_file} NOT FOUND (optional)")
    
    # Final verdict
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)
    
    if all_checks_passed:
        print("\n✅ ALL CRITICAL CHECKS PASSED!")
        print("✅ Phase 10 advanced training features are properly installed")
        print("✅ You are using the NEW training implementation")
        print("\n🚀 You can now run training with confidence:")
        print("   python quick_test_training.py")
        print("   OR")
        print("   python -m src.models.transformer_training --epochs 1 --batch-size 16")
    else:
        print("\n❌ SOME CHECKS FAILED!")
        print("⚠️  Phase 10 features may not be fully installed")
        print("\n🔧 Possible solutions:")
        print("   1. Make sure you're in the correct directory")
        print("   2. Pull the latest changes from git")
        print("   3. Re-run the Phase 10 implementation")
        print("   4. Check that all files were created correctly")
    
    print("\n" + "="*80)
    
    # Show what to look for during training
    if all_checks_passed:
        print("\n📋 WHAT TO LOOK FOR DURING TRAINING:")
        print("="*80)
        print("\nWhen you run training, you should see these Phase 10 indicators:")
        print("\n1. At the start:")
        print("   ✓ 'Training mode: local' (or 'cloud')")
        print("   ✓ 'Configuration loaded from: ...'")
        print("\n2. During setup:")
        print("   ✓ 'Using learning rate scheduler: linear' (or cosine, etc.)")
        print("   ✓ 'FP16 mixed precision training enabled' (if GPU)")
        print("   ✓ 'Early stopping enabled with patience: X'")
        print("\n3. Configuration section:")
        print("   ✓ '============================================================'")
        print("   ✓ 'Training Configuration:'")
        print("   ✓ '  Epochs: X'")
        print("   ✓ '  Train Batch Size: X'")
        print("   ✓ '  Learning Rate: X'")
        print("   ✓ '  LR Scheduler: [type]'")
        print("   ✓ '  FP16: True/False'")
        print("   ✓ '============================================================'")
        print("\n4. At the end:")
        print("   ✓ 'Training pipeline completed successfully!'")
        print("\nIf you see ALL of these, you're definitely using Phase 10! ✅")
        print("="*80)
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
