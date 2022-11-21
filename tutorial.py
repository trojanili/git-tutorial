#!/bin/python

from sys import argv

try:
    from git import Repo
    import PySimpleGUI as sg
except ImportError:
    print("Je mist libraries! Zorg dat je GitPython en PySimpleGui installeert (via PyCharm of `pip`")

try:
    with Repo(".") as repo:
        main = repo.heads.main
except Exception:
    print("De library kan je Git executable niet vinden. Pas de run configuration in PyCharm aan, zodat de environment-variabele `GIT_PYTHON_GIT_EXECUTABLE` naar `git.exe` verwijst. Waarschijnlijk bevindt dit programma zich op `\\Program Files\\Git\\bin\\git.exe`.")

sg.theme('DarkGrey13')

class Image:
    def __init__(self, *filename):
        self.path = filename

    def print(self):
        print("\n(IMAGE)\n")

    def show(self):
        return [sg.Image("images/" + p) for p in self.path]

class Heading(str):
    def print(self):
        print("#", self)

    def show(self):
        return [sg.Text(self, font=("Any 16 bold"))]

class Text(str):
    def print(self):
        print(self)

    def show(self):
        return [sg.Text(self, font=("Any 12"))]

class Sidenote(str):
    def print(self):
        print(self)

    def show(self):
        return [sg.Text(self, font=("Any 9 italic"))]

class Code(str):
    def print(self):
        print(self)

    def show(self):
        return [[sg.Text(self, font=("Courier 12"))],
                [Sidenote("De code is ook in de output te vinden, om makkelijker te copy-pasten.").show()]]


def get_state():
    try:
        with open(".state", "r") as file:
            state = file.read()
            if state.strip().isnumeric():
                return int(state.strip())
            else:
                put_state(0)
                return 0
    except Exception:
        put_state(0)
        return 0

def put_state(i):
    with open(".state", "w+") as file:
        file.write(str(i))

def next():
    n = get_state()
    put_state(n+1)
    exercise(n+1)

def travel(commit):
    with Repo(".") as repo:
        main = repo.heads.main
        main.commit = commit
        repo.head.reference = main
        repo.head.reset(index=True, working_tree=True)
    with open(".git/refs/heads/main", "r") as infile:
        with open(".git/refs/remotes/origin/main", "w") as outfile:
            outfile.write(infile.read())

def keep(bname):
    with Repo(".") as repo:
        if bname in repo.refs:
            repo.git.branch('-D', bname)
        repo.create_head(bname)

nieuw = """
def main():
    print("Dit is de tweede module")
"""

aangepast = """
def check_antwoord(antwoord):
    return antwoord == 42

def hello_world(lang):
    if lang == "NL":
        print("Hallo wereld!")
    elif lang == "FR":
        print("Bonjour le monde!")
    else:
        print("Hello world!")

hello_world("EN")

antwoord = input("Wat is het antwoord op de ultieme vraag van het leven, het universum, en alles?")
if check_antwoord(antwoord):
    print("Correct!")
else:
    print("Mogelijk heb je een andere vraag in je hoofd?")
"""

def manual_merge_branch():
    keep("manual_merge")

def nieuw_branch():
    keep("nieuw")
    travel("step_back")

def check_heads(main=None, remote=None):
    def inner():
        with Repo(".") as repo:
            mainref = repo.heads.main
            remoteref = mainref.tracking_branch()
            result = True
            if main:
                result &= mainref.commit.message.startswith(main)
            if remote:
                result &= remoteref.commit.message.startswith(remote)
            return result
    return inner

def check_file(filename, should_be):
    def inner():
        try:
            with open(filename, "r") as file:
                content = file.read()
        except Exception:
            content = ""

        with Repo(".") as repo:
            return content.strip() == should_be.strip() and not repo.is_dirty(path=filename)
    return inner

def rewind():
    travel("step_back")

