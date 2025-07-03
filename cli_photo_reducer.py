#!/usr/bin/env python3
"""
Command Line Photo Size Reducer - A simple application to resize images to specified dimensions
"""

import os
import sys
import argparse
from PIL import Image
import glob

def resize_image(input_path, output_path, width, height, maintain_aspect_ratio=True, quality=85):
    """
    Resize a single image and save it to the output path.
    
    Args:
        input_path: Path to the input image file
        output_path: Path to save the resized image
        width: Target width in pixels
        height: Target height in pixels
        maintain_aspect_ratio: If True, maintain the original aspect ratio
        quality: JPEG quality (1-100) for JPEG images
    
    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Open the image
        img = Image.open(input_path)
        
        # Determine new dimensions
        if maintain_aspect_ratio:
            img_ratio = img.width / img.height
            
            if img_ratio > 1:
                # Landscape orientation
                new_width = width
                new_height = int(width / img_ratio)
            else:
                # Portrait or square orientation
                new_height = height
                new_width = int(height * img_ratio)
        else:
            new_width = width
            new_height = height
        
        # Resize the image
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save the resized image
        _, ext = os.path.splitext(input_path)
        if ext.lower() in ['.jpg', '.jpeg']:
            resized_img.save(output_path, quality=quality)
        else:
            resized_img.save(output_path)
        
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Resize images to specified dimensions")
    parser.add_argument("input", help="Input image file or directory path (use wildcards for multiple files)")
    parser.add_argument("output", help="Output directory path")
    parser.add_argument("--width", type=int, default=800, help="Target width in pixels (default: 800)")
    parser.add_argument("--height", type=int, default=600, help="Target height in pixels (default: 600)")
    parser.add_argument("--no-aspect-ratio", action="store_true", help="Don't maintain aspect ratio")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100, default: 85)")
    parser.add_argument("--suffix", default="_resized", help="Suffix to add to output filenames (default: _resized)")
    
    args = parser.parse_args()
    
    # Validate input path
    input_paths = []
    if os.path.isdir(args.input):
        # If input is a directory, process all images in it
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff']:
            input_paths.extend(glob.glob(os.path.join(args.input, ext)))
            input_paths.extend(glob.glob(os.path.join(args.input, ext.upper())))
    elif '*' in args.input or '?' in args.input:
        # Input is a wildcard pattern
        input_paths = glob.glob(args.input)
    else:
        # Input is a single file
        input_paths = [args.input]
    
    # Check if we found any files
    if not input_paths:
        print("Error: No input images found.")
        return 1
    
    # Make sure output directory exists
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Process images
    success_count = 0
    error_count = 0
    maintain_aspect_ratio = not args.no_aspect_ratio
    
    print(f"Found {len(input_paths)} image(s) to process")
    print(f"Target size: {args.width}x{args.height} pixels")
    print(f"Maintaining aspect ratio: {'Yes' if maintain_aspect_ratio else 'No'}")
    print(f"JPEG quality: {args.quality}")
    print("---")
    
    for i, input_path in enumerate(input_paths, 1):
        # Create output path
        basename = os.path.basename(input_path)
        name, ext = os.path.splitext(basename)
        output_path = os.path.join(args.output, f"{name}{args.suffix}{ext}")
        
        # Process the image
        print(f"[{i}/{len(input_paths)}] Processing: {basename}... ", end="", flush=True)
        success, error = resize_image(
            input_path, 
            output_path, 
            args.width, 
            args.height, 
            maintain_aspect_ratio, 
            args.quality
        )
        
        if success:
            print("Done")
            success_count += 1
        else:
            print(f"Error: {error}")
            error_count += 1
    
    # Print summary
    print("---")
    print(f"Processing complete: {success_count} succeeded, {error_count} failed")
    if success_count > 0:
        print(f"Resized images saved to: {args.output}")
    
    return 0 if error_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
