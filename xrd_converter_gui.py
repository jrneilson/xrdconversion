#!/usr/bin/env python3
"""
XRD Format Converter GUI
A cross-platform GUI application for converting BRML/RAW/XRDML files to XYE format.
Supports drag-and-drop and file selection dialogs.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
# import tkinter.dnd as dnd  # Not used - replaced with tkinterdnd2
import os
import sys
import threading
from pathlib import Path
import platform

# Import the converter functionality
from xrd_converter import XRDConverter


class XRDConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XRD Format Converter")
        self.root.geometry("800x600")
        
        # Set minimum window size
        self.root.minsize(600, 400)
        
        # Configure for different platforms
        if platform.system() == "Darwin":  # macOS
            self.root.configure(bg='#f0f0f0')
        
        self.setup_ui()
        self.setup_drag_drop()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="XRD Format Converter", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, 
                                  text="Convert BRML and RAW files to XYE format",
                                  font=('Arial', 11))
        subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky=tk.W)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(1, weight=1)
        
        # Buttons frame
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(1, weight=1)
        
        # Select files button
        self.select_button = ttk.Button(button_frame, text="Select Files", 
                                       command=self.select_files)
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        # Clear button
        self.clear_button = ttk.Button(button_frame, text="Clear List", 
                                      command=self.clear_files)
        self.clear_button.grid(row=0, column=1, padx=(0, 10), sticky=tk.E)
        
        # Convert button
        self.convert_button = ttk.Button(button_frame, text="Convert Files", 
                                        command=self.convert_files,
                                        style='Accent.TButton')
        self.convert_button.grid(row=0, column=2)
        
        # Drag and drop area
        self.drop_frame = tk.Frame(file_frame, bg='#e8f4f8', relief='ridge', bd=2)
        self.drop_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.drop_frame.columnconfigure(0, weight=1)
        self.drop_frame.rowconfigure(0, weight=1)
        
        # Drop zone label
        self.drop_label = tk.Label(self.drop_frame, 
                                  text="Drag and drop BRML/RAW files here\\n\\nSupported formats:\\n• .brml files\\n• .raw files",
                                  bg='#e8f4f8', fg='#666666',
                                  font=('Arial', 12),
                                  justify=tk.CENTER)
        self.drop_label.grid(row=0, column=0, padx=20, pady=20)
        
        # File list
        list_frame = ttk.LabelFrame(file_frame, text="Selected Files", padding="5")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(list_container, height=6)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, 
                                 command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Conversion Progress", padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to convert files")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Output log frame
        log_frame = ttk.LabelFrame(main_frame, text="Conversion Log", padding="5")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initialize file list
        self.file_paths = []
        
    def setup_drag_drop(self):
        """Set up drag and drop functionality."""
        try:
            # Try to use tkinterdnd2 for proper drag-drop support
            import tkinterdnd2 as tkdnd
            
            # This will only work if root was created as tkdnd.Tk()
            if hasattr(self.root, 'drop_target_register'):
                self.root.drop_target_register(tkdnd.DND_FILES)
                self.root.dnd_bind('<<Drop>>', self.handle_drop_tkdnd)
                print("Advanced drag-drop enabled")
            else:
                print("Basic drag-drop fallback")
                self.setup_basic_drop()
                
        except ImportError:
            print("tkinterdnd2 not available, using basic file handling")
            self.setup_basic_drop()
    
    def setup_basic_drop(self):
        """Set up basic file handling without advanced drag-drop."""
        # Bind click events for visual feedback
        self.drop_frame.bind('<Button-1>', self.on_drop_enter)
        self.drop_frame.bind('<ButtonRelease-1>', self.on_drop_leave)
        
        # Add instruction text about using file dialog
        self.drop_label.configure(
            text="Click 'Select Files' to choose BRML/RAW files\n\nSupported formats:\n• .brml files\n• .raw files"
        )
        
    def on_drop_enter(self, event):
        """Visual feedback when drag enters."""
        self.drop_frame.configure(bg='#d4e8fc')
        self.drop_label.configure(bg='#d4e8fc')
        
    def on_drop_leave(self, event):
        """Reset visual feedback when drag leaves."""
        self.drop_frame.configure(bg='#e8f4f8')
        self.drop_label.configure(bg='#e8f4f8')
        
    def handle_drop_tkdnd(self, event):
        """Handle dropped files from tkinterdnd2."""
        files = event.data.split()
        valid_files = []
        
        for file_path in files:
            # Remove file:// prefix if present and handle URL encoding
            if file_path.startswith('file://'):
                file_path = file_path[7:]
            
            # Handle URL encoding
            import urllib.parse
            file_path = urllib.parse.unquote(file_path)
            
            if os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.brml', '.raw', '.xrdml']:
                    valid_files.append(file_path)
                else:
                    self.log(f"Skipped {os.path.basename(file_path)}: Unsupported format")
            else:
                self.log(f"Skipped {file_path}: Not a file")
        
        if valid_files:
            self.add_files(valid_files)
        else:
            messagebox.showwarning("No Valid Files", 
                                 "No valid BRML, RAW, or XRDML files were dropped.")
    
    def select_files(self):
        """Open file selection dialog."""
        filetypes = [
            ("XRD files", "*.brml *.raw *.xrdml *.XRDML"),
            ("BRML files", "*.brml"),
            ("RAW files", "*.raw"),
            ("XRDML files", "*.xrdml *.XRDML"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select XRD Files",
            filetypes=filetypes
        )
        
        if files:
            self.add_files(files)
    
    def add_files(self, file_paths):
        """Add files to the conversion list."""
        added_count = 0
        for file_path in file_paths:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))
                added_count += 1
        
        if added_count > 0:
            self.log(f"Added {added_count} file(s) to conversion list")
            self.update_status(f"{len(self.file_paths)} file(s) ready for conversion")
    
    def clear_files(self):
        """Clear the file list."""
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("Cleared file list")
        self.update_status("Ready to convert files")
        self.progress.configure(value=0)
    
    def convert_files(self):
        """Convert all files in the list."""
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select files to convert first.")
            return
        
        # Disable UI during conversion
        self.set_ui_state(False)
        
        # Start conversion in a separate thread
        thread = threading.Thread(target=self.perform_conversion)
        thread.daemon = True
        thread.start()
    
    def perform_conversion(self):
        """Perform the actual conversion (runs in separate thread)."""
        total_files = len(self.file_paths)
        successful = 0
        failed = 0
        
        self.root.after(0, lambda: self.progress.configure(maximum=total_files, value=0))
        self.root.after(0, lambda: self.log("Starting conversion..."))
        
        for i, file_path in enumerate(self.file_paths):
            # Update progress
            self.root.after(0, lambda i=i: self.progress.configure(value=i))
            self.root.after(0, lambda f=os.path.basename(file_path): 
                          self.update_status(f"Converting {f}..."))
            
            try:
                # Create converter instance
                converter = XRDConverter()
                
                # Convert file
                success = converter.convert_file(file_path)
                
                if success:
                    successful += 1
                    self.root.after(0, lambda f=os.path.basename(file_path): 
                                  self.log(f"✓ Successfully converted {f}"))
                else:
                    failed += 1
                    self.root.after(0, lambda f=os.path.basename(file_path): 
                                  self.log(f"✗ Failed to convert {f}"))
                    
            except Exception as e:
                failed += 1
                self.root.after(0, lambda f=os.path.basename(file_path), e=str(e): 
                              self.log(f"✗ Error converting {f}: {e}"))
        
        # Update final progress
        self.root.after(0, lambda: self.progress.configure(value=total_files))
        
        # Show completion message
        summary = f"Conversion complete! {successful} successful, {failed} failed"
        self.root.after(0, lambda: self.log(summary))
        self.root.after(0, lambda: self.update_status(summary))
        
        # Re-enable UI
        self.root.after(0, lambda: self.set_ui_state(True))
        
        # Show completion dialog
        if failed == 0:
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"All {successful} files converted successfully!"))
        else:
            self.root.after(0, lambda: messagebox.showwarning("Partial Success", 
                f"{successful} files converted successfully, {failed} failed. Check the log for details."))
    
    def set_ui_state(self, enabled):
        """Enable or disable UI elements."""
        state = 'normal' if enabled else 'disabled'
        self.select_button.configure(state=state)
        self.clear_button.configure(state=state)
        self.convert_button.configure(state=state)
    
    def update_status(self, message):
        """Update the status label."""
        self.status_label.configure(text=message)
    
    def log(self, message):
        """Add a message to the log."""
        self.log_text.insert(tk.END, f"{message}\\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()



def main():
    """Main function to run the GUI application."""
    # Try to create drag-drop enabled window first
    try:
        import tkinterdnd2 as tkdnd
        root = tkdnd.Tk()
        print("Using tkinterdnd2 for enhanced drag-drop support")
    except ImportError:
        root = tk.Tk()
        print("Using standard tkinter (no advanced drag-drop)")
    
    # Create the application
    app = XRDConverterGUI(root)
    
    # Handle command line arguments (for file associations)
    if len(sys.argv) > 1:
        files = [arg for arg in sys.argv[1:] if os.path.isfile(arg)]
        if files:
            root.after(100, lambda: app.add_files(files))
    
    # Set up the application icon (if available)
    try:
        # Try to set window icon
        if platform.system() == "Darwin":  # macOS
            root.iconbitmap()  # Use default icon
        else:  # Windows/Linux
            root.iconbitmap()  # Use default icon
    except:
        pass  # Ignore icon errors
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()