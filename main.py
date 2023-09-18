import tkinter as tk
import tkinter.scrolledtext as st
from typing import TypeVar, Generic

T = TypeVar('T')


class Time(Generic[T]):
    def __init__(self: T, hrs: int = 0, mins: int = 0, secs: int = 0) -> None:
        self.hrs = hrs
        self.mins = mins
        self.secs = secs
        self.negStatus = ""

    def clear(self: T) -> None:
        """Desc: Set time to 0:00:00"""
        self.hrs = 0
        self.mins = 0
        self.secs = 0
        self.negStatus = ""

    def set(self: T, time_string: str) -> None:
        """Desc: Turn an inputted string into a Time object
        Pre: Only numbers and colons in the string, no more than 2 colons"""
        # Address negativity
        if time_string[0] == "-":
            self.negStatus = "-"
            time_string = time_string[1:]
        else:
            self.negStatus = ""

        # Address implied zero in seconds place if string ends in colon
        if time_string[-1] == ":":
            time_string += "0"

        time_array = time_string.split(":")
        time_array = [int(i) for i in time_array]

        length = len(time_array)
        # Only seconds are given:
        if length == 1:
            self.hrs = 0
            self.mins = 0
            self.secs = time_array[0]
        # Minutes & seconds are given:
        elif length == 2:
            self.hrs = 0
            self.mins = time_array[0]
            self.secs = time_array[1]
        # Hours, minutes, & seconds are given:
        elif length == 3:
            self.hrs = time_array[0]
            self.mins = time_array[1]
            self.secs = time_array[2]
        self.adjust_units()

    def convert_to_secs(self: T) -> None:
        """Desc: set seconds equal to the total number of seconds in the time
        (for addition/subtraction)"""

        self.mins += 60 * self.hrs
        self.hrs = 0
        self.secs += 60 * self.mins
        self.mins = 0
        if self.negStatus == "-":
            self.secs *= -1

    def abs(self: T) -> None:
        """Desc: Set attributes to absolute value and negStatus to empty"""
        self.hrs = abs(self.hrs)
        self.mins = abs(self.mins)
        self.secs = abs(self.secs)
        self.negStatus = ""

    def adjust_units(self: T) -> None:
        """Desc: After a time change, call this function to maintain base-60
        units (ex: 90 secs -> 1min 30secs)"""
        if self.secs < 0:
            self.negStatus = "-"
            self.secs *= -1
        # If secs>59, turn as many seconds into minutes as possible
        if self.secs >= 60:
            spillover = self.secs // 60
            self.secs -= spillover * 60
            self.mins += spillover
        # If mins>59, turn as many minutes into hours as possible
        if self.mins >= 60:
            spillover = self.mins // 60
            self.mins -= spillover * 60
            self.hrs += spillover

    def __str__(self: T) -> str:
        """Desc: Print Time in the form (-)[hours]:[minutes]:[seconds]"""
        return '{}{}:{:02d}:{:02d}'.format(self.negStatus, self.hrs, self.mins, self.secs)

    def __add__(self: T, other: T) -> T:
        """Desc: Add two time objects by adding their total seconds and
        readjusting the units, return result"""
        temp = Time()
        self.convert_to_secs()
        other.convert_to_secs()
        temp.secs = self.secs + other.secs
        self.adjust_units()
        other.adjust_units()
        temp.adjust_units()
        return temp

    def __sub__(self: T, other: T) -> T:
        """Desc: Subtract two time objects by subtracting their total seconds
        and readjusting the units, return result"""

        temp = Time()
        self.convert_to_secs()
        other.convert_to_secs()
        temp.secs = self.secs - other.secs
        self.adjust_units()
        other.adjust_units()
        temp.adjust_units()
        return temp


def add_to_calc(symbol: any) -> None:
    """Desc: Concatenate symbol to the end of the calculation input string and
    show it in the field"""
    global calc_input_str

    calc_input_str += str(symbol)
    input_field.configure(text=calc_input_str)