exercises = { 0: { "text": [
                  Text("Welkom! In deze tutorial gaan we leren hoe we Git kunnen gebruiken om met meerdere mensen samen te werken."),
                  Text("Voordat we beginnen, een paar tips:"),
                  Text("- Je moet na iedere stap het script `tutorial.py` opnieuw uitvoeren."),
                  Text("  - Als alles goed is gegaan krijg je een nieuwe instructie, zo niet blijft de oude terugkomen."),
                  Text("- Lees goed wat er staat, en vraag om hulp als je er niet uitkomt."),
                  Text("- Het doel is uiteindelijk om hier comfortabel mee te worden, dus experimenteren is ok. In het ergste geval resetten we gewoon.")
                  ],
                   "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                   "post": rewind
                 },
             1: { "text": [
                 Heading("Fetch"),
                 Text("Het eerste dat we ons aan willen leren, is om regelmatig werk van GitHub naar je eigen systeem te synchroniseren."),
                 Text("Laten we dit meteen doen, misschien heeft iemand inmiddels iets veranderd. Gebruik hiervoor het Git > Fetch menu in PyCharm of het commando `git fetch`."),
                 Image("1_Fetch.png"),
                 ],
                  "done": check_heads(main="Internationalisatie", remote="Test code"),
                 },
             2: { "text": [
                 Heading("Fast Forward"),
                 Text("Zo te zien heeft iemand anders (of misschien wel jijzelf, vanuit de browser of een andere computer) een commit gemaakt die nieuwer is dan de huidige versie."),
                 Image("2_FFBefore.png"),
                 Text("Klik rechts op de binnengehaalde commit in PyCharm, en Merge de commit in je main branch."),
                 Text("Alternatief in de command line: gebruik `git merge origin/main --ff-only` om de veranderingen te integreren."),
                 Image("2_FastForward.png")
                 ],
                  "done": check_heads(main="Test code", remote="Test code"),
                 },
             3: { "text": [
                 Text("Goed gedaan! Dit ging gelukkig vrij pijnloos, omdat we de nieuwe code hebben binnengehaald voordat we zelf zijn begonnen."),
                 Image("3_FFAfter.png"),
                 Text("Als we dat niet hadden gedaan, dan hadden we misschien twee verschillende versies gehad die we hadden moeten samenvoegen."),
                 Text("We gaan even een stap terug in de tijd - voordat we de Fetch deden.")
                 ],
                  "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                  "post": rewind
                 },
             4: { "text": [
                 Heading("Automerge"),
                 Text("Nu maken we eerst een eigen aanpassing, zonder eerst de remote changes binnen te halen."),
                 Text("We maken een nieuw bestand, `nieuw.py`, met de volgende inhoud:"),
                 Code(nieuw),
                 Text("Add en commit dit bestand:"),
                 Image("4_CommitWindow.png"),
                 Text("(Command Line: `git add nieuw.py`, `git commit -m \"Message\"`).")
                 ],
                  "done": check_file("nieuw.py", nieuw),
                 },
             5: { "text": [
                 Text("Tof! We hebben onze nieuwe code veiliggesteld, nu nog naar GitHub doorzetten. Maar dan... Als we nu proberen te Pushen gaat het mis :-/"),
                 Image("5_BasicMergeError.png", "5_Split.png"),
                 Text("Als we een Fetch doen zien we dat we twee parallelle lijnen hebben gemaakt. Oeps. Geeft niet, kan gebeuren. Dus, hoe verder?"),
                 Text("Helaas, de fast forward doet het niet. Dit keer kunnen we niet gewoon doorspoelen, maar zullen we de veranderingen moeten samenvoegen."),
                 Text("Dit kan met het Merge menu item, of het commando `git merge origin/main`."),
                 Image("5_Merge.png", "5_MergeWhat.png"),
                 Sidenote("Bij het mergen wordt een nieuwe commit gemaakt. Je krijgt de mogelijkheid om hier een message voor te schrijven, maar in dit geval moeten we gewoon de standaard-tekst aanhouden.")
                 ],
                  "done": check_heads(main="Merge remote-tracking branch"),
                 },
             6: { "text": [
                 Text("In dit geval kan git de twee verschillende commits veilig samenvoegen, omdat we in losse bestanden hebben gewerkt."),
                 Text("We gaan nog een keertje back in time, en dit keer maken er echt een fubar van..."),
                 Image("6_conflict.png"),
                 Text("Het resultaat van de vorige stap is niet helemaal verwijderd, maar staat nog in je timeline onder het label `nieuw`. Negeer deze aftakking voor nu even."),
                 ],
                  "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                  "post": nieuw_branch
                 },
             7: { "text": [
                 Heading("Manual Merging"),
                 Text("We maken wederom wat aanpassingen, maar nu dwars door het bestand `project.py` heen. Open het bestand, en pas het als volgt aan:"),
                 Code(aangepast),
                 Text("Wederom doen we een add en commit voordat we verder kunnen. ")
                 ],
                  "done": check_file("project.py", aangepast),
                 },
             8: { "text": [
                 Text("Na de commit heb je de nieuwe commit (`main`) en Internationalisatie (`origin/main`), de `nieuw` branch is voor later."),
                 Text("Na de fetch staat `origin/main` op Test Code, de andere twee commits staan nog steeds in time-out."),
                 Image("8_Status.png"),
                 Text("Cool. Laten we kijken wat er nu gebeurt. Je kan proberen te pushen, maar ook nu weer krijgen we de opdracht om eerst de remote changes te mergen. Sure."),
                 Text("Fetch, geen verrassingen, maar dan... De automatische merge kan het niet meer voor ons oplossen. We moeten een handmatige merge doen."),
                 Text("Kies in het linkerscherm hieronder voor Merge, niet voor voor Accept Ours of Theirs."),
                 Text("We krijgen nu in PyCharm de beide versies aan twee kanten met een compromis die we in het midden moeten samenstellen."),
                 Image("8_Conflict1.png", "8_Conflict2.png"),
                 Text("Als dat gelukt is kunnen we de gemergde file opnieuwe met `git add` toevoegen, een merge commit maken (gebruik wederom de standaard naam voor nu), en dan pas mogen we pushen.")
                 ],
                  "done": check_heads(main="Merge remote-tracking branch"),
                  "post": manual_merge_branch
                 },
             9: { "text": [
                 Text("Dat is ook gelukt. Je kunt nu veilig pushen als je wilt. De laatste individuele oefening gaan we nog een merge uitvoeren, die als het goed is weer automatisch kan."),
                 Text("Wat er wel nieuw aan is, is dat we nu een tweede branch hebben in plaats van nieuwe aanpassingen op GitHub."),
                 Text("Remember the timeline waarin we `nieuw.py` hebben gemaakt en gemerged? Die is niet echt kwijt, maar stiekem opgeslagen als een aparte branch genaamd `nieuw`.")
                 ],
                  "post": next,
                 },
             10: { "text": [
                 Heading("Branches"),
                 Text("Branches zijn splitsingen die met opzet gemaakt zijn, om verschillende aanpassingen los van elkaar uit te kunnen voeren."),
                 Text("Meestal wordt dit gebruikt voor verschillende features waar mensen parallel aan werken."),
                 Text("Deze bestaan langere tijd naast elkaar en worden, en kunnen gemerged worden zodra de feature 'af' is."),
                 Image("9_goose.png"),
                 Sidenote("Soms worden nog extra branches als tussenstappen gebruikt. Een gangbare werkvorm is:"),
                 Sidenote("- Een branch per feature of bugfix die in ontwikkeling is,"),
                 Sidenote("- Een development branch waarin de code samengevoegd en getest wordt en"),
                 Sidenote("- De main branch mag dan alleen goed geteste code en geintegreerde code op komt te staan."),
                 Text("Jullie kunnen zelf als projectgroep kiezen hoe ver je hier in gaat. We adviseren om in ieder geval iedereen een eigen branch te geven.")
                 ],
                  "post": next,
                 },
             11: { "text": [
                 Text("Nu houden we het simpel, en hebben we twee 'features' waarvan er een al op de main staat."),
                 Text("De `check_antwoord`-feature is al op main geintegreerd, maar de eerder gemaakte tweede module (`nieuw.py`) mist nog."),
                 Text("Je kan op dit punt `git checkout` gebruiken om van branch te wisselen, bijvoorbeeld met `git checkout nieuw` om de code op deze branch te bekijken."),
                 Text("Probeer dat en ga daarna met `git checkout main` weer terug naar de main-branch."),
                 Text("Doe nu `git merge nieuw` om de beide tijdlijnen weer samen te voegen, en push het resultaat naar GitHub."),
                 Text("Dit samenvoegen (en het beheren van de Git en de kwaliteit van de code daarop) kan in veel teams een speciale rol zijn.")
                 ],
                  "done": check_heads(main="Merge branch 'nieuw'"),
                 },
             12: { "text": [
                 Heading("A winner is you!"),
                 Text("Je bent klaar met het individuele deel van deze tutorial. Wacht op de rest van je groepje, of kijk of kan helpen als iemand moeite heeft. Nog een paar tips:"),
                 Text("- We hebben nu steeds `git fetch` en `git merge` in twee stappen gedaan. Dit is (zeker om het te leren) fijn, zodat je alle stappen kan zien en niet door de merge verrast wordt."),
                 Text("  In de praktijk worden deze stappen zo vaak na elkaar gebruikt, dat dit ook in 1 keer kan met een `git pull`."),
                 Text("- Je kan `git checkout` niet alleen voor branches gebruiken, maar voor iedere commit. Dit kan handig zijn om even terug te gaan naar een oude versie"),
                 Text("- Je kan zelf branches aanmaken met `git branch NAAM` of `git checkout -b NAAM` - die laatste zorgt dat je ook meteen op de nieuwe branch verder gaat. Met `git branch` kan je alle branches bekijken."),
                 Text("   Voor deze repo is er nog een `setup` branch, met instructies voor docenten die dit met hun klas willen doen, en `demo_code` die alleen geschiedenis van `project.py` bevat zonder deze tutorial."),
                 Text("- In plaats van wachten op je groepsgenoten kun je ook de Oh-My-Git game downloaden (https://blinry.itch.io/oh-my-git) om te oefenen of nieuwe dingen te leren."),
                 Text("   Je hoort het goed, docent zegt 'ga maar gamen'."),
                 Image("12_omg.png", "12_trap.png"),
                 Text(""),
                 Text("- Zodra je team klaar is: maak een fork van https://github.com/hu-ict-projb/git-20-questions, neem de README en historie door, en speel met je team 20 Questions. "),
                 Text(""),
                 ],
                  "done": lambda: False, # No further steps
                 },
       }

def exercise(n):
    if n in exercises:
        if "done" in exercises[n] and exercises[n]["done"]():
            put_state(n+1)
            exercise(n+1)
        else:
            for line in exercises[n]["text"]:
                line.print()

            layout = [t.show() for t in exercises[n]["text"]]
            layout += [[sg.Button("Klaar?")]]

            window = sg.Window('PySimpleGUI', layout)

            event = 0
            while event != sg.WIN_CLOSED and event != "Klaar?":  # Event Loop
                event, values = window.read()

            if "post" in exercises[n]:
                exercises[n]["post"]()

def debug(n, stop=12):
    for line in exercises[n]["text"]:
        line.print()

    print()

    layout = [t.show() for t in exercises[n]["text"]]
    layout += [[sg.Button("Klaar?")]]

    window = sg.Window('PySimpleGUI', layout)

    event = 0
    while event != sg.WIN_CLOSED and event != "Klaar?":  # Event Loop
        event, values = window.read()

    if n < stop:
        debug(n+1)


if __name__ == "__main__":
    if len(argv) > 2:
        debug(int(argv[1]), int(argv[2]))
    else:
        exercise(get_state())
