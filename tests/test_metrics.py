"""
Test script to verify training metrics are valid and reasonable.
"""
import os
import json

def test_metrics():
    """Verify that training metrics are valid."""
    model_path = "models/transformer/distilbert"
    info_path = os.path.join(model_path, "training_info.json")
    
    if not os.path.exists(info_path):
        print(f"❌ Training info not found: {info_path}")
        print("   Please run training first: .\\scripts\\run_transformer_local.ps1")
        return False
    
    print("=" * 60)
    print("Validating Training Metrics")
    print("=" * 60)
    
    try:
        # Load training info
        with open(info_path, 'r') as f:
            info = json.load(f)
        
        print("\n📊 Performance Metrics:")
        print("-" * 60)
        
        metrics = info['metrics']
        
        # Display metrics
        metric_names = [
            ('accuracy', 'Accuracy'),
            ('f1_macro', 'F1 Macro'),
            ('f1_weighted', 'F1 Weighted'),
            ('precision_macro', 'Precision Macro'),
            ('recall_macro', 'Recall Macro')
        ]
        
        for key, name in metric_names:
            if key in metrics:
                value = metrics[key]
                print(f"  {name:20s}: {value:.4f}")
                
                # Validate range
                if not (0 <= value <= 1):
                    print(f"    ⚠️  WARNING: {name} out of valid range [0, 1]")
        
        # ROC-AUC (if available)
        if 'roc_auc' in metrics:
            print(f"  {'ROC-AUC':20s}: {metrics['roc_auc']:.4f}")
        elif 'roc_auc_ovr' in metrics:
            print(f"  {'ROC-AUC (OvR)':20s}: {metrics['roc_auc_ovr']:.4f}")
        
        print("\n⏱️  Timing Information:")
        print("-" * 60)
        print(f"  Training time:      {info['training_time_minutes']:.2f} minutes")
        print(f"                      ({info['training_time_seconds']:.2f} seconds)")
        print(f"  Inference time:     {info['avg_inference_time_ms']:.2f} ms/sample")
        
        print("\n🎯 Model Information:")
        print("-" * 60)
        print(f"  Number of classes:  {info['num_classes']}")
        print(f"  Classes:            {', '.join(info['classes'])}")
        
        # Validation checks
        print("\n✓ Validation Checks:")
        print("-" * 60)
        
        checks_passed = True
        
        # Check 1: Metrics in valid range
        for key, name in metric_names:
            if key in metrics:
                if 0 <= metrics[key] <= 1:
                    print(f"  ✅ {name} is in valid range [0, 1]")
                else:
                    print(f"  ❌ {name} is out of range: {metrics[key]}")
                    checks_passed = False
        
        # Check 2: Training time is positive
        if info['training_time_seconds'] > 0:
            print(f"  ✅ Training time is positive")
        else:
            print(f"  ❌ Invalid training time: {info['training_time_seconds']}")
            checks_passed = False
        
        # Check 3: Inference time is positive
        if info['avg_inference_time_ms'] > 0:
            print(f"  ✅ Inference time is positive")
        else:
            print(f"  ❌ Invalid inference time: {info['avg_inference_time_ms']}")
            checks_passed = False
        
        # Check 4: Number of classes matches
        if info['num_classes'] == len(info['classes']):
            print(f"  ✅ Number of classes matches class list")
        else:
            print(f"  ❌ Class count mismatch: {info['num_classes']} vs {len(info['classes'])}")
            checks_passed = False
        
        # Check 5: Reasonable performance (accuracy > 50% for multi-class)
        if metrics['accuracy'] > 0.5:
            print(f"  ✅ Accuracy is reasonable (> 50%)")
        else:
            print(f"  ⚠️  Low accuracy: {metrics['accuracy']:.4f} (may need more training)")
        
        # Performance assessment
        print("\n📈 Performance Assessment:")
        print("-" * 60)
        
        accuracy = metrics['accuracy']
        f1_macro = metrics['f1_macro']
        
        if accuracy >= 0.90 and f1_macro >= 0.85:
            print("  🌟 EXCELLENT - Model performs very well!")
        elif accuracy >= 0.85 and f1_macro >= 0.75:
            print("  ✅ GOOD - Model performs well")
        elif accuracy >= 0.75 and f1_macro >= 0.65:
            print("  👍 FAIR - Model performs adequately")
        elif accuracy >= 0.60 and f1_macro >= 0.50:
            print("  ⚠️  POOR - Consider more training or hyperparameter tuning")
        else:
            print("  ❌ VERY POOR - Model needs significant improvement")
        
        print("\n" + "=" * 60)
        if checks_passed:
            print("✅ ALL VALIDATION CHECKS PASSED!")
        else:
            print("⚠️  SOME VALIDATION CHECKS FAILED")
        print("=" * 60)
        
        return checks_passed
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_metrics()
    exit(0 if success else 1)