def evaluate_calc() -> None:
    """Desc: Evaluate the expression (or replace the answer field if no +/-)"""
    global calc_input_str, answer_field, answer_time

    calc_time = Time()
    # If the calculation input is empty, do nothing
    if calc_input_str == "":
        pass
    # If calculation input doesn't start with +/-, reset the answer field to
    # the calculation input
    elif (calc_input_str[0].isdigit()) or (calc_input_str[0] == ":"):
        answer_time.set(calc_input_str)
        answer_field.configure(text=str(answer_time))
        clear_field()
        history_text.insert("end", ("-" * 24 + "\n"))
        history_text.insert("end", f"{str(answer_time)}\n")
    # If the calculation input starts with +, add the calculation input to the answer field
    elif calc_input_str[0] == "+":
        if calc_input_str != "+":
            last_ans = answer_time
            calc_time.set(calc_input_str[1:])
            answer_time = answer_time + calc_time
            answer_field.configure(text=str(answer_time))
            history_text.insert("end", f"{str(answer_time)} = {str(last_ans)} + {str(calc_time)}\n")
        clear_field()
    # If the calculation input starts with -, subtract the calculation input from the answer field
    elif calc_input_str[0] == "-":
        if calc_input_str != "-":
            last_ans = answer_time
            calc_time.set(calc_input_str)
            answer_time = answer_time + calc_time
            answer_field.configure(text=str(answer_time))
            calc_time.abs()
            history_text.insert("end", f"{str(answer_time)} = {str(last_ans)} - {str(calc_time)}\n")
        clear_field()


def plus() -> None:
    """Desc: Evaluate the current expression (if present), clear the field and␣
    ↪add "+" to the calculation input string"""
    global calc_input_str

    if calc_input_str == "+" or calc_input_str == "-":
        clear_field()
    elif calc_input_str != "":
        evaluate_calc()
    add_to_calc("+")


def minus() -> None:
    """Desc: Evaluate the current expression (if present), clear the field and␣
    ↪add "-" to the calculation input string"""
    global calc_input_str

    if calc_input_str == "+" or calc_input_str == "-":
        clear_field()
    elif calc_input_str != "":
        evaluate_calc()
    add_to_calc("-")


def clear_field() -> None:
    """Desc: Empty the calculation input string"""
    global calc_input_str, answer_field, input_field

    calc_input_str = ""
    input_field.configure(text=calc_input_str)


def delete() -> None:
    """Desc: Remove the most recently added character from the calculator input␣
    ↪string"""
    global calc_input_str, input_field

    calc_input_str = calc_input_str[:-1]
    input_field.configure(text=calc_input_str)


def show_hist() -> None:
    """Desc: Flip to the history page (and prevent typing in text box)"""
    global history_pg
    history_pg.lift()
    history_text.configure(state='disabled')


def clear_hist() -> None:
    """Desc: Delete all text in the history log"""
    global history_text
    history_text.configure(state='normal')
    history_text.delete("1.0", "end")
    history_text.configure(state='disabled')


def show_main() -> None:
    """Desc: Flip to the main page"""
    global history_text, main_pg
    history_text.configure(state='normal')
    main_pg.lift()


def add_colon() -> None:
    """Desc: Add colon to the string (and 0's before if necessary). Don't add␣
    ↪if there are already 2 colons"""
    global calc_input_str

    if calc_input_str in {"", "+", "-"}:
        add_to_calc("0:")
    else:
        num_col = 0
        for i in range(len(calc_input_str)):
            if calc_input_str[i] == ":":
                num_col += 1
        if num_col < 2 and calc_input_str[-1].isdigit():
            add_to_calc(":")
        elif num_col == 1:
            add_to_calc("00:")


