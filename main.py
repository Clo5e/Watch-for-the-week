import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
from datetime import datetime
import random

class Watch:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

class WatchApp:
    def __init__(self, watch_dir='watches', watch_file='watchlist.txt', form_dir='forms', choosen_dir='choosen'):
        self.watch_dir = watch_dir
        self.watch_file = watch_file
        self.form_dir = form_dir
        self.choosen_dir = choosen_dir
        self.watches = []
        self.week_watches = {}
        self.load_week_watches()

        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)

        if not os.path.exists(self.watch_file) or os.path.getsize(self.watch_file) == 0:
            self.add_watches()
        else:
            self.load_watches()

        if not os.path.exists(self.form_dir):
            os.makedirs(self.form_dir)

        if not os.path.exists(self.choosen_dir):
            os.makedirs(self.choosen_dir)

    def add_watches(self):
        num_watches = simpledialog.askinteger("Dodaj zegarki", "Ile zegarków chcesz dodać?")
        if num_watches == 0:
            return
        for _ in range(num_watches):
            name = simpledialog.askstring("Dodaj zegarek", "Podaj nazwę zegarka:")
            image_path = filedialog.askopenfilename(initialdir=self.watch_dir)
            new_image_path = os.path.join(self.watch_dir, f"{name}.png")
            shutil.copyfile(image_path, new_image_path)
            watch = Watch(name, new_image_path)
            self.watches.append(watch.__dict__)

        with open(self.watch_file, 'w') as f:
            json.dump(self.watches, f)

    def load_watches(self):
        with open(self.watch_file, 'r') as f:
            self.watches = json.load(f)

    def remove_watch(self, watch_name):
        self.watches = [watch for watch in self.watches if watch['name'] != watch_name]
        with open(self.watch_file, 'w') as f:
            json.dump(self.watches, f)
        os.remove(os.path.join(self.watch_dir, f"{watch_name}.png"))

    def modify_watch(self, old_name, new_name=None, new_image_path=None):
        for watch in self.watches:
            if watch['name'] == old_name:
                if new_name:
                    os.rename(watch['image_path'], os.path.join(self.watch_dir, f"{new_name}.png"))
                    watch['name'] = new_name
                    watch['image_path'] = os.path.join(self.watch_dir, f"{new_name}.png")
                if new_image_path:
                    os.remove(watch['image_path'])
                    shutil.copyfile(new_image_path, watch['image_path'])

        with open(self.watch_file, 'w') as f:
            json.dump(self.watches, f)

    def select_watches_for_week(self):
        if len(self.watches) < 5:
            messagebox.showerror("Błąd", "Zbyt mało zegarków. Dodaj więcej zegarków.")
            return
        elif len(self.watches) < 7:
            choosen_watches = random.sample(self.watches, 5)
            week_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek']
        else:
            choosen_watches = random.sample(self.watches, 7)
            week_days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']

        self.week_watches = dict(zip(week_days, choosen_watches))

        choosen_file = os.path.join(self.choosen_dir, f"choosen_watches-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        with open(choosen_file, 'w') as f:
            json.dump(self.week_watches, f)

    def load_week_watches(self):
        choosen_files = os.listdir(self.choosen_dir)
        choosen_files.sort(key=lambda x: datetime.strptime(x.split('-')[1].replace('.txt', ''), '%Y%m%d%H%M%S'))
        last_choosen_file = choosen_files[-1] if choosen_files else None
        if last_choosen_file:
            try:
                with open(os.path.join(self.choosen_dir, last_choosen_file), 'r') as f:
                    self.week_watches = json.load(f)
            except json.JSONDecodeError:
                print(f"Błąd podczas odczytywania pliku {last_choosen_file}. Plik może być pusty lub zawierać niepoprawne dane.")


    def end_of_day_survey(self):
        survey_questions = [
            "Jak oceniasz komfort noszenia zegarka?",
            "Czy zegarek spełnia Twoje oczekiwania?",
            "Czy poleciłbyś ten zegarek innym?",
            "Jak oceniasz wygląd zegarka?",
            "Czy zegarek jest wygodny w użyciu?"
        ]
        survey_answers = []
        for question in survey_questions:
            answer = simpledialog.askstring("Ankieta", question)
            survey_answers.append(answer)

        form_file = os.path.join(self.form_dir, f"form-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        with open(form_file, 'w') as f:
            for question, answer in zip(survey_questions, survey_answers):
                f.write(f"{question}\n{answer}\n")


class WatchAppGUI:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.selected_watch = None
        self.select_watches_for_week_button = tk.Button(self.root, text="Wybór zegarków", command=self.app.select_watches_for_week)
        self.select_watches_for_week_button.pack()
        self.update_buttons()
        self.show_today_watch_button()
        self.show_week_watches_button()
        self.add_watch_button()
        self.remove_watch_button()
        self.modify_watch_button()
        self.survey_button()
        self.add_exit_button()

    def run(self):
        self.root.mainloop()

    def add_watch_button(self):
        button = tk.Button(self.root, text="Dodaj zegarek", command=self.app.add_watches)
        button.pack()

    def remove_watch_button(self):
        button = tk.Button(self.root, text="Usuń zegarek", command=self.remove_watch)
        button.pack()

    def modify_watch_button(self):
        button = tk.Button(self.root, text="Modyfikuj zegarki", command=self.modify_watch)
        button.pack()

    def survey_button(self):
        button = tk.Button(self.root, text="Ankieta", command=self.app.end_of_day_survey)
        button.pack()

    def update_buttons(self):
        current_day = datetime.today().weekday()  # 0 is Monday, 6 is Sunday
        choosen_files = os.listdir(self.app.choosen_dir)
        choosen_files.sort(key=lambda x: datetime.strptime(x.split('-')[1].replace('.txt', ''), '%Y%m%d%H%M%S'))
        last_choosen_file = choosen_files[-1] if choosen_files else None
        last_choosen_date = datetime.strptime(last_choosen_file.split('-')[1].replace('.txt', ''), '%Y%m%d%H%M%S') if last_choosen_file else None
        if last_choosen_date and last_choosen_date.isocalendar()[1] == datetime.now().isocalendar()[1]:
            # If there is a choosen file for this week
            if current_day == 6:  # If today is Sunday
                self.select_watches_for_week_button['state'] = 'normal'
            else:
                self.select_watches_for_week_button['state'] = 'disabled'
        else:
            # If there is no choosen file for this week
            self.select_watches_for_week_button['state'] = 'normal'

        self.root.after(1000, self.update_buttons)  # Check again in 1 second

    def remove_watch(self):
        self.select_watch()
        if self.selected_watch and messagebox.askyesno("Usuń zegarek", f"Czy na pewno chcesz usunąć zegarek o nazwie {self.selected_watch}?"):
            self.app.remove_watch(self.selected_watch)

    def modify_watch(self):
        self.select_watch()
        if self.selected_watch:
            modify_dialog = tk.Toplevel(self.root)
            modify_dialog.title("Modyfikuj zegarek")
            label = tk.Label(modify_dialog, text="Wybierz, co chcesz zmodyfikować:")
            label.pack()
            name_button = tk.Button(modify_dialog, text="Zmień nazwę", command=lambda: self.modify_watch_name(self.selected_watch))
            name_button.pack()
            image_button = tk.Button(modify_dialog, text="Zmień obrazek", command=lambda: self.modify_watch_image(self.selected_watch))
            image_button.pack()

    def modify_watch_name(self, watch_name):
        new_name = simpledialog.askstring("Modyfikuj zegarek", "Podaj nową nazwę zegarka:")
        self.app.modify_watch(watch_name, new_name=new_name)

    def modify_watch_image(self, watch_name):
        new_image_path = filedialog.askopenfilename(initialdir=self.app.watch_dir)
        self.app.modify_watch(watch_name, new_image_path=new_image_path)

    def select_watch(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Wybierz zegarek")
        label = tk.Label(dialog, text="Wybierz zegarek do modyfikacji:")
        label.pack()
        watch_names = [watch['name'] for watch in self.app.watches]
        combobox = ttk.Combobox(dialog, values=watch_names)
        combobox.pack()
        button = tk.Button(dialog, text="OK", command=lambda: self.set_selected_watch(combobox.get(), dialog))
        button.pack()
        dialog.wait_window()

    def set_selected_watch(self, watch_name, dialog):
        self.selected_watch = watch_name
        dialog.destroy()

    def survey(self):
        survey_dialog = tk.Toplevel(self.root)
        survey_dialog.title("Ankieta")
        survey_questions = [
            "Jak oceniasz komfort noszenia zegarka?",
            "Czy zegarek spełnia Twoje oczekiwania?",
            "Czy poleciłbyś ten zegarek innym?",
            "Jak oceniasz wygląd zegarka?",
            "Czy zegarek jest wygodny w użyciu?"
        ]
        survey_answers = []
        for question in survey_questions:
            label = tk.Label(survey_dialog, text=question)
            label.pack()
            answer_entry = tk.Entry(survey_dialog)
            answer_entry.pack()
            survey_answers.append(answer_entry)
        button = tk.Button(survey_dialog, text="Zakończ ankietę", command=lambda: self.finish_survey(survey_answers, survey_dialog))
        button.pack()

    def finish_survey(self, survey_answers, dialog):
        survey_questions = [
            "Jak oceniasz komfort noszenia zegarka?",
            "Czy zegarek spełnia Twoje oczekiwania?",
            "Czy poleciłbyś ten zegarek innym?",
            "Jak oceniasz wygląd zegarka?",
            "Czy zegarek jest wygodny w użyciu?"
        ]
        answers = [entry.get() for entry in survey_answers]
        form_file = os.path.join(self.app.form_dir, f"form-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt")
        with open(form_file, 'w') as f:
            for question, answer in zip(survey_questions, answers):
                f.write(f"{question}\n{answer}\n")
        dialog.destroy()

    def select_watches_for_week(self):
        self.app.select_watches_for_week()

    def show_today_watch_button(self):
        button = tk.Button(self.root, text="Pokaż zegarek na dziś", command=self.show_today_watch)
        button.pack()

    def show_today_watch(self):
        days_of_week = {
            'Monday': 'Poniedziałek',
            'Tuesday': 'Wtorek',
            'Wednesday': 'Środa',
            'Thursday': 'Czwartek',
            'Friday': 'Piątek',
            'Saturday': 'Sobota',
            'Sunday': 'Niedziela'
        }
        today = days_of_week[datetime.today().strftime('%A')]
        watch = self.app.week_watches.get(today)
        if watch:
            watch_image = Image.open(watch['image_path'])

            # Skalowanie obrazka
            base_height = 500  # Wysokość obrazka do skalowania
            hpercent = base_height / float(watch_image.size[1])
            wsize = int(float(watch_image.size[0]) * float(hpercent))
            watch_image = watch_image.resize((wsize, base_height), Image.LANCZOS)

            watch_photo = ImageTk.PhotoImage(watch_image)

            # Tworzenie nowego okna dialogowego dla obrazka
            watch_dialog = tk.Toplevel(self.root)
            watch_dialog.title(f"{today}: {watch['name']}")
            label = tk.Label(watch_dialog, image=watch_photo)
            label.image = watch_photo  # keep a reference to the image
            label.pack()
        else:
            messagebox.showinfo("Zegarek na dziś", "Nie wybrano zegarka na dziś.")

    def show_week_watches_button(self):
        button = tk.Button(self.root, text="Pokaż zegarki na ten tydzień", command=self.show_week_watches)
        button.pack()

    def show_week_watches(self):
        watches_message = ""
        for day, watch in self.app.week_watches.items():
            watches_message += f"{day}: {watch['name']}\nŚcieżka do obrazka: {watch['image_path']}\n\n"
        messagebox.showinfo("Zegarki na ten tydzień", watches_message)

    def add_exit_button(self):
        button = tk.Button(self.root, text="Wyjdź", command=self.exit_app)
        button.pack()

    def exit_app(self):
        if messagebox.askyesno("Wyjdź", "Czy na pewno chcesz wyjść?"):
            self.root.destroy()




app = WatchApp()
gui = WatchAppGUI(app)
#gui.add_watch_button()
#gui.remove_watch_button()
#gui.modify_watch_button()
#gui.survey_button()
#gui.add_exit_button()
gui.run()
