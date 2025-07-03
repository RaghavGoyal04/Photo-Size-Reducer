#!/usr/bin/env python3
"""
Photo Size Reducer - A simple application to resize images to specified dimensions or file size
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import io
import math

class PhotoReducerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Size Reducer")
        self.root.geometry("800x700")  # Increase initial height
        self.root.configure(padx=10, pady=10)  # Reduce padding
        
        # Create a process frame at the bottom that will stay fixed
        self.process_frame = ttk.LabelFrame(self.root, text="Process Images")
        self.process_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        
        # Process button - make it more prominent with a larger font
        process_button = ttk.Button(self.process_frame, text="PROCESS IMAGES", command=self.process_images)
        process_button.pack(padx=5, pady=5, fill=tk.X)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.process_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=2)
        self.progress_label = ttk.Label(self.process_frame, text="")
        self.progress_label.pack(padx=5, pady=2)
        
        # Create a main frame with scrollbar
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # Add a scrollbar
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a canvas that will be scrollable
        self.canvas = tk.Canvas(self.main_frame, yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        self.scrollbar.config(command=self.canvas.yview)
        
        # Create a frame inside the canvas for all our widgets
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", tags="self.scroll_frame")
        
        # Set up variables
        self.input_files = []
        self.output_dir = ""
        self.width_var = tk.StringVar(value="800")
        self.height_var = tk.StringVar(value="600")
        self.maintain_aspect_ratio = tk.BooleanVar(value=True)
        self.quality_var = tk.IntVar(value=85)
        self.target_size_kb_var = tk.StringVar(value="600")
        self.size_mode = tk.BooleanVar(value=True)  # True = target size in KB, False = dimensions
        self.preview_image = None
        self.current_preview_index = 0
        self.current_img = None  # Store the current image object
        
        # Create the UI
        self.create_ui()
        
        # Set up scrolling when the frame size changes
        self.scroll_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind mousewheel for scrolling
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
    
    def on_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas"""
        width = event.width
        self.canvas.itemconfig(self.scroll_window, width=width)
    
    def on_mousewheel(self, event):
        """Scroll the canvas with the mousewheel"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_ui(self):
        # Instructions frame - more compact
        instructions_frame = ttk.Frame(self.scroll_frame)
        instructions_frame.pack(fill=tk.X, padx=5, pady=2)
        
        instructions_text = (
            "1. Select images → 2. Choose output directory → 3. Set size or dimensions → 4. PROCESS IMAGES"
        )
        
        instructions_label = ttk.Label(instructions_frame, text=instructions_text, justify=tk.LEFT)
        instructions_label.pack(padx=5, pady=2, anchor=tk.W)
        
        # Create frames
        input_frame = ttk.LabelFrame(self.scroll_frame, text="Input")
        input_frame.pack(fill=tk.X, padx=5, pady=2)
        
        output_frame = ttk.LabelFrame(self.scroll_frame, text="Output")
        output_frame.pack(fill=tk.X, padx=5, pady=2)
        
        mode_frame = ttk.LabelFrame(self.scroll_frame, text="Resize Mode")
        mode_frame.pack(fill=tk.X, padx=5, pady=2)
        
        settings_frame = ttk.LabelFrame(self.scroll_frame, text="Resize Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.preview_frame = ttk.LabelFrame(self.scroll_frame, text="Preview")
        self.preview_frame.pack(fill=tk.X, padx=5, pady=2)  # Changed to X from BOTH to control height
        
        # Input frame elements
        ttk.Button(input_frame, text="Select Images", command=self.select_images).pack(side=tk.LEFT, padx=5, pady=2)
        self.file_count_label = ttk.Label(input_frame, text="No files selected")
        self.file_count_label.pack(side=tk.LEFT, padx=5, pady=2)
        self.file_size_label = ttk.Label(input_frame, text="")
        self.file_size_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Output frame elements
        ttk.Button(output_frame, text="Select Output Directory", command=self.select_output_dir).pack(side=tk.LEFT, padx=5, pady=2)
        self.output_dir_label = ttk.Label(output_frame, text="No output directory selected")
        self.output_dir_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Mode frame elements
        mode_grid = ttk.Frame(mode_frame)
        mode_grid.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Radiobutton(mode_grid, text="Target file size (KB)", variable=self.size_mode, value=True, 
                        command=self.toggle_mode).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Radiobutton(mode_grid, text="Manual dimensions", variable=self.size_mode, value=False, 
                        command=self.toggle_mode).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Settings frame elements
        self.settings_grid = ttk.Frame(settings_frame)
        self.settings_grid.pack(fill=tk.X, padx=5, pady=2)
        
        # File size mode elements
        self.size_frame = ttk.Frame(self.settings_grid)
        ttk.Label(self.size_frame, text="Target Size:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(self.size_frame, textvariable=self.target_size_kb_var, width=10).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.size_frame, text="KB").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        ttk.Button(self.size_frame, text="Calculate Dimensions", command=self.calculate_dimensions).grid(
            row=0, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Dimension mode elements
        self.dim_frame = ttk.Frame(self.settings_grid)
        ttk.Label(self.dim_frame, text="Width:").grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(self.dim_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.dim_frame, text="pixels").grid(row=0, column=2, padx=5, pady=2, sticky=tk.W)
        
        ttk.Label(self.dim_frame, text="Height:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Entry(self.dim_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
        ttk.Label(self.dim_frame, text="pixels").grid(row=1, column=2, padx=5, pady=2, sticky=tk.W)
        
        # Quality setting
        ttk.Label(self.settings_grid, text="Quality:").grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        ttk.Scale(self.settings_grid, from_=1, to=100, variable=self.quality_var, orient=tk.HORIZONTAL, length=200,
                 command=self.on_quality_change).grid(row=2, column=1, columnspan=2, padx=5, pady=2, sticky=tk.W)
        self.quality_label = ttk.Label(self.settings_grid, text="85%")
        self.quality_label.grid(row=2, column=3, padx=5, pady=2, sticky=tk.W)
        
        # Aspect ratio
        ttk.Checkbutton(self.settings_grid, text="Maintain aspect ratio", variable=self.maintain_aspect_ratio,
                       command=self.update_preview).grid(row=3, column=0, columnspan=3, padx=5, pady=2, sticky=tk.W)
        
        # Show the appropriate mode
        self.toggle_mode()
        
        # Preview frame elements
        preview_controls = ttk.Frame(self.preview_frame)
        preview_controls.pack(fill=tk.X, side=tk.TOP, padx=5, pady=2)
        
        ttk.Button(preview_controls, text="Previous", command=self.show_previous_preview).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(preview_controls, text="Next", command=self.show_next_preview).pack(side=tk.LEFT, padx=5, pady=2)
        ttk.Button(preview_controls, text="Update Preview", command=self.update_preview).pack(side=tk.LEFT, padx=5, pady=2)
        
        # Fixed height preview canvas to prevent it from taking up too much space
        self.preview_canvas = tk.Canvas(self.preview_frame, bg="light gray", height=200)
        self.preview_canvas.pack(fill=tk.X, padx=5, pady=2)
    
    def toggle_mode(self, *args):
        """Toggle between file size mode and manual dimension mode"""
        if self.size_mode.get():
            # Size mode
            self.size_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)
            self.dim_frame.grid_remove()
        else:
            # Dimension mode
            self.dim_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)
            self.size_frame.grid_remove()
        
        # Update preview if we have an image loaded
        if self.current_img:
            self.update_preview()
    
    def on_quality_change(self, *args):
        """Update quality label when slider changes"""
        quality = self.quality_var.get()
        self.quality_label.config(text=f"{quality}%")
        
        # Update estimated file size if we have an image and in dimension mode
        if self.current_img and not self.size_mode.get():
            self.update_file_size_estimate()
    
    def select_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self.input_files = list(file_paths)
            self.file_count_label.config(text=f"{len(self.input_files)} files selected")
            self.current_preview_index = 0
            self.update_preview()
    
    def select_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir = dir_path
            self.output_dir_label.config(text=self.output_dir)
    
    def show_previous_preview(self):
        if not self.input_files:
            return
        self.current_preview_index = (self.current_preview_index - 1) % len(self.input_files)
        self.update_preview()
    
    def show_next_preview(self):
        if not self.input_files:
            return
        self.current_preview_index = (self.current_preview_index + 1) % len(self.input_files)
        self.update_preview()
    
    def estimate_file_size(self, width, height, quality):
        """Estimate file size based on dimensions and quality"""
        if not self.current_img:
            return 0
            
        # Create a resized image in memory
        img_ratio = self.current_img.width / self.current_img.height
        
        if self.maintain_aspect_ratio.get():
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
        
        # Don't allow dimensions greater than original
        new_width = min(new_width, self.current_img.width)
        new_height = min(new_height, self.current_img.height)
        
        # Resize and save to memory buffer to estimate size
        resized_img = self.current_img.resize((new_width, new_height), Image.LANCZOS)
        buffer = io.BytesIO()
        
        # Save with specified quality
        file_path = self.input_files[self.current_preview_index]
        _, ext = os.path.splitext(file_path)
        
        if ext.lower() in ['.jpg', '.jpeg']:
            resized_img.save(buffer, format="JPEG", quality=quality)
        elif ext.lower() == '.png':
            resized_img.save(buffer, format="PNG")
        elif ext.lower() == '.gif':
            resized_img.save(buffer, format="GIF")
        else:
            # Default to JPEG for other formats
            resized_img.save(buffer, format="JPEG", quality=quality)
        
        # Get size in KB
        size_kb = buffer.tell() / 1024
        return size_kb
    
    def update_file_size_estimate(self):
        """Update the file size estimate label based on current settings"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            quality = self.quality_var.get()
            
            size_kb = self.estimate_file_size(width, height, quality)
            self.file_size_label.config(text=f"Estimated size: {size_kb:.1f} KB")
        except (ValueError, AttributeError):
            self.file_size_label.config(text="")
    
    def calculate_dimensions(self):
        """Calculate dimensions based on target file size"""
        if not self.current_img or not self.input_files:
            messagebox.showwarning("No Image", "Please select an image first.")
            return
            
        try:
            target_kb = float(self.target_size_kb_var.get())
            if target_kb <= 0:
                messagebox.showerror("Invalid Size", "Target size must be greater than 0 KB.")
                return
                
            # Start with original dimensions
            original_width = self.current_img.width
            original_height = self.current_img.height
            
            # Initial quality
            quality = self.quality_var.get()
            
            # Calculate initial size estimate
            initial_size = self.estimate_file_size(original_width, original_height, quality)
            
            # If original is already smaller than target, keep original
            if initial_size <= target_kb:
                self.width_var.set(str(original_width))
                self.height_var.set(str(original_height))
                messagebox.showinfo("No Resizing Needed", 
                                   f"Original image is already {initial_size:.1f} KB, which is smaller than target.")
                return
            
            # Binary search to find appropriate scaling factor
            min_scale = 0.01  # 1% of original size
            max_scale = 1.0   # 100% of original size
            best_scale = 0.5
            best_diff = float('inf')
            
            for _ in range(10):  # 10 iterations should be enough for good approximation
                scale = (min_scale + max_scale) / 2
                test_width = int(original_width * scale)
                test_height = int(original_height * scale)
                
                # Ensure minimum dimensions of 10x10
                test_width = max(10, test_width)
                test_height = max(10, test_height)
                
                size_kb = self.estimate_file_size(test_width, test_height, quality)
                diff = abs(size_kb - target_kb)
                
                if diff < best_diff:
                    best_diff = diff
                    best_scale = scale
                
                if size_kb > target_kb:
                    max_scale = scale
                else:
                    min_scale = scale
            
            # Apply best scale
            new_width = max(10, int(original_width * best_scale))
            new_height = max(10, int(original_height * best_scale))
            
            # Set the new values
            self.width_var.set(str(new_width))
            self.height_var.set(str(new_height))
            
            # Show manual dimensions mode
            self.size_mode.set(False)
            self.toggle_mode()
            
            # Update preview
            self.update_preview()
            
            messagebox.showinfo("Dimensions Calculated", 
                               f"Calculated dimensions: {new_width}x{new_height} pixels\n"
                               f"Estimated file size: {self.estimate_file_size(new_width, new_height, quality):.1f} KB")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for target size.")
    
    def update_preview(self):
        if not self.input_files:
            return
        
        try:
            # Get current image
            img_path = self.input_files[self.current_preview_index]
            self.current_img = Image.open(img_path)
            
            # Resize for preview (just for display, not actual processing)
            preview_width = self.preview_canvas.winfo_width() - 10
            preview_height = self.preview_canvas.winfo_height() - 10
            
            if preview_width <= 1 or preview_height <= 1:
                # Canvas not yet properly sized, retry after a short delay
                self.root.after(100, self.update_preview)
                return
            
            # Calculate aspect ratios
            img_ratio = self.current_img.width / self.current_img.height
            preview_ratio = preview_width / preview_height
            
            if img_ratio > preview_ratio:
                # Image is wider than preview area
                display_width = preview_width
                display_height = int(preview_width / img_ratio)
            else:
                # Image is taller than preview area
                display_height = preview_height
                display_width = int(preview_height * img_ratio)
            
            img_preview = self.current_img.resize((display_width, display_height), Image.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(img_preview)
            
            # Display on canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                preview_width // 2 + 5, 
                preview_height // 2 + 5, 
                image=self.preview_image, 
                anchor="center"
            )
            
            # Add file info
            file_name = os.path.basename(img_path)
            original_size = f"{self.current_img.width}x{self.current_img.height}"
            
            # Get file size
            file_size_bytes = os.path.getsize(img_path)
            file_size_kb = file_size_bytes / 1024
            
            self.preview_canvas.create_text(
                10, 20, 
                text=f"File: {file_name} | Size: {file_size_kb:.1f} KB | Dimensions: {original_size}",
                anchor="nw",
                fill="black"
            )
            
            # If in dimension mode, update estimated file size
            if not self.size_mode.get():
                self.update_file_size_estimate()
            
        except Exception as e:
            messagebox.showerror("Preview Error", f"Error creating preview: {str(e)}")
    
    def process_images(self):
        if not self.input_files:
            messagebox.showwarning("No Input", "Please select images to resize.")
            return
        
        if not self.output_dir:
            messagebox.showwarning("No Output", "Please select an output directory.")
            return
        
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if width <= 0 or height <= 0:
                messagebox.showerror("Invalid Size", "Width and height must be positive numbers.")
                return
        except ValueError:
            messagebox.showerror("Invalid Size", "Width and height must be valid numbers.")
            return
        
        # Start processing in a separate thread to avoid freezing the UI
        threading.Thread(target=self._process_images_thread, args=(width, height), daemon=True).start()
    
    def _process_images_thread(self, width, height):
        total_files = len(self.input_files)
        processed = 0
        quality = self.quality_var.get()
        
        for img_path in self.input_files:
            try:
                # Update progress UI
                file_name = os.path.basename(img_path)
                self.root.after(0, lambda: self.progress_label.config(text=f"Processing: {file_name}"))
                
                # Open image
                img = Image.open(img_path)
                
                # Get original file size
                original_size_kb = os.path.getsize(img_path) / 1024
                
                # Determine new dimensions
                if self.maintain_aspect_ratio.get():
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
                
                # Prepare output filename
                file_name = os.path.basename(img_path)
                name, ext = os.path.splitext(file_name)
                output_file = os.path.join(self.output_dir, f"{name}_resized{ext}")
                
                # Save the resized image
                if ext.lower() in ['.jpg', '.jpeg']:
                    resized_img.save(output_file, quality=quality)
                else:
                    resized_img.save(output_file)
                
                # Get new file size
                new_size_kb = os.path.getsize(output_file) / 1024
                
                # Update progress
                processed += 1
                progress = (processed / total_files) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                
                # Log the size reduction
                size_reduction = original_size_kb - new_size_kb
                percent_reduction = (size_reduction / original_size_kb) * 100 if original_size_kb > 0 else 0
                
                log_message = (
                    f"Processed: {file_name}\n"
                    f"Dimensions: {img.width}x{img.height} → {new_width}x{new_height}\n"
                    f"Size: {original_size_kb:.1f} KB → {new_size_kb:.1f} KB ({percent_reduction:.1f}% reduction)"
                )
                
                print(log_message)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Processing Error", 
                                                               f"Error processing {os.path.basename(img_path)}: {str(e)}"))
        
        # Processing complete
        self.root.after(0, lambda: self.progress_label.config(text="Processing complete!"))
        self.root.after(0, lambda: messagebox.showinfo("Complete", 
                                                     f"Successfully processed {processed} of {total_files} images."))


def main():
    root = tk.Tk()
    app = PhotoReducerApp(root)
    
    # Process button and progress bar are already set up in the PhotoReducerApp class
    
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.mainloop()


if __name__ == "__main__":
    main()
