import os
import json
import shutil
from datetime import datetime
import random
from tkinter import filedialog, messagebox, simpledialog


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
        # Filtruj pliki, które mają poprawny format: 'choosen_watches-YYYYMMDDHHMMSS.txt'
        filtered_files = [f for f in choosen_files if '-' in f and f.endswith('.txt') and len(f.split('-')) > 1]
        # Sortuj pliki po dacie
        filtered_files.sort(key=lambda x: datetime.strptime(x.split('-')[1].replace('.txt', ''), '%Y%m%d%H%M%S'))

        last_choosen_file = filtered_files[-1] if filtered_files else None
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