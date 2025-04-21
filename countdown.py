import tkinter as tk
from tkinter import ttk
from screeninfo import get_monitors
from PIL import Image, ImageTk
import os

# Global variables
is_fullscreen = False
is_timer_running = False
is_timer_paused = False
timeup_label = None
remaining_seconds = 0
last_start_seconds = 0
timer_window_active = False

# Create root early
root = tk.Tk()
root.withdraw()

# Global digit list
digits = [tk.StringVar(value="0") for _ in range(4)]

# -- Countdown logic --
def countdown(seconds_remaining):
    global remaining_seconds, timeup_label

    if is_timer_paused:
        return

    remaining_seconds = seconds_remaining

    if seconds_remaining <= 0:
        frame.pack_forget()
        root.configure(bg="red")
        timeup_label = tk.Label(
            root,
            text="TIME'S UP",
            font=("Helvetica", 150, "bold"),
            fg="white",
            bg="red"
        )
        timeup_label.pack(expand=True)
        return

    # Update digits
    m1 = (seconds_remaining // 600) % 10
    m2 = (seconds_remaining // 60) % 10
    s1 = (seconds_remaining % 60) // 10
    s2 = (seconds_remaining % 10)

    digits[0].set(str(m1))
    digits[1].set(str(m2))
    digits[2].set(str(s1))
    digits[3].set(str(s2))

    remaining_seconds -= 1
    root.after(1000, lambda: countdown(remaining_seconds))


def start_countdown(event=None):
    global is_timer_running, is_timer_paused, remaining_seconds, timeup_label, last_start_seconds

    if timeup_label:
        timeup_label.destroy()
        timeup_label = None
        root.configure(bg="black")
        frame.pack(expand=True)
        for i in range(4):
            digits[i].set("0")
        is_timer_running = False
        is_timer_paused = False
        remaining_seconds = 0
        return

    if is_timer_running and not is_timer_paused:
        is_timer_paused = True
        return

    if is_timer_running and is_timer_paused:
        is_timer_paused = False
        countdown(remaining_seconds)
        return

    total_seconds = (
        int(digits[0].get()) * 600 +
        int(digits[1].get()) * 60 +
        int(digits[2].get()) * 10 +
        int(digits[3].get())
    )

    if total_seconds > 0:
        last_start_seconds = total_seconds
        is_timer_running = True
        is_timer_paused = False
        remaining_seconds = total_seconds
        countdown(remaining_seconds)


def set_timer_from_seconds(seconds):
    global remaining_seconds, is_timer_running, is_timer_paused
    global timeup_label
    if timeup_label:
        timeup_label.destroy()
        timeup_label = None

    remaining_seconds = seconds
    is_timer_running = False
    is_timer_paused = False

    m1 = (seconds // 600) % 10
    m2 = (seconds // 60) % 10
    s1 = (seconds % 60) // 10
    s2 = (seconds % 10)

    digits[0].set(str(m1))
    digits[1].set(str(m2))
    digits[2].set(str(s1))
    digits[3].set(str(s2))

    if 'frame' in globals():
        root.configure(bg="black")
        frame.pack(expand=True)

# -- Digit control logic --
def increment(index):
    global remaining_seconds

    current = int(digits[index].get())
    if index == 0 or index == 1 or index == 3:
        new_val = (current + 1) % 10
    elif index == 2:
        new_val = (current + 1) % 6

    digits[index].set(str(new_val))

    if is_timer_running or is_timer_paused:
        update_remaining_seconds()

def decrement(index):
    global remaining_seconds

    current = int(digits[index].get())
    if index == 0 or index == 1 or index == 3:
        new_val = (current - 1) % 10
    elif index == 2:
        new_val = (current - 1) % 6

    digits[index].set(str(new_val))

    if is_timer_running or is_timer_paused:
        update_remaining_seconds()

def update_remaining_seconds():
    global remaining_seconds
    remaining_seconds = (
        int(digits[0].get()) * 600 +
        int(digits[1].get()) * 60 +
        int(digits[2].get()) * 10 +
        int(digits[3].get())
    )

# -- Fullscreen & key handling --
def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.overrideredirect(is_fullscreen)
    root.attributes("-fullscreen", is_fullscreen)

def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    root.overrideredirect(False)
    root.attributes("-fullscreen", False)
    root.geometry("800x400")

def launch_controller_window(monitor):
    global last_start_seconds

    controller = tk.Toplevel()
    controller.title("Timer Controller")
    controller.geometry(f"400x800+{monitor.x}+{monitor.y}")
    controller.configure(bg="gray15")

    header = tk.Frame(controller, bg="black", height=120)
    header.pack(fill="x", side="top")

    header_inner = tk.Frame(header, bg="black")
    header_inner.pack(expand=True)

    # Load and display logo on the header bar
    try:
        logo_img = Image.open("qavlogo.jpg")
        logo_img = logo_img.resize((300, 150), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo_img)

        logo_label = tk.Label(header_inner, image=logo_tk, bg="black")
        logo_label.image = logo_tk
        logo_label.pack(pady=5)
    except Exception as e:
        print("Error loading logo:", e)


    # Close both windows when controller is closed
    def on_controller_close():
        root.destroy()
        controller.destroy()
    controller.protocol("WM_DELETE_WINDOW", on_controller_close)

    monitors = get_monitors()
    tk.Label(controller, text="Select Display for Timer", font=("Arial", 12), fg="white", bg="gray15").pack(pady=5)

    monitor_var = tk.StringVar(value=f"{monitor.width}x{monitor.height} @ ({monitor.x},{monitor.y})")

    options = [
        f"{i}: {m.width}x{m.height} @ ({m.x}, {m.y})"
        for i, m in enumerate(monitors)
    ]

    dropdown = ttk.Combobox(controller, values=options, textvariable=monitor_var, state="readonly", font=("Arial", 10))
    dropdown.pack(pady=5)

    preset_buttons = []

    def launch_on_selected_display():
        index = dropdown.current()
        selected = monitors[index]
        start_timer_on_display(selected)
        for btn in preset_buttons:
            btn.config(state="normal")

    tk.Button(controller, text="Launch Timer on Selected Display", command=launch_on_selected_display).pack(pady=10)

    # Time Display
    tk.Label(controller, text="Current Time", font=("Arial", 14), fg="white", bg="gray15").pack(pady=10)
    time_display = tk.Label(controller, text="", font=("Courier New", 48), fg="lime", bg="black", width=8)
    time_display.pack(pady=5)

    def update_display():
        time_display.config(text=f"{digits[0].get()}{digits[1].get()}:{digits[2].get()}{digits[3].get()}")
        controller.after(200, update_display)

    update_display()

    def restart_last():
        if last_start_seconds > 0:
            set_timer_from_seconds(last_start_seconds)
            start_countdown()

    def adjust_minutes(delta):
        total = (
            int(digits[0].get()) * 600 +
            int(digits[1].get()) * 60 +
            int(digits[2].get()) * 10 +
            int(digits[3].get())
        )
        total = max(0, total + (delta * 60))
        set_timer_from_seconds(total)

    def reset_timer():
        for d in digits:
            d.set("0")
        global is_timer_running, is_timer_paused, timeup_label, remaining_seconds
        is_timer_running = False
        is_timer_paused = False
        if timeup_label:
            timeup_label.destroy()
            timeup_label = None
        remaining_seconds = 0
        if 'frame' in globals():
            frame.pack(expand=True)
            root.configure(bg="black")

    control_frame = tk.Frame(controller, bg="gray15")
    control_frame.pack(pady=10)

    tk.Button(control_frame, text="Start / Pause", command=start_countdown, width=15).grid(row=0, column=0, padx=10, pady=5)
    tk.Button(control_frame, text="Reset", command=reset_timer, width=15).grid(row=0, column=1, padx=10, pady=5)

    # Quick Presets
    preset_frame = tk.LabelFrame(controller, text="Quick Set", bg="gray15", fg="white", font=("Arial", 10))
    preset_frame.pack(pady=10)

    presets = [
        ("1 min", 60), ("5 min", 300), ("10 min", 600),
        ("15 min", 900), ("30 min", 1800), ("45 min", 2700), ("1 hour", 3600)
    ]

    for i, (label, secs) in enumerate(presets):
        row, col = divmod(i, 3)
        btn = tk.Button(preset_frame, text=label, width=10, command=lambda s=secs: set_timer_from_seconds(s), state="disabled")
        btn.grid(row=row, column=col, padx=5, pady=5)
        preset_buttons.append(btn)

    # Minute Adjust
    adjust_frame = tk.LabelFrame(controller, text="Adjust Time", bg="gray15", fg="white", font=("Arial", 10))
    adjust_frame.pack(pady=10)

    for label, delta, col in [("+1 min", 1, 0), ("-1 min", -1, 1)]:
        btn = tk.Button(adjust_frame, text=label, width=15, command=lambda d=delta: adjust_minutes(d), state="disabled")
        btn.grid(row=0, column=col, padx=5, pady=5)
        preset_buttons.append(btn)

    # Utilities
    utils_frame = tk.LabelFrame(controller, text="Utilities", bg="gray15", fg="white", font=("Arial", 10))
    utils_frame.pack(pady=10)

    restart_btn = tk.Button(utils_frame, text="Restart Last", width=32, command=restart_last, state="disabled")
    restart_btn.pack(pady=5)
    preset_buttons.append(restart_btn)

    controller.attributes('-topmost', True)

# -- Launch Timer --
def start_timer_on_display(monitor):
    global root, frame, timer_window_active, digits

    if timer_window_active:
        root.destroy()  # Clean up the previous timer window

    root = tk.Toplevel()
    timer_window_active = True

    digits = [tk.StringVar(value="0") for _ in range(4)]

    root.title("Countdown Timer")
    root.configure(bg="black")
    root.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
    root.overrideredirect(True)

    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)
    root.bind("<space>", start_countdown)

    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    digit_labels = []
    for i in range(2):
        label = tk.Label(frame, textvariable=digits[i], font=("Helvetica", 200), fg="white", bg="black", width=1)
        label.pack(side="left", padx=10)

        def make_handler(index=i, label_ref=label):
            def handler(event):
                if event.y < label_ref.winfo_height() / 2:
                    increment(index)
                else:
                    decrement(index)
            return handler

        label.bind("<Button-1>", make_handler())
        digit_labels.append(label)

    colon = tk.Label(frame, text=":", font=("Helvetica", 200), fg="white", bg="black")
    colon.pack(side="left")

    for i in range(2, 4):
        label = tk.Label(frame, textvariable=digits[i], font=("Helvetica", 200), fg="white", bg="black", width=1)
        label.pack(side="left", padx=10)

        def make_handler(index=i, label_ref=label):
            def handler(event):
                if event.y < label_ref.winfo_height() / 2:
                    increment(index)
                else:
                    decrement(index)
            return handler

        label.bind("<Button-1>", make_handler())
        digit_labels.append(label)

# -- Entry Point --
if __name__ == "__main__":
    print("Countdown Timer Started")
    primary = get_monitors()[0]
    launch_controller_window(primary)
    root.mainloop()
