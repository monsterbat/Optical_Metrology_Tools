import tkinter as tk
from tkinter import Label, Button, Text, StringVar, messagebox, ttk
from src.utils.paths import resource_path
from src.utils.version import get_app_title, get_version_info
from src.io.file_operations import open_duplicate_process, open_user_guide, open_box_plot_tool, open_correlation_tool, open_box_plot_lite, open_quick_report, open_exclude_outliers, open_data_file_and_update_ui, process_duplicate_with_file, process_spec_setup_with_file, process_outliers_with_file, open_normal_distribution, open_file_jsl, open_file_jsl_beta, open_best_fit_beta, open_google_drive_file
from src.ui.spec_setup_dialog import open_spec_setup
from src.ui.python_pc_ui import create_python_pc_ui

def create_main_window():
    """Create the main window with scrollable content"""
    root = tk.Tk()
    root.title(get_app_title())
    
    # Set window size and center it on screen
    window_width = 750
    window_height = 550
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate position to center the window
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    
    # Set geometry with centered position
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.minsize(600, 400)  # Minimum window size
    
    # Create main container frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)
    
    # Create canvas and scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)
    
    # Configure scrollable frame
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    # Create window in canvas with centering
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Function to center the content horizontally
    def center_content(event=None):
        canvas_width = canvas.winfo_width()
        frame_width = scrollable_frame.winfo_reqwidth()
        
        # Center the frame horizontally
        x_position = max(0, (canvas_width - frame_width) // 2)
        canvas.coords(canvas_window, x_position, 0)
    
    # Bind canvas resize event to recenter content
    canvas.bind("<Configure>", center_content)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Bind mousewheel to canvas
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Bind mousewheel events
    canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
    canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
    canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
    
    # Store references for later use
    root.scrollable_frame = scrollable_frame
    root.canvas = canvas
    
    # Initial centering after window is created
    root.after(100, center_content)
    
    return root

def create_header_ui(root):
    """Create header section with description and instruction link"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.Frame(parent)
    frame.pack(fill="x", padx=10, pady=10)

    # Description text
    desc_text = tk.Label(frame, text="This is the toolbox for processing, analyzing, and visualizing optical data.", 
                         font=("Arial", 11), anchor="center", justify="center")
    desc_text.pack(fill="x", pady=(0, 5))

    # Instruction link
    link_text = tk.Label(frame, text="➡️ Click here to view the instructions.", 
                         font=("Arial", 14, "bold"), cursor="hand2")
    link_text.pack(anchor="center")
    
    # Bind click event to open user guide
    link_text.bind("<Button-1>", lambda e: open_user_guide())
    
    return frame


def create_quick_analysis_ui(root):
    """Create Quick analysis section with Quick report button"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Quick analysis", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # Button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    # Create Quick report button
    quick_report_btn = Button(
        btn_frame, 
        text="Quick report", 
        width=16, 
        font=("Arial", 12), 
        command=open_quick_report
    )
    quick_report_btn.pack(pady=5)


def create_open_data_ui(root):
    """Create independent Open Data section without border"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.Frame(parent)
    frame.pack(fill="x", padx=10, pady=10)

    # Center button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    # Open Data(jsl) button (隱藏但保留，未來可能使用)
    open_data_jsl_btn = Button(btn_frame, text="Open Data(jsl)", width=16, font=("Arial", 12, "bold"))
    # open_data_jsl_btn.pack(side="left", padx=8, pady=5)  # 註解掉不顯示

    # Open Data button (原本的 Beta 版本，現在是主要版本)
    open_data_btn = Button(btn_frame, text="Open Data", width=16, font=("Arial", 12, "bold"))
    open_data_btn.pack(side="left", padx=8, pady=5)

    # Google Drive button (新增)
    google_drive_btn = Button(btn_frame, text="Google Drive", width=16, font=("Arial", 12, "bold"))
    google_drive_btn.pack(side="left", padx=8, pady=5)

    # Set button commands
    open_data_jsl_btn.config(command=open_file_jsl)
    open_data_btn.config(command=open_file_jsl_beta)
    google_drive_btn.config(command=open_google_drive_file)

    return frame

def create_data_process_ui(root):
    """Create the Data Process block with three function buttons"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Data Process", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # Button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    # Process buttons (now always enabled)
    exclude_duplicate_btn = Button(btn_frame, text="Exclude Duplicate", width=16, font=("Arial", 12))
    exclude_duplicate_btn.pack(side="left", padx=8)

    setup_spec_btn = Button(btn_frame, text="Setup Spec", width=16, font=("Arial", 12))
    setup_spec_btn.pack(side="left", padx=8)

    exclude_outlier_btn = Button(btn_frame, text="Exclude Outlier", width=16, font=("Arial", 12))
    exclude_outlier_btn.pack(side="left", padx=8)

    # Set button commands
    exclude_duplicate_btn.config(command=open_duplicate_process)
    setup_spec_btn.config(command=open_spec_setup)
    exclude_outlier_btn.config(command=open_exclude_outliers)

    return frame

def create_process_capability_ui(root, on_open_analysis):
    """Create Process Capability section with Best Fit and Normal distribution buttons"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Process Capability", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # Button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    # Normal distribution button
    normal_dist_btn = Button(
        btn_frame, 
        text="Normal distribution", 
        width=16, 
        font=("Arial", 12), 
        command=open_normal_distribution
    )
    normal_dist_btn.pack(side="left", padx=8)

    # Best Fit button (renamed from Select Analysis Items)
    best_fit_btn = Button(
        btn_frame, 
        text="Best Fit", 
        width=16, 
        font=("Arial", 12), 
        command=on_open_analysis
    )
    best_fit_btn.pack(side="left", padx=8)

    # Best Fit(beta) button - 新增的按鈕
    best_fit_beta_btn = Button(
        btn_frame, 
        text="Best Fit(beta)", 
        width=16, 
        font=("Arial", 12), 
        command=open_best_fit_beta
    )
    best_fit_beta_btn.pack(side="left", padx=8)
    
    return frame

def create_process_capability_python_only_ui(root):
    """Create Process Capability Python Only section with button"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Process Capability Python Only", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # Button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    def open_python_pc_window():
        """開啟Process Capability Python Only視窗"""
        # 創建新的頂層視窗
        pc_window = tk.Toplevel(root)
        pc_window.title("Process Capability Python Only")
        pc_window.geometry("900x700")
        pc_window.resizable(True, True)
        
        # 置中顯示
        pc_window.transient(root)
        
        # 在新視窗中創建UI
        python_pc_ui = create_python_pc_ui(pc_window)
        
        return python_pc_ui

    # Process Capability Python Only button
    python_pc_btn = tk.Button(
        btn_frame, 
        text="Process Capability Python Only", 
        width=30, 
        font=("Arial", 12, "bold"), 
        command=open_python_pc_window
    )
    python_pc_btn.pack(pady=5)
    
    return frame

def create_report_generate_ui(root, jmp_file_path, on_extract):
    """Create Report Generate section with JSL input and extract button"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Report Generate", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # JSL input box
    Label(frame, text="Please paste JSL code:", font=("Arial", 11)).pack(anchor="center", pady=(5, 2))
    text_input = Text(frame, height=6, width=80, font=("Consolas", 12))
    text_input.pack(pady=(0, 10))

    # Extract button
    btn_extract = Button(frame, text="Generate in report format", font=("Arial", 12), command=on_extract, width=30)
    btn_extract.pack(pady=(0, 5))

    return text_input

def create_analysis_tools_ui(root):
    """Create analysis tools section with BoxPlot and Correlation buttons"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    frame = tk.LabelFrame(parent, bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", padx=10, pady=10)

    # Center title
    title = tk.Label(frame, text="Analysis Tools", font=("Arial", 18, "bold"), anchor="center", justify="center")
    title.pack(fill="x", pady=(0, 10))

    # Button frame
    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    # Create Box Plot button
    """
    box_plot_btn = Button(
        btn_frame, 
        text="Box Plot", 
        width=16, 
        font=("Arial", 12), 
        command=open_box_plot_tool
    )
    box_plot_btn.pack(side="left", padx=8)
    

    # Create Box Plot Lite button
    box_plot_lite_btn = Button(
        btn_frame, 
        text="Box Plot Lite", 
        width=16, 
        font=("Arial", 12), 
        command=open_box_plot_lite
    )
    box_plot_lite_btn.pack(side="left", padx=8)
    """
    # Create Correlation button
    correlation_btn = Button(
        btn_frame, 
        text="Correlation", 
        width=16, 
        font=("Arial", 12), 
        command=open_correlation_tool
    )
    correlation_btn.pack(side="left", padx=8)

def create_app_info_ui(root):
    """Create application info section with version, author info and instruction button"""
    # Use scrollable_frame if available, otherwise use root
    parent = getattr(root, 'scrollable_frame', root)
    # Create info frame
    frame = tk.Frame(parent)
    frame.pack(fill="x", padx=10, pady=5)
    
    # Center button frame
    center_frame = tk.Frame(frame)
    center_frame.pack(anchor="center", pady=5)
    
    # Instruction button (placed in center)
    # help_btn = Button(center_frame, text="How to use", command=open_user_guide, font=("Arial", 12), width=20)
    # help_btn.pack(pady=5)
    
    # Version and author info (placed at bottom center)
    # version_label = Label(frame, text=get_version_info(), font=("Arial", 10), anchor="center")
    # version_label.pack(fill="x", pady=5)
    
    return frame 