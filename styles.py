from tkinter import font, PhotoImage

# Initialize fonts (without creating root window directly)
standard10_font = None  # Will be initialized after creating root window
bold10_font = None
standard12_font = None
bold12_font = None
name_font = None

def init_fonts():
    global standard10_font, bold10_font, standard12_font, bold12_font, name_font
    standard10_font = font.Font(family="Helvetica", size=10)
    bold10_font = font.Font(family="Helvetica", size=10, weight="bold")
    standard12_font = font.Font(family="Helvetica", size=12)
    bold12_font = font.Font(family="Helvetica", size=12, weight="bold")
    name_font = font.Font(family="Helvetica", size=16, weight="bold")# icons
