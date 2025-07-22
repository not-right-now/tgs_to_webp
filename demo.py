#!/usr/bin/env python3
"""
Comprehensive demo of the TGS to WebP Converter with automatic timing preservation.

This demo shows various usage patterns and provides detailed information about
the conversion process and results.
"""

import shutil
from tgs_to_webp import convert_tgs_to_webp, TGSToWebPConverter
from lottie.parsers.tgs import parse_tgs
from PIL import Image
import os
import glob
import time

def analyze_tgs_file(file_path):
    """Analyze a TGS file and return detailed information."""
    try:
        print(f"    📁 Analyzing: {os.path.basename(file_path)}")
        
        with open(file_path, 'rb') as f:
            lottie_animation = parse_tgs(f)
        
        total_frames = int(lottie_animation.out_point - lottie_animation.in_point)
        fps = lottie_animation.frame_rate
        duration = total_frames / fps
        
        print(f"    ⏱️  Original: {total_frames} frames at {fps} FPS")
        print(f"    🕐 Duration: {duration:.3f} seconds")
        return total_frames, fps, duration
        
    except Exception as e:
        print(f"    ❌ Analysis failed: {e}")
        return None, None, None

def analyze_webp_output(file_path):
    """Analyze WebP output and return information."""
    if not os.path.exists(file_path):
        print(f"    ❌ Output file not found: {file_path}")
        return False
    
    try:
        img = Image.open(file_path)
        size_bytes = os.path.getsize(file_path)
        
        print(f"    ✅ Output: {img.n_frames} frames, {size_bytes:,} bytes")
        print(f"    📐 Resolution: {img.size[0]}x{img.size[1]}")
        print(f"    🎬 Format: {img.format}, Animated: {img.is_animated}")
        
        # Try to get frame duration info
        if hasattr(img, 'info') and 'duration' in img.info:
            frame_duration_ms = img.info['duration']
            effective_fps = 1000 / frame_duration_ms if frame_duration_ms > 0 else 0
            effective_duration = img.n_frames * frame_duration_ms / 1000
            print(f"    🎯 Effective: {effective_fps:.1f} FPS, {effective_duration:.3f}s duration")
        
        return True
    except Exception as e:
        print(f"    ❌ Output analysis failed: {e}")
        return False

def demo_basic_conversion():
    """Demo 1: Basic conversion with automatic timing preservation."""
    print("🟢 Demo 1: Basic Conversion (Recommended)")
    print("=" * 50)
    print("Using simple convert_tgs_to_webp() with automatic timing preservation\nDimensions: Original  Quality: Default(80)")
    
    input_files = glob.glob("demo_inp/*.tgs")
    if not input_files:
        print("❌ No TGS files found in demo_inp/")
        return False
    
    success_count = 0
    for i, input_file in enumerate(input_files, 1):
        print(f"\n📂 Converting file {i}/{len(input_files)}")
        
        # Analyze input
        orig_frames, orig_fps, orig_duration = analyze_tgs_file(input_file)
        
        # Convert with automatic timing
        output_file = f"demo_out/basic_{i}.webp"
        print(f"    🔄 Converting with automatic timing preservation...")
        
        start_time = time.time()
        success = convert_tgs_to_webp(input_file, output_file)
        conversion_time = time.time() - start_time
        
        if success:
            print(f"    ⏱️  Conversion took {conversion_time:.2f} seconds")
            analyze_webp_output(output_file)
            success_count += 1
        else:
            print(f"    ❌ Conversion failed")
    
    print(f"\n📊 Basic Conversion Summary: {success_count}/{len(input_files)} successful")
    return success_count > 0

def demo_custom_settings():
    """Demo 2: Custom resolution and quality settings."""
    print("\n\n🟡 Demo 2: Custom Resolution & Quality")
    print("=" * 50)
    print("Using custom width, height, and quality settings\nAutomatic timing preservation: Enabled")
    
    input_files = glob.glob("demo_inp/*.tgs")
    if not input_files:
        return False
    
    # Different resolution settings to test
    settings = [
        {"width": 256, "height": 256, "quality": 95, "name": "256x256_Q95"},
        {"width": 400, "height": 400, "quality": 80, "name": "400x400_Q80_default"},
        {"width": 800, "height": 800, "quality": 60, "name": "800x800_Q60"}
    ]
    
    for setting in settings:
        print(f"\n📐 Testing {setting['width']}x{setting['height']} at {setting['quality']}% quality")
        
        input_file = input_files[0]  # Use first file
        output_file = f"demo_out/custom_{setting['name']}.webp"
        
        analyze_tgs_file(input_file)
        
        print(f"    🔄 Converting...")
        start_time = time.time()
        success = convert_tgs_to_webp(
            input_file, 
            output_file,
            width=setting['width'],
            height=setting['height'],
            quality=setting['quality']
        )
        conversion_time = time.time() - start_time
        
        if success:
            print(f"    ⏱️  Conversion took {conversion_time:.2f} seconds")
            analyze_webp_output(output_file)
        else:
            print(f"    ❌ Conversion failed")

