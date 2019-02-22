import tkinter as tk
from tkinter import messagebox
import webbrowser as wb
from Main import run
from Tabulate import order_by_total_pts, get_overalls, get_round_medals
from GenerateFiles import build_individuals, build_placers, build_round_placers
import os

title_font = ('times', 20, 'bold')
top_label_font = ('times', 12)
small_label_font = ('times', 10)
label_font = ('helvetica', 12)
null_font = ('times', 7)


def go_to_site(ext=''):
    """(str) -> NoneType
    Opens the website for ease of access, ext is any extension required.
    """
    wb.open('https://www.autofeis.com/' + ext)


class Window(tk.Tk):

    def __init__(self, parent):
        tk.Tk.__init__(self, parent)
        self.parent = parent
        self.version = '0.8.6'
        self.vars = list()
        self.minsize(width=500, height=500)
        self.maxsize(width=500, height=500)
        self.center()
        self.window = tk.Canvas(self, width=500, height=500)
        self.window.pack()
        self.judge_count = 0
        self.pic_names = list()
        self.ext = ''
        self.count = 0
        self.judge = list()
        self.judge_names = list()
        self.marks = list()
        self.feis_name = None
        self.checks = list()

        self.init_welcome()

    def initialize(self):
        """(Window) -> NoneType
        Creates everything which should be uniform in each window.
        """
        l1 = tk.Label(self, text="AutoFeis", font=title_font, fg="purple")
        l1.place(x=5, y=5)

        l2 = tk.Label(self, text="Spencer McMurray 2018", font=top_label_font)
        l2.place(x=335, y=15)

        l3 = tk.Label(self, text=self.version, font=small_label_font)
        l3.place(x=460, y=0)

        b1 = tk.Button(self, command=lambda: go_to_site(), text="Website", font=top_label_font, bg='white', fg='purple')
        b1.place(x=0, y=468)

        self.window.create_line(0, 42, 500, 42)
        self.window.create_line(125, 42, 125, 0)

    def init_welcome(self):
        """(Window) -> NoneType
        Initializes the welcome screen.
        """
        self.reset()

        l1 = tk.Label(self, text='Welcome to AutoFeis!', font=label_font)
        l1.place(x=250, y=150, anchor='center')

        self.feis_name = tk.StringVar()
        self.feis_name.set("Enter Feis Name")
        e1 = tk.Entry(self, width=50, textvariable=self.feis_name)
        e1.place(x=250, y=200, anchor="center")

        b1 = tk.Button(self, command=self.init_feis_menu, text="Next", width=25, bg='white', fg='purple')
        b1.place(x=250, y=250, anchor="center")

    def init_feis_menu(self):
        """(Window) -> NoneType
        Initializes the feis menu.
        """
        self.reset()
        self.super_reset()

        b1 = tk.Button(self, text="New Competition", command=self.init_new_comp, fg="purple", bg="white",
                       font=label_font)
        b1.place(x=250, y=175, anchor="center")

        b1 = tk.Button(self, text="Past Competitions", command=lambda: go_to_site(), fg="purple", bg="white",
                       font=label_font)
        b1.place(x=250, y=225, anchor="center")

        back = tk.Button(self, command=self.init_welcome, text="Back",
                         font=label_font, fg="purple", bg="white")
        back.place(x=451, y=469)

    def init_new_comp(self):
        """(Window) -> NoneType
        Initializes the new competition menu.
        """
        self.reset()
        self.vars = list()
        self.judge_count = 0
        self.judge_names = list()
        choices = [1, 2, 3]

        l1 = tk.Label(self, text="Competition Name:", font=label_font)
        l1.place(x=10, y=50)

        self.vars.append(tk.StringVar())
        e1 = tk.Entry(self, width=50, textvariable=self.vars[0])
        e1.place(x=170, y=52)

        l2 = tk.Label(self, text="Number Of Rounds:", font=label_font)
        l2.place(x=10, y=100)

        self.vars.append(tk.StringVar())
        self.vars[-1].set(choices[0])
        d1 = tk.OptionMenu(self, self.vars[-1], *choices)
        d1.place(x=170, y=102)

        l3 = tk.Label(self, text="Number of Judges:", font=label_font)
        l3.place(x=10, y=150)

        self.vars.append(tk.StringVar())
        self.vars[-1].set(choices[0])
        d2 = tk.OptionMenu(self, self.vars[-1], *choices)
        d2.place(x=170, y=152)

        b1 = tk.Button(self, command=self.init_enter_sheets, text="Create", fg="purple", bg="white", font=label_font)
        b1.place(x=413, y=200)

        back = tk.Button(self, command=self.init_feis_menu, text="Back", font=label_font, fg="purple", bg="white")
        back.place(x=451, y=469)

    def init_enter_sheets(self):
        """(Window) -> NoneType
        Initializes the screen to enter scoresheets.
        """
        self.reset()

        if not os.path.exists("../AutoFeis Git/to_print/" + self.vars[0].get()):
            os.makedirs("../AutoFeis Git/to_print/" + self.vars[0].get())

        self.count = 0
        if self.judge != list():
            self.marks.append(self.judge)
        self.judge = list()
        if len(self.vars) > 3:
            self.vars.pop()

        self.pic_names = list()
        self.judge_count += 1

        l0 = tk.Label(self, text="Upload the scoresheets one at a time using the upload button, then", font=label_font)
        l0.place(x=10, y=50)

        l0 = tk.Label(self, text="hit the 'Next' button once all scoresheets are uploaded for this judge",
                      font=label_font)
        l0.place(x=10, y=75)

        l1 = tk.Label(self, text="Judge " + str(self.judge_count) + ":", font=label_font)
        l1.place(x=10, y=125)

        self.vars.append(tk.StringVar())
        e1 = tk.Entry(self, width=25, textvariable=self.vars[-1])
        e1.place(x=85, y=127)
        e1.insert(0, "Judge Name")

        l2 = tk.Label(self, text="Hitting next may take a minute as it is reading. Do not exit!", font=label_font)
        l2.place(x=10, y=175)

        b1 = tk.Button(self, command=self.get_file, text="Upload Scoresheet", fg="purple", bg="white")
        b1.place(x=250, y=120)

        b2 = tk.Button(self, command=self.init_sign_off, text="Next", fg="purple", bg="white")
        b2.place(x=375, y=120)

    def init_sign_off(self):
        """(Window) -> NoneType
        Initializes the sign off screen
        """
        self.reset()

        self.judge_names.append(self.vars[-1].get())
        # vars[0] is competition name, vars[-1] is the latest judge.
        text = self.vars[0].get() + ": " + self.vars[-1].get() + " Sign-off Sheet #" + str(self.count + 1)
        l1 = tk.Label(self, text=text, font=label_font)
        l1.place(x=10, y=50)

        self.display_sign_off()

        # Force it to go through a fcn to check for obvious human errors(mark>100, dancer_num not in db, etc)
        if self.count + 1 == len(self.pic_names):
            if int(self.vars[2].get()) == self.judge_count:
                b1 = tk.Button(self, command=self.verify_valid_sign_off, text="Get Overalls", font=label_font,
                               fg="purple", bg="white")
            else:
                b1 = tk.Button(self, command=self.verify_valid_sign_off, text="Next Judge", font=label_font,
                               fg="purple", bg="white")
        else:
            b1 = tk.Button(self, command=self.verify_valid_sign_off, text="Next Sheet", font=label_font, fg="purple",
                           bg="white")
        b1.place(x=300, y=469)

        self.count += 1

    def init_get_overalls(self):
        """(Window) -> NoneType
        Initializes the screen to get the overall marks.
        """
        self.reset()
        self.marks.append(self.judge)

        marks = list()
        for judge in self.marks:
            new_judge = list()
            for dancer in judge:
                # Dancer number will only be -1 if dancer has been nullified, so skip them.
                if dancer[0].get() == '-1':
                    continue
                new_dancer = list()
                for item in dancer:
                    new_dancer.append(float(item.get()))
                new_judge.append(new_dancer)
            marks.append(new_judge)

        for i in range(len(self.marks)):
            self.marks[i] = order_by_total_pts(marks[i])

        judge_for_round = len(self.marks) == len(self.marks[0]) - 1
        overalls = get_overalls(self.marks)
        round_medals = get_round_medals(overalls, judge_for_round)

        b1 = tk.Button(self, command=lambda: build_individuals(overalls, self.feis_name.get(),
                                                               self.vars[0].get(), self.judge_names),
                       text="Create Individual Dancer Sheets", font=label_font, fg="purple", bg="white")
        b1.place(x=250, y=150, anchor="center")

        # Add a check box to include names or not(for privacy/feis needs/posted results)

        b2 = tk.Button(self, command=lambda: build_placers(overalls, self.vars[0].get()),
                       text="Create Overall Placed Dancers Sheet", font=label_font, fg="purple", bg="white")
        b2.place(x=250, y=200, anchor="center")

        b3 = tk.Button(self, command=lambda: build_round_placers(round_medals, self.vars[0].get(), self.judge_names,
                                                                 judge_for_round),
                       text="Create Round Medals Sheet", font=label_font, fg="purple", bg="white")
        b3.place(x=250, y=250, anchor="center")

        # Add Prompt
        b4 = tk.Button(self, command=self.init_feis_menu, text="Complete This Competition", font=label_font,
                       fg="purple", bg="white")
        b4.place(x=250, y=400, anchor="center")

    def verify_valid_sign_off(self):
        """(Window) -> NoneType
        Creates a message to display to the screen if invalid input has been given.
        """
        self.null_them()
        err = ''
        nums = set()
        for dancer in self.judge:
            if dancer[0].get() in nums and dancer[0].get() != '-1':
                err += 'Dancer number: ' + str(dancer[0].get()) + ' has been found multiple times\n'
            nums.add(dancer[0].get())
            try:
                valid = int(float(dancer[0].get())) == 0
            except ValueError:
                err += 'Dancer number: ' + str(dancer[0].get()) + "doesn't have a valid dancer number\n"
            # Check if dancer[0].get() is in the db!
            for i in range(1, len(dancer)):
                try:
                    if int(float(dancer[i].get())) not in range(101):
                        err += ('Dancer number: ' + str(dancer[0].get()) + ' has the invalid mark: '
                                + str(dancer[i].get()) + '\n')
                except ValueError:
                    err += ('Dancer number: ' + str(dancer[0].get()) + ' has the invalid mark: '
                            + str(dancer[i].get()) + '\n')
            been_seen = len(self.marks) == 0
            for old_dancer in self.marks:
                if dancer[0].get() == old_dancer[0].get():
                    been_seen = True
            if not been_seen:
                err += 'Dancer number: ' + str(dancer[0].get()) + ' is here, but not on other judges sheets\n'

        if len(err) != 0:
            messagebox.showinfo("Entry Error", err[:-1])
        else:
            if self.count == len(self.pic_names):
                if int(self.vars[2].get()) == self.judge_count:
                    self.init_get_overalls()
                else:
                    self.init_enter_sheets()
            else:
                self.init_sign_off()

    def display_sign_off(self):
        """(Window) -> NoneType
        Helper function to display the sign off info.
        """
        rounds = ""
        for i in range(int(self.vars[1].get())):
            rounds += "     Round " + str(i + 1)
        rounds += '     Remove?'

        l1 = tk.Label(self, text="Dancer Number" + rounds, font=label_font)
        l1.place(x=10, y=80)

        # Get marks from AutoAssist
        assist_marks = run(self.pic_names[self.count], int(self.vars[1].get()))

        # Dancer Numbers
        nums = list()
        for i in range(len(assist_marks)):
            nums.append(tk.StringVar())
            e = tk.Entry(self, width=15, textvariable=nums[-1])
            e.place(x=14, y=110 + 20 * i)
            e.insert(0, str(assist_marks[i][0]))

        marks = list()
        for i in range(int(self.vars[1].get())):
            items = list()
            # Marks for Round i + 1
            for j in range(len(assist_marks)):
                # Assume any number found greater than 100 is a decimal to simplify our vision complexity.
                if assist_marks[j][i + 1] > 100:
                    str_curr = str(assist_marks[j][i + 1])
                    assist_marks[j][i + 1] = float(str_curr[:2] + '.' + str_curr[2])
                items.append(tk.StringVar())
                e = tk.Entry(self, width=10, textvariable=items[-1])
                e.place(x=143 + 78 * i, y=110 + 20 * j)
                e.insert(0, str(assist_marks[j][i + 1]))
                # Insert the NULLIFY button
                if i + 1 == int(self.vars[1].get()):
                    self.checks.append(tk.IntVar())
                    c = tk.Checkbutton(self, variable=self.checks[-1])
                    c.place(x=400, y=107 + 20 * j)

            marks.append(items)

        # Setup all of the judge's marks.
        for i in range(len(nums)):
            dancer_marks = list()
            for k in range(len(marks)):
                dancer_marks.append(marks[k][i])
            self.judge.append([nums[i]] + dancer_marks)

    def null_them(self):
        """(Window) -> NoneType
        Nullifies all dancers will their remove box checked.
        """
        for i in range(len(self.checks)):
            # If the i'th box is checked, nullify the i'th dancer.
            if self.checks[i].get():
                self.judge[i][0].set('-1')

    def get_file(self):
        """(Window) -> NoneType
        Opens a prompt for getting file location, then returns that file location.
        """
        from tkinter.filedialog import askopenfilename

        # Change later.
        name = askopenfilename(initialdir="marksheets", filetypes=(("Image File", "*.png"), ("Image File", "*.jpg")),
                               title="Choose a file.")
        self.pic_names.append(name)

    def center(self):
        """(Window) -> NoneType
        Centers the window.
        """
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def reset(self):
        """(Window) -> NoneType
        Resets the screen.
        """
        self.ext = ''
        self.checks = list()
        for child in self.winfo_children():
            child.destroy()
        self.window = tk.Canvas(self, width=500, height=500)
        self.window.pack()
        self.initialize()

    def super_reset(self):
        """(Window) -> NoneType
        Resets the screen, and sets up for a new competition.
        """
        for child in self.winfo_children():
            child.destroy()
        self.window = tk.Canvas(self, width=500, height=500)
        self.window.pack()
        self.judge_count = 0
        self.pic_names = list()
        self.ext = ''
        self.count = 0
        self.judge = list()
        self.judge_names = list()
        self.marks = list()

        self.initialize()


if __name__ == '__main__':
    app = Window(None)
    app.title('AutoFeis')
    img = tk.PhotoImage(file='icon.gif')
    app.tk.call('wm', 'iconphoto', app._w, img)
    app.mainloop()