if __name__ == '__main__':
    calc_input_str = ""
    answer_time = Time()

    # Create window
    root = tk.Tk()
    root.geometry("262x280")
    root.title("Time Calculator")

    # Create calculation history page
    history_pg = tk.Frame(root)
    history_pg.grid()
    history_pg.configure(bg="gray17")
    history_pg.place(in_=root, x=0, y=0, relwidth=1, relheight=1)

    history_text = st.ScrolledText(history_pg, width=26, height=12, font=("Arial", 13), bg="gray80")
    history_text.grid(row=0, column=0, padx=3, pady=4, columnspan=2)
    btn_back_hst = tk.Button(history_pg, text="Back", command=lambda: show_main(), font=("Arial", 14), bg="gray27",
                             fg="snow")
    btn_back_hst.grid(row=1, column=0, sticky="ew")
    btn_clr_hst = tk.Button(history_pg, text="Clear", command=lambda: clear_hist(), font=("Arial", 14), bg="gray27",
                            fg="snow")
    btn_clr_hst.grid(row=1, column=1, sticky="ew")

    # Create help page
    help_pg = tk.Frame(root)
    help_pg.grid()
    help_pg.configure(bg="gray17")
    help_pg.place(in_=root, x=0, y=0, relwidth=1, relheight=1)
    help_text = tk.Text(help_pg, width=40, height=16, font=("Arial", 8), bg="gray80")
    help_text.grid(row=0, column=0, padx=8, pady=5)
    help_text.insert(index="1.0", chars="Welcome to the Time Calculator!\n\n"
                                        "Press numbers/\":\" with your mouse or keyboard\n"
                                        "to input a time (automatically H:M:S). Press \"Del\"\n"
                                        "to remove the last character.\n\n"
                                        "Then, press + or - to enter a time that will be\n"
                                        "added/subtracted to/from the previous time.\n"
                                        "Press =, +, or - to evaluate.\n\n"
                                        "Entering a time without + or - at the front will start\n"
                                        "a new round of calculations.\n\n"
                                        "Press \"Hist\" to see all past calculation steps and\n\n"
                                        "Press \"Back\" to exit this help page.")
    help_text.configure(state='disabled')
    btn_back_hlp = tk.Button(help_pg, text="Back", command=lambda: show_main(), font=("Arial", 14), bg="gray27",
                         fg="snow")
    btn_back_hlp.grid(row=1, column=0, pady=3, sticky="ew")

    # Create main calculator page
    main_pg = tk.Frame(root)
    main_pg.grid()
    main_pg.configure(bg="gray17")
    main_pg.place(in_=root, x=0, y=0, relwidth=1, relheight=1)

    # Answer and input text bars (main page)
    answer_field = tk.Label(main_pg, height=1, width=16, font=("Arial", 20), anchor="e", bg="gray17", fg="snow")
    answer_field.grid(columnspan=4)
    input_field = tk.Label(main_pg, height=1, width=16, font=("Arial", 20), anchor="e", bg="gray80")
    input_field.grid(columnspan=4)

    # Buttons (main page)
    btn1 = tk.Button(main_pg, text="1", command=lambda: add_to_calc("1"), font=("Arial", 14), bg="gray27", fg="snow")
    btn1.grid(row=4, column=0, pady=1, padx=1, sticky="ew")
    btn2 = tk.Button(main_pg, text="2", command=lambda: add_to_calc("2"), font=("Arial", 14), bg="gray27", fg="snow")
    btn2.grid(row=4, column=1, pady=1, padx=1, sticky="ew")
    btn3 = tk.Button(main_pg, text="3", command=lambda: add_to_calc("3"), font=("Arial", 14), bg="gray27", fg="snow")
    btn3.grid(row=4, column=2, pady=1, padx=1, sticky="ew")
    btn4 = tk.Button(main_pg, text="4", command=lambda: add_to_calc("4"), font=("Arial", 14), bg="gray27", fg="snow")
    btn4.grid(row=3, column=0, pady=1, padx=1, sticky="ew")
    btn5 = tk.Button(main_pg, text="5", command=lambda: add_to_calc("5"), font=("Arial", 14), bg="gray27", fg="snow")
    btn5.grid(row=3, column=1, pady=1, padx=1, sticky="ew")
    btn6 = tk.Button(main_pg, text="6", command=lambda: add_to_calc("6"), font=("Arial", 14), bg="gray27", fg="snow")
    btn6.grid(row=3, column=2, pady=1, padx=1, sticky="ew")
    btn7 = tk.Button(main_pg, text="7", command=lambda: add_to_calc("7"), font=("Arial", 14), bg="gray27", fg="snow")
    btn7.grid(row=2, column=0, pady=1, padx=1, sticky="ew")
    btn8 = tk.Button(main_pg, text="8", command=lambda: add_to_calc("8"), font=("Arial", 14), bg="gray27", fg="snow")
    btn8.grid(row=2, column=1, pady=1, padx=1, sticky="ew")
    btn9 = tk.Button(main_pg, text="9", command=lambda: add_to_calc("9"), font=("Arial", 14), bg="gray27", fg="snow")
    btn9.grid(row=2, column=2, pady=1, padx=1, sticky="ew")
    btn0 = tk.Button(main_pg, text="0", command=lambda: add_to_calc("0"), font=("Arial", 14), bg="gray27", fg="snow")
    btn0.grid(row=5, column=1, pady=1, padx=1, sticky="ew")
    btn_colon = tk.Button(main_pg, text=":", command=lambda: add_colon(), font=("Arial", 14), bg="gray27", fg="snow")
    btn_colon.grid(row=5, column=0, pady=1, padx=1, sticky="ew")
    btn_hist = tk.Button(main_pg, text="Hist", command=lambda: show_hist(), font=("Arial", 14), bg="gray27", fg="snow")
    btn_hist.grid(row=6, column=0, pady=1, padx=1, sticky="ew", columnspan=2)
    btn_help = tk.Button(main_pg, text="Help", command=lambda: help_pg.lift(), font=("Arial", 14), bg="gray27",
                         fg="snow")
    btn_help.grid(row=6, column=2, pady=1, padx=1, sticky="ew", columnspan=2)
    btn_del = tk.Button(main_pg, text="Del", command=lambda: delete(), font=("Arial", 14), bg="gray27", fg="snow")
    btn_del.grid(row=2, column=3, pady=1, padx=1, sticky="ew")
    btn_plus = tk.Button(main_pg, text="+", command=lambda: plus(), font=("Arial", 14), bg="gray27", fg="snow")
    btn_plus.grid(row=3, column=3, pady=1, padx=1, sticky="ew")
    btn_minus = tk.Button(main_pg, text="-", command=lambda: minus(), font=("Arial", 14), bg="gray27", fg="snow")
    btn_minus.grid(row=4, column=3, pady=1, padx=1, sticky="ew")
    btn_equal = tk.Button(main_pg, text="=", command=lambda: evaluate_calc(), font=("Arial", 14), bg="gray27",
                          fg="snow")
    btn_equal.grid(row=5, column=2, pady=1, padx=1, sticky="ew", columnspan=2)

    # Keybinds for main page
    main_pg.bind_all('<KeyPress-1>', lambda x: add_to_calc("1"))
    main_pg.bind_all('<KeyPress-2>', lambda x: add_to_calc("2"), add="+")
    main_pg.bind_all('<KeyPress-3>', lambda x: add_to_calc("3"), add="+")
    main_pg.bind_all('<KeyPress-4>', lambda x: add_to_calc("4"), add="+")
    main_pg.bind_all('<KeyPress-5>', lambda x: add_to_calc("5"), add="+")
    main_pg.bind_all('<KeyPress-6>', lambda x: add_to_calc("6"), add="+")
    main_pg.bind_all('<KeyPress-7>', lambda x: add_to_calc("7"), add="+")
    main_pg.bind_all('<KeyPress-8>', lambda x: add_to_calc("8"), add="+")
    main_pg.bind_all('<KeyPress-9>', lambda x: add_to_calc("9"), add="+")
    main_pg.bind_all('<KeyPress-0>', lambda x: add_to_calc("0"), add="+")
    main_pg.bind_all('<KeyPress-:>', lambda x: add_colon(), add="+")
    main_pg.bind_all('<KeyPress-+>', lambda x: plus(), add="+")
    main_pg.bind_all('<minus>', lambda x: minus(), add="+")
    main_pg.bind_all('<KeyPress-=>', lambda x: evaluate_calc(), add="+")
    main_pg.bind_all('<Return>', lambda x: evaluate_calc(), add="+")
    main_pg.bind_all('<=>', lambda x: evaluate_calc(), add="+")
    main_pg.bind_all('<Delete>', lambda x: delete(), add="+")
    main_pg.bind_all('<BackSpace>', lambda x: delete(), add="+")

    root.mainloop()
