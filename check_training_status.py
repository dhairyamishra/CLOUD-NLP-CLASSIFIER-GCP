#!/usr/bin/env python3
"""
Quick script to check if training is actually stuck or just slow.
Run this in a separate terminal while training is running.
"""

import psutil
import time
import sys
from pathlib import Path

def check_python_processes():
    """Check all Python processes and their resource usage."""
    python_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'create_time']):
        try:
            if 'python' in proc.info['name'].lower():
                python_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return python_processes

def format_bytes(bytes_val):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def format_time(seconds):
    """Format seconds to human-readable format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def check_training_files():
    """Check for recent training activity."""
    model_dirs = [
        Path("models/baselines"),
        Path("models/transformer/distilbert"),
        Path("models/transformer/distilbert_fullscale")
    ]
    
    recent_files = []
    current_time = time.time()
    
    for model_dir in model_dirs:
        if model_dir.exists():
            for file_path in model_dir.rglob("*"):
                if file_path.is_file():
                    mtime = file_path.stat().st_mtime
                    age = current_time - mtime
                    if age < 600:  # Files modified in last 10 minutes
                        recent_files.append((file_path, age))
    
    return recent_files

def main():
    """Main diagnostic function."""
    print("=" * 70)
    print("TRAINING STATUS CHECKER")
    print("=" * 70)
    print("\nChecking Python processes...\n")
    
    # Check Python processes
    python_procs = check_python_processes()
    
    if not python_procs:
        print("❌ No Python processes found!")
        print("   Training may have crashed or not started yet.")
        return
    
    print(f"✓ Found {len(python_procs)} Python process(es)\n")
    
    # Monitor for 10 seconds
    print("Monitoring CPU usage for 10 seconds...\n")
    
    for i in range(10):
        print(f"[{i+1}/10] ", end="", flush=True)
        
        total_cpu = 0
        total_memory = 0
        
        for proc in python_procs:
            try:
                cpu = proc.cpu_percent(interval=1)
                mem = proc.memory_info().rss
                total_cpu += cpu
                total_memory += mem
                
                runtime = time.time() - proc.create_time()
                
                print(f"PID {proc.pid}: CPU={cpu:.1f}% | Memory={format_bytes(mem)} | Runtime={format_time(runtime)}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print(f"PID {proc.pid}: Process ended")
        
        if i < 9:
            print()
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    avg_cpu = total_cpu / len(python_procs)
    
    if avg_cpu > 50:
        print("✅ TRAINING IS ACTIVE")
        print(f"   Average CPU usage: {avg_cpu:.1f}%")
        print("   Status: Training is running normally")
        print("   Action: Be patient, training takes time!")
    elif avg_cpu > 10:
        print("⚠️  TRAINING IS SLOW")
        print(f"   Average CPU usage: {avg_cpu:.1f}%")
        print("   Status: Training is running but slow")
        print("   Possible causes:")
        print("   - CPU training (very slow, expected)")
        print("   - Waiting for I/O operations")
        print("   - In tokenization phase (no CPU usage shown)")
    elif avg_cpu > 0.1:
        print("⚠️  TRAINING MAY BE STUCK")
        print(f"   Average CPU usage: {avg_cpu:.1f}%")
        print("   Status: Very low CPU activity")
        print("   Possible causes:")
        print("   - DataLoader worker deadlock (Windows)")
        print("   - Waiting for user input")
        print("   - Between training phases")
        print("   Action: Check console output for errors")
    else:
        print("❌ TRAINING APPEARS STUCK")
        print(f"   Average CPU usage: {avg_cpu:.1f}%")
        print("   Status: No CPU activity detected")
        print("   Action: Process may be deadlocked")
        print("   Recommendation: Kill process and restart with dataloader_num_workers=0")
    
    # Check for recent file activity
    print("\n" + "=" * 70)
    print("RECENT FILE ACTIVITY")
    print("=" * 70)
    
    recent_files = check_training_files()
    
    if recent_files:
        print(f"✓ Found {len(recent_files)} recently modified file(s):\n")
        for file_path, age in sorted(recent_files, key=lambda x: x[1])[:5]:
            print(f"   {file_path.name} (modified {format_time(age)} ago)")
        print("\n   Status: Training is making progress!")
    else:
        print("⚠️  No recently modified files found")
        print("   This could mean:")
        print("   - Training just started (no checkpoints yet)")
        print("   - Training is stuck before first checkpoint")
        print("   - Check console for current phase")
    
    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    
    if avg_cpu > 50:
        print("✅ Everything looks good! Training is active.")
        print("   - Continue waiting for training to complete")
        print("   - Check console for progress updates")
    elif avg_cpu > 10:
        print("⚠️  Training is slow but active.")
        print("   - If on CPU: This is normal, training takes hours")
        print("   - If on GPU: Check GPU utilization with nvidia-smi")
        print("   - Consider reducing batch size or sequence length")
    else:
        print("❌ Training appears stuck or deadlocked.")
        print("   1. Check console output for error messages")
        print("   2. If stuck at 'Starting training...', likely DataLoader issue")
        print("   3. Kill process: Stop-Process -Name python -Force")
        print("   4. Fix configs: Set dataloader_num_workers: 0")
        print("   5. Restart training")
    
    print("\n" + "=" * 70)
    print("For detailed diagnosis, see: docs/TRAINING_STALL_DIAGNOSIS.md")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
