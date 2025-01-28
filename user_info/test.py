from tkinter import ttk, TRUE
import tkinter as tk
from datetime import datetime
import pandas as pd
from user_data import userData
import pickle
import tkinter.font as tkFont
from tkinter import PhotoImage
from PIL import Image, ImageTk


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LogGuard AI")
        self.config(bg='#23013b')
        self.geometry('1920x1080')

        # Dictionary to hold frames
        self.frames = {}

        # Create and store each screen
        for F in (FirstScreen, SecondScreen, ThirdScreen):
            frame = F(parent=self, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        try:
            with open("user_data.pkl", "rb") as file:
                self.userData = pickle.load(file)
        except FileNotFoundError as e:
            self.userData = userData()

        if self.userData.isLoggedIn:
            self.show_frame(ThirdScreen)
        else :
            self.show_frame(FirstScreen)

    def show_frame(self, frame_class):
        """Display the given frame."""
        frame = self.frames[frame_class]
        frame.tkraise()


class FirstScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        font_large_Comic_Sans_MS = tkFont.Font(family="Comic Sans MS", size=40)
        font_small_Comic_Sans_MS = tkFont.Font(family="Comic Sans MS", size=20)
        font_regular = tkFont.Font(family="Inter", size=10)

        # StringVar for the fields
        self.name = tk.StringVar(value="enter name")
        self.email = tk.StringVar(value="enter email")
        self.startingHours = tk.StringVar(value="start")
        self.endingHours = tk.StringVar(value="end")
        self.checkboxString = tk.StringVar()

        # Load and resize image
        image_path = "logo.jpg"  # Replace with the path to your image file
        custom_image = Image.open(image_path)  # Open the image using PIL

        # Resize the image to cover the left half of the window (960x1080)
        custom_image_resized = custom_image.resize((960, 800), Image.Resampling.LANCZOS)

        # Convert the resized image to a format Tkinter can display
        self.custom_image_tk = ImageTk.PhotoImage(custom_image_resized)

        # Banner frame with the resized image
        banner_image = tk.Label(self, image=self.custom_image_tk)
        banner_image.grid(row=0, column=0, rowspan=5, sticky="ns")  # Spanning the left half, full height

        # Log-in frame
        log_in = tk.Frame(self, bg='white')
        log_in.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")  # Sticky in both directions for stretching

        # Ensure the column for the log_in frame stretches
        self.grid_columnconfigure(1, weight=1)  # Column 1 should stretch

        # Ensure the row for the log_in frame stretches
        self.grid_rowconfigure(0, weight=1)  # Row 0 should stretch

        # Add log-in details
        tk.Label(log_in, text="Log Guard", bg='white', font=font_large_Comic_Sans_MS).grid(row=0, column=0, pady=10)
        tk.Label(log_in, text="Setup", bg='white', font=font_small_Comic_Sans_MS).grid(row=1, column=0, pady=5)

        tk.Label(log_in, text="Name", bg='white', font=font_regular).grid(row=2, column=0, pady=5)
        tk.Entry(log_in, textvariable=self.name).grid(row=2, column=1, pady=5)

        tk.Label(log_in, text="Email", bg='white', font=font_regular).grid(row=3, column=0, pady=5)
        tk.Entry(log_in, textvariable=self.email).grid(row=3, column=1, pady=5)

        tk.Label(log_in, text="You will get reports on the provided email", bg='white', font="Satoshi 5 bold").grid(row=4, column=0, columnspan=2, pady=10)

        tk.Label(log_in, text="Enter working hours:", bg='white', font=font_regular).grid(row=5, column=0, pady=5)
        tk.Entry(log_in, textvariable=self.startingHours).grid(row=5, column=1, pady=5)
        tk.Label(log_in, text="to", bg='white', font=font_regular).grid(row=6, column=0, pady=5)
        tk.Entry(log_in, textvariable=self.endingHours).grid(row=6, column=1, pady=5)

        tk.Label(log_in, text="Summary Frequency", bg='white', font=font_regular).grid(row=7, column=0, pady=5)

        items = ('Daily', 'Weekly', 'Monthly')
        food_string = tk.StringVar(value=items[0])
        combo = ttk.Combobox(log_in, textvariable=food_string)
        combo['values'] = items
        combo.grid(row=7, column=1, pady=5)

        # Agree to terms checkbox
        agree_check = tk.Checkbutton(
            log_in,
            background="white",
            text='I agree to terms and conditions',
            variable=self.checkboxString,
            command=lambda: print(self.checkboxString.get())
        )
        agree_check.grid(row=8, column=0, columnspan=2, pady=10)

        # Continue button
        btn_continue = tk.Button(log_in, text="Continue", bg="#71f0e7", padx=10, pady=10, bd=0, fg="white",
                                 activebackground="#71f0e7", activeforeground="white", command=self.saveAndNext)
        btn_continue.grid(row=9, column=0, columnspan=2, pady=10)

    def saveAndNext(self):
        # Save the entered data
        with open("user_data.pkl", "wb") as file:
            newUserData = userData(
                self.name.get(),
                self.email.get(),
                self.startingHours.get(),
                self.endingHours.get(),
                True,
            )
            pickle.dump(newUserData, file)
        self.controller.show_frame(ThirdScreen)






class SecondScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Second Screen")

        # Create a notebook as a menu at the top
        self.menu = ttk.Notebook(self)
        self.menu.grid(row=0, column=0, sticky="ew")  # Stretch across the top

        # Add tabs to the notebook
        self.dashboard_tab = ttk.Frame(self.menu)
        self.settings_tab = ttk.Frame(self.menu)
        self.menu.add(self.dashboard_tab, text="Dashboard")
        self.menu.add(self.settings_tab, text="Settings")

        # Bind tab changes to a handler
        self.menu.bind("<<NotebookTabChanged>>", self.on_tab_selected)

        # Create a content frame where content will change dynamically
        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Configure grid to expand
        self.grid_rowconfigure(1, weight=1)  # Content frame row should expand
        self.grid_columnconfigure(0, weight=1)  # Content frame column should expand
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Display initial content for "Dashboard"
        self.show_dashboard()

    def show_dashboard(self):
        """Display the Dashboard content."""
        self.clear_content_frame()  # Clear previous content

        # Create the Treeview inside the content frame
        tree = ttk.Treeview(self.content_frame, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")  # Make the Treeview fill the content frame

        # Add a scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")  # Place scrollbar to the right

        # Load data into the Treeview
        self.load_csv(tree)

    def load_csv(self, tree):
        """Load data from a CSV file into the Treeview."""
        try:
            # Read the CSV file
            df = pd.read_csv("exported_logons.csv")

            # Configure the Treeview columns
            tree["columns"] = list(df.columns)
            for col in df.columns:
                tree.heading(col, text=col)  # Set column headings
                tree.column(col, width=100, anchor="center")  # Set column widths

            # Add data rows to the Treeview
            for _, row in df.iterrows():
                tree.insert("", "end", values=list(row))
        except FileNotFoundError:
            label = tk.Label(
                self.content_frame,
                text="CSV file not found. Please make sure 'exported_logons.csv' exists.",
                fg="red",
                font=("Arial", 12),
            )
            label.grid(pady=10)

    def show_settings(self):
        """Display the Settings content."""
        self.clear_content_frame()  # Clear previous content

        # Load and display user data setup form from FirstScreen
        try:
            with open("user_data.pkl", "rb") as file:
                user_data = pickle.load(file)
        except FileNotFoundError:
            user_data = userData()

        # Fonts
        font_large_Comic_Sans_MS = tkFont.Font(family="Comic Sans MS", size=40)
        font_small_Comic_Sans_MS = tkFont.Font(family="Comic Sans MS", size=20)
        font_regular = tkFont.Font(family="Inter", size=10)

        # StringVars for the Entry fields
        name = tk.StringVar(value=user_data.name)
        email = tk.StringVar(value=user_data.email)
        starting_hours = tk.StringVar(value=user_data.startingHours)
        ending_hours = tk.StringVar(value=user_data.endingHours)

        # Load and resize image
        image_path = "logo.png"  # Replace with the path to your image file
        custom_image = Image.open(image_path)  # Open the image using PIL
        custom_image_resized = custom_image.resize((960, 1080), Image.Resampling.LANCZOS)  # Resize
        self.custom_image_tk = ImageTk.PhotoImage(custom_image_resized)

        # Banner frame with the resized image
        banner_image = tk.Label(self.content_frame, image=self.custom_image_tk)
        banner_image.grid(row=0, column=0, rowspan=5, sticky="ns")  # Spanning the left half, full height

        # Settings frame
        settings_frame = tk.Frame(self.content_frame, bg='white')
        settings_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

        # Ensure the column for the settings_frame stretches
        self.content_frame.grid_columnconfigure(1, weight=1)  # Column 1 should stretch

        # Ensure the row for the settings_frame stretches
        self.content_frame.grid_rowconfigure(0, weight=1)  # Row 0 should stretch

        # Add settings details
        tk.Label(settings_frame, text="Settings", bg='white', font=font_large_Comic_Sans_MS).grid(row=0, column=0,
                                                                                                  pady=10)
        tk.Label(settings_frame, text="Adjust your details", bg='white', font=font_small_Comic_Sans_MS).grid(row=1,
                                                                                                             column=0,
                                                                                                             pady=5)

        tk.Label(settings_frame, text="Name", bg='white', font=font_regular).grid(row=2, column=0, pady=5)
        tk.Entry(settings_frame, textvariable=name).grid(row=2, column=1, pady=5)

        tk.Label(settings_frame, text="Email", bg='white', font=font_regular).grid(row=3, column=0, pady=5)
        tk.Entry(settings_frame, textvariable=email).grid(row=3, column=1, pady=5)

        tk.Label(settings_frame, text="Enter working hours:", bg='white', font=font_regular).grid(row=4, column=0,
                                                                                                  pady=5)
        tk.Entry(settings_frame, textvariable=starting_hours).grid(row=4, column=1, pady=5)
        tk.Label(settings_frame, text="to", bg='white', font=font_regular).grid(row=5, column=0, pady=5)
        tk.Entry(settings_frame, textvariable=ending_hours).grid(row=5, column=1, pady=5)

        tk.Label(settings_frame, text="Summary Frequency", bg='white', font=font_regular).grid(row=6, column=0, pady=5)

        items = ('Daily', 'Weekly', 'Monthly')
        frequency_string = tk.StringVar(value=items[0])
        combo = ttk.Combobox(settings_frame, textvariable=frequency_string)
        combo['values'] = items
        combo.grid(row=6, column=1, pady=5)

        # Save button
        tk.Button(
            settings_frame,
            text="Save",
            command=lambda: self.save_user_data(name.get(), email.get(), starting_hours.get(), ending_hours.get())
        ).grid(row=7, column=0, columnspan=2, pady=10)

    def save_user_data(self, name, email, starting_hours, ending_hours):
        """Save user data to a pickle file."""
        with open("user_data.pkl", "wb") as file:
            data = userData(name, email, starting_hours, ending_hours, True)
            pickle.dump(data, file)

    def clear_content_frame(self):
        """Remove all widgets from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def on_tab_selected(self, event):
        """Handle tab selection."""
        selected_tab = self.menu.tab(self.menu.select(), "text")  # Get the text of the selected tab
        if selected_tab == "Dashboard":
            self.show_dashboard()
        elif selected_tab == "Settings":
            self.show_settings()






class ThirdScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
         
        # Label for the screen title
        label = tk.Label(self, text="dashboard", font=("Arial", 36))
        label.place(x=550,y=100)

        # Button to navigate back to the home screen
        button = tk.Button(self, text="generate report",
                           command=lambda:print("report add soon"))
        button.place(x=600,y=200)

        button = tk.Button(self, text="view history",
                   command=lambda: controller.show_frame(SecondScreen))
        button.place(x=600,y=250)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()