# Photo-Size-Reducer
reduce the photos size without tinkering with dimensions. Just enter the target file size or dimensions you want and voila!

## Features

- Select multiple images for batch processing
- Resize images based on target file size (KB) or manual dimensions
- Automatically calculate dimensions to reach target file size
- Option to maintain aspect ratio during resizing
- Adjustable image quality for JPEG files
- Preview images before processing with file size estimates
- Simple and intuitive user interface

## Requirements

- Python 3.6 or higher
- Pillow (Python Imaging Library)

## Installation

1. Clone or download this repository
2. Create and activate a virtual environment (recommended):

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Command-Line Version (No Tkinter Required)

If you don't want to install Tkinter or prefer a command-line interface, you can use the CLI version:

```bash
# Basic usage
python cli_photo_reducer.py input_image.jpg output_directory

# Process all images in a directory
python cli_photo_reducer.py "input_directory/*.jpg" output_directory

# Specify custom dimensions
python cli_photo_reducer.py input_image.jpg output_directory --width 1024 --height 768

# Specify target file size
python cli_photo_reducer.py input_image.jpg output_directory --target-size 100

# Additional options
python cli_photo_reducer.py input_image.jpg output_directory --no-aspect-ratio --quality 90 --suffix _small
```

Command-line options:
- `--width` - Target width in pixels (default: 800)
- `--height` - Target height in pixels (default: 600)
- `--target-size` - Target file size in KB
- `--no-aspect-ratio` - Don't maintain aspect ratio
- `--quality` - JPEG quality (1-100, default: 85)
- `--suffix` - Suffix to add to output filenames (default: _resized)

### GUI Version (Requires Tkinter)

1. Run the application:

```bash
python photo_reducer.py
```

2. Select the images you want to resize
3. Choose an output directory for the resized images
4. Choose your resize mode:
   - **Target file size (KB)**: Enter the maximum size in KB and click "Calculate Dimensions"
   - **Manual dimensions**: Directly enter width and height in pixels
5. Adjust quality setting as needed
6. Click "Process Images" to start the batch processing

## How It Works

This application uses the Python Imaging Library (Pillow) to load, resize, and save images. 
The tkinter library provides the graphical user interface.

When using the "Target file size" mode, the application performs a binary search to find the 
optimal dimensions that will result in a file size closest to your target size while preserving 
aspect ratio. This is useful for preparing images for web uploads with size limits.

When "Maintain aspect ratio" is checked, the application will resize images to fit within the 
specified dimensions while preserving their original proportions. If unchecked, images will be 
stretched or compressed to exactly match the specified dimensions.

## License

This project is open source and available under the MIT License.