def demo_class_usage():
    """Demo 3: Using the TGSToWebPConverter class."""
    print("\n\n🟣 Demo 3: Class-Based Usage")
    print("=" * 50)
    print("Using TGSToWebPConverter class for advanced control")
    
    input_files = glob.glob("demo_inp/*.tgs")
    if not input_files:
        return False
    
    # Create converter with custom settings
    converter = TGSToWebPConverter(
        width=512,
        height=512,
        quality=85,
        preserve_timing=True
    )
    
    print(f"📝 Converter configured: 512x512, 85% quality, timing preservation enabled")
    
    for i, input_file in enumerate(input_files, 1):
        print(f"\n📂 Processing file {i}/{len(input_files)} with class")
        
        analyze_tgs_file(input_file)
        
        output_file = f"demo_out/class_{i}.webp"
        print(f"    🔄 Converting using class method...")
        
        start_time = time.time()
        success = converter.convert(input_file, output_file)
        conversion_time = time.time() - start_time
        
        if success:
            print(f"    ⏱️  Conversion took {conversion_time:.2f} seconds")
            analyze_webp_output(output_file)
        else:
            print(f"    ❌ Conversion failed")

def demo_manual_timing():
    """Demo 4: Manual timing control (advanced)."""
    print("\n\n🔴 Demo 4: Manual Timing Override (Advanced)")
    print("=" * 50)
    print("Demonstrating manual FPS control by disabling automatic timing\nResolution: Original and Quality: Default")
    
    input_files = glob.glob("demo_inp/*.tgs")
    if not input_files:
        return False
    
    input_file = input_files[0]  # Use first file
    
    print(f"🎛️  Testing manual FPS settings on: {os.path.basename(input_file)}")
    analyze_tgs_file(input_file)
    
    # Test different manual FPS settings
    fps_settings = [15, 30, 60]
    
    for fps in fps_settings:
        print(f"\n🎯 Manual FPS: {fps}")
        output_file = f"demo_out/manual_fps_{fps}.webp"
        
        print(f"    🔄 Converting with preserve_timing=False, fps={fps}...")
        start_time = time.time()
        success = convert_tgs_to_webp(
            input_file, 
            output_file,
            fps=fps,
            preserve_timing=False  # Disable automatic timing
        )
        conversion_time = time.time() - start_time
        
        if success:
            print(f"    ⏱️  Conversion took {conversion_time:.2f} seconds")
            analyze_webp_output(output_file)
        else:
            print(f"    ❌ Conversion failed")

def main():
    print("🎬 TGS to WebP Converter - Comprehensive Demo")
    print("=" * 60)
    print("This demo shows the automatic timing preservation feature")
    print("and various usage patterns of the converter.\n")
    
    # Create output directory
    os.makedirs("demo_out", exist_ok=True)
    
    # Check for input files
    input_files = glob.glob("demo_inp/*.tgs")
    if not input_files:
        print("❌ No TGS files found in demo_inp/ directory")
        print("Please add some .tgs files to demo_inp/ and run again.")
        return
    
    print(f"📁 Found {len(input_files)} TGS files in demo_inp/:")
    for f in input_files:
        print(f"   • {os.path.basename(f)}")
    
    #Output directory cleanup before running demo
    print("\n🧹 Clearing previous demo outputs...")
    if os.path.exists("demo_out"):
        shutil.rmtree("demo_out")
    os.makedirs("demo_out", exist_ok=True) # Recreate the empty directory

    # Run all demos
    try:
        demo_basic_conversion()
        demo_custom_settings()  
        demo_class_usage()
        demo_manual_timing()
        
        print("\n\n🎉 Demo Complete!")
        print("=" * 60)
        print("Key takeaways:")
        print("✅ Automatic timing preservation works perfectly")
        print("✅ Simple API: convert_tgs_to_webp('input.tgs', 'output.webp')")
        print("✅ Custom settings available for resolution and quality")
        print("✅ Class-based usage for advanced scenarios")
        print("✅ Manual timing override available when needed")
        
        print(f"\n📂 Check demo_out/ directory for all generated WebP files")
        
        # List output files
        output_files = glob.glob("demo_out/*.webp")
        if output_files:
            print(f"\n📋 Generated {len(output_files)} WebP files:")
            for f in sorted(output_files):
                size = os.path.getsize(f)
                print(f"   • {os.path.basename(f)} ({size:,} bytes)")
        
        print("\n💡 Usage in your projects(README.md for more advanced usage):")
        print("   from tgs_to_webp import convert_tgs_to_webp")
        print("   success = convert_tgs_to_webp('sticker.tgs', 'sticker.webp')")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()