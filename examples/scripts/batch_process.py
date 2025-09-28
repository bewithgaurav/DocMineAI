#!/usr/bin/env python3
"""
Batch Processing Script for DocMineAI

This script helps process multiple document folders in batch,
useful for large-scale document analysis projects.

Usage:
    python batch_process.py --input-dirs dir1 dir2 dir3 --config my_config.yaml
    python batch_process.py --input-file folder_list.txt
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List

def main():
    parser = argparse.ArgumentParser(
        description="Batch process multiple document folders"
    )
    parser.add_argument(
        "--input-dirs", 
        nargs="+", 
        help="List of directories to process"
    )
    parser.add_argument(
        "--input-file", 
        help="Text file with list of directories (one per line)"
    )
    parser.add_argument(
        "--config", 
        default="config/extraction_config.yaml",
        help="Configuration file to use"
    )
    parser.add_argument(
        "--output-dir", 
        default="batch_outputs",
        help="Directory to store batch outputs"
    )
    parser.add_argument(
        "--model", 
        choices=["ollama", "openai"],
        default="ollama",
        help="Model to use for extraction"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Get list of directories to process
    directories = []
    
    if args.input_dirs:
        directories.extend(args.input_dirs)
    
    if args.input_file:
        if os.path.exists(args.input_file):
            with open(args.input_file, 'r') as f:
                directories.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"❌ Input file {args.input_file} not found")
            sys.exit(1)
    
    if not directories:
        print("❌ No directories specified. Use --input-dirs or --input-file")
        sys.exit(1)
    
    # Validate directories
    valid_dirs = []
    for dir_path in directories:
        if os.path.isdir(dir_path):
            valid_dirs.append(dir_path)
            print(f"✅ Found directory: {dir_path}")
        else:
            print(f"⚠️  Directory not found: {dir_path}")
    
    if not valid_dirs:
        print("❌ No valid directories found")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    print(f"📁 Output directory: {args.output_dir}")
    
    # Process each directory
    print(f"\n🚀 Processing {len(valid_dirs)} directories...")
    
    results = []
    total_start = time.time()
    
    for i, directory in enumerate(valid_dirs, 1):
        print(f"\n[{i}/{len(valid_dirs)}] Processing: {directory}")
        
        # Generate output filename
        dir_name = os.path.basename(directory.rstrip('/'))
        output_file = os.path.join(args.output_dir, f"{dir_name}_extraction.yaml")
        
        # Build command
        cmd = [
            "python", "extract.py",
            "--docs-dir", directory,
            "--config", args.config,
            "--model", args.model,
            "--output", output_file
        ]
        
        if args.verbose:
            cmd.append("--verbose")
        
        # Execute command
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=True
            )
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Completed in {duration:.1f}s: {output_file}")
            results.append({
                'directory': directory,
                'output_file': output_file,
                'duration': duration,
                'status': 'success'
            })
            
            if args.verbose:
                print(f"📊 Output: {result.stdout.strip()}")
                
        except subprocess.CalledProcessError as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"❌ Failed after {duration:.1f}s: {directory}")
            print(f"Error: {e.stderr.strip()}")
            results.append({
                'directory': directory,
                'duration': duration,
                'status': 'failed',
                'error': e.stderr.strip()
            })
    
    # Summary
    total_end = time.time()
    total_duration = total_end - total_start
    
    successful = len([r for r in results if r['status'] == 'success'])
    failed = len([r for r in results if r['status'] == 'failed'])
    
    print(f"\n{'='*60}")
    print(f"📊 BATCH PROCESSING SUMMARY")
    print(f"{'='*60}")
    print(f"Total directories: {len(valid_dirs)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time: {total_duration:.1f}s")
    print(f"Average time per directory: {total_duration/len(valid_dirs):.1f}s")
    
    if successful > 0:
        print(f"\n📁 Output files saved to: {args.output_dir}/")
        for result in results:
            if result['status'] == 'success':
                print(f"  ✅ {result['output_file']}")
    
    if failed > 0:
        print(f"\n❌ Failed directories:")
        for result in results:
            if result['status'] == 'failed':
                print(f"  ❌ {result['directory']}: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()