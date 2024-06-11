import psychopy
from psychopy import visual, core, event, gui, sound
import pandas as pd
import csv

df_train = pd.read_csv("treningowestimuli.csv", sep=";")
df_exp = pd.read_csv("eksperymentalnestimuli.csv", sep=";")
#zbieranie info wstępych, jesli nie to sie wszystko wyłącza
info = {"ID": "", "Wiek": "", "Płeć": ["Kobieta", "Mężczyzna", "Inna"]}
dialog = gui.DlgFromDict(dictionary=info, title="Dane osoby badanej")
if not dialog.OK:
    core.quit()

#tworzy sie csv w ktorym zapisujemy pliki
output_file = f"participant_{info['ID']}.csv"
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Trial", "Slowo1", "Slowo2", "Relacja", "CzasOdpowiedzi", "Poprawność", "Part", "Wiek", "Płeć", "Feedback"])

#piękna funckja pokazuja tekst taki jaki chcemy
def display_text(win, main_text, bottom_text=None):
    instruction_text = visual.TextStim(win, text=main_text, color="black", wrapWidth=1.2, pos=(0, 0.2))
    instruction_text.draw()
    if bottom_text:
        bottom_text_stim = visual.TextStim(win, text=bottom_text, color="black", pos=(0, -0.8))
        bottom_text_stim.draw()
    win.flip()
    event.waitKeys(keyList=["space"])

#funckaja na cala procedure 
def procedura(df, num_trials, training=False, music=None, part=None):
    df = df.sample(n=num_trials).reset_index(drop=True)#zapewnia nam losowosc, df sie wymienia w zaleznosci od tego czego potrzeba
    pop_odp_count = 0 #pozniej w treningowej sprawdzamy, czy poprawnosc aby na pewno nie jest za mala
    if music:#selfexplanatory
        music.play()

    for trial_num, row in df.iterrows():#chodzi o to, ze jak sie wymieszaja juz wiersze to rzeby szlo po kolei po wymiesznaych
        if trial_num == num_trials:
            break

        fix = visual.TextStim(win, text='+', color=(-1, -1, -1))#piekny sliczny i cudowny punkt fiksacji
        fix.draw()
        win.flip()
        core.wait(0.8)

        para = f"{row['Slowo1']} \n {row['Slowo2']}"# robimy pare słow 
        word_stim = visual.TextStim(win, text=para, color=(-1, -1, -1), pos=(0.0, 0.0))
        word_stim.draw()
        win.flip()

        timer = core.Clock()  #włącza się zegar
        response = event.waitKeys(maxWait=3, keyList=['m', 'z'], timeStamped=timer)

        if response:# czy byla odpowiedz czy nie, wiadomo
            key, rt = response[0]
        else:
            key, rt = None, None

        relacja_text = row['Relacja'] #tutaj zasytanawiamy sie nad relacja,a wlasciwie to sie nikt nie zastanawia tylko grzecznie pytamy plik csv o relacje
        correct = (key == 'm' and row['Relacja'] in ['Powiązane', 'Niepowiązane']) or (key == 'z' and row['Relacja'] == 'Nie-słowo')
        
        if key is None:#czy jest poprawnosc klawisza nacisnietego z tym jak ma byc
            correct = -1
        else:
            correct = 1 if correct else 0
            
        if correct == 1:
            pop_odp_count += 1


        feedback = ""#to się wlacza tylko na treningowej i dajemy znac czy jest git czy nie
        if training:
            if key:
                if correct:
                    feedback = "poprawnie"
                else:
                    feedback = "odpowiedź niepoprawna"
            else:
                feedback = "odpowiedź niepoprawna lub udzielona za wolno"

            feedback_stim = visual.TextStim(win, text=feedback, color=(-1, -1, -1))
            feedback_stim.draw()
            win.flip()
            core.wait(2)
            win.flip()
            core.wait(0.8)

        #zapisywanie do pliku wyjsciowego
        with open(output_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([trial_num, row['Slowo1'], row['Slowo2'], relacja_text, rt, correct, part if not training else "tren", info['Wiek'], info['Płeć'], feedback if training else ""])

        win.flip()
        core.wait(0.8)

    if music:
        music.stop() #wiadomo sie musi skonczyc
        
    if training and pop_odp_count < num_trials // 2:##czy w treningowej ktos sie za duzo nie pomylil?sprawdzaam
        dodatkowa_instrukcja = (
            "Wydaje się, że miałeś/aś problem z instrukcją. "
            "Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. "
            "Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”."
            "\n\nNaciśnij spację, aby ponownie przeczytać instrukcje."
        )
        display_text(win, dodatkowa_instrukcja)
        for instrukcja in instrukcje:
            display_text(win, instrukcja, bottom_text)


# jakie sq poczatkowe instrukcje
instrukcje = [
    "W tym zadaniu, które zaraz zobaczysz na ekranie pojawią się jednocześnie dwa słowa. Twoim zadaniem jest ocenić, czy słowa są słowami prawdziwymi czy bezsensownymi. Jeśli oba słowa są prawdziwymi polskimi słowami, naciśnij na klawiaturze „m”. Jeśli jeden lub oba słowa są słowami bezsensownymi, naciśnij na klawiaturze „z”.",
    "Przykłady poprawnych zestawów słów (takich, przy których należy kliknąć „m”): WIOSNA - WIATR. Przykłady niepoprawnych zestawów słów (takich, przy których należy kliknąć „z”): WIOSNA - UZYLE lub AGWITK - HATOPS. W niektórych częściach badania będziesz słuchał/a muzyki. Prosimy o nie zmienianie jej głośności - to część eksperymentu.",
    "Przed rozpoczęciem sesji eksperymentalnej, będziesz poddany krótkiej sesji treningowej, która pomoże Ci zrozumieć zadanie. W trakcie tej sesji treningowej otrzymasz informację po każdej udzielonej odpowiedzi, czy była poprawna. Postaraj się odpowiadać poprawnie i szybko, ponieważ czas Twojej reakcji będzie mierzony."
]
bottom_text = "[Naciśnij spację, aby przejść dalej]"

#otwieramy okno, zlamana biel
win = visual.Window([1280, 720], color="#F5F5F5", monitor="testMonitor", units="norm", fullscr=True)
win.refreshThreshold = 1 / 60.0  # Set FPS to 60

#dzień dobry psychopy, to jest nasza muzyka
muz_bez_slow = sound.Sound("bezslow.wav")
muz_slowa = sound.Sound("zeslowamip.wav")
###################
###################
###################
###################
#pokazujemy instrukcje, mini funckja
for instrukcja in instrukcje:
    display_text(win, instrukcja, bottom_text)


#sesja treningowa 
procedura(df_train, 15, training=True)

#eksperymentalna
display_text(win, "Zaraz rozpocznie się sesja eksperymentalna. Pamiętaj, oceniasz czy zestawy słów są prawdziwe i dla takich klikasz klawisz „m” a dla bezsensowych klikasz klawisz „z”. Odpowiadaj poprawnie i staraj się robić to jak najszybciej.", "Naciśnij spację, aby rozpocząć.")

#czesci eksperymentalnej
display_text(win, "Sesja eksperymentalna - Część 1", "Naciśnij spację, aby rozpocząć")
procedura(df_exp, 90, music=muz_bez_slow, part=1)
display_text(win, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

display_text(win, "Sesja eksperymentalna - Część 2", "Naciśnij spację, aby rozpocząć")
procedura(df_exp, 90, part=2)
display_text(win, "Ta część dobiegła końca, to chwila na moment odpoczynku.\nGdy będziesz gotowy/a kliknij spację, by kontynuować")

display_text(win, "Sesja eksperymentalna - Część 3", "Naciśnij spację, aby rozpocząć")
procedura(df_exp, 90, music=muz_slowa, part=3)
display_text(win, "To koniec eksperymentu. Bardzo dziękujemy za wzięcie udziału w naszym badaniu!", "[Naciśnij spację, by wyjść z procedury eksperymentalnej]")

# Close window
win.close()
core.quit()
