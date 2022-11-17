#!/bin/python

# TODO setup branch with README (docent?)
# TODO PySimpleGUI?
#  - Screenshots
#  - Text update
#  - Appropriate memes
# TODO Part 2
#  - Shared repo
#  - Iedereen een branch
#  - Git lead begint als spelleider
#  - Iedereen maakt eigen branch, edit 'vragen.txt', push naar eigen branch
#  - Spelleider haalt alle branches op, merget naar main en zet antwoorden erij
#  - 20 questions
#  - README.md
# TODO Test op Windows / PyCharm - Git lib aanwezig?

from git import Repo
from sys import argv

def get_state():
    try:
        with open(".state", "r") as file:
            state = file.read()
            print("DEBUG", "get_state", state)
            if state.isnumeric():
                return int(state)
            else:
                put_state(0)
                return 0
    except Exception:
        put_state(0)
        return 0

def put_state(i):
    with open(".state", "w+") as file:
        file.write(str(i))

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

        return content.strip() == should_be.strip()
    return inner

def rewind():
    travel("step_back")

exercises = { 0: { "text": ["Welkom! In deze tutorial gaan we leren hoe we Git kunnen gebruiken om met meerdere mensen samen te werken."],
                   "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                   "post": rewind
                 },
             1: { "text": ["Het eerste dat we ons aan willen leren, is om regelmatig werk van GitHub naar je eigen systeem te synchroniseren. Laten we dit meteen doen, misschien heeft iemand inmiddels iets veranderd. Gebruik hiervoor het commando `git fetch`."],
                  "done": check_heads(main="Internationalisatie", remote="Test code"),
                 },
             2: { "text": ["Zo te zien heeft iemand anders (of misschien wel jijzelf, vanuit de browser of een andere computer) een commit gemaakt die nieuwer is dan de huidige versie. Gebruik `git merge origin/main --ff-only` om de veranderingen te integreren."],
                  "done": check_heads(main="Test code", remote="Test code"),
                 },
             3: { "text": ["Goed gedaan! Dit ging gelukkig vrij pijnloos, omdat we de nieuwe code hebben binnengehaald voordat we zelf zijn begonnen. Als we dat niet hadden gedaan, dan hadden we misschien twee verschillende versies gehad die we hadden moeten samenvoegen.","We gaan even een stap terug in de tijd - voordat we de `git fetch` deden."],
                  "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                  "post": rewind
                 },
             4: { "text": ["Nu maken we eerst een eigen aanpassing, zonder eerst de remote changes binnen te halen. We maken een nieuw bestand, `nieuw.py`, met de volgende inhoud:"],
                  "done": check_file("nieuw.py", nieuw),
                 },
             5: { "text": ["Tof! Laten we deze aanpassing committen (`git add nieuw.py`, `git commit -m \"Message\"`). Als we nu `git push` proberen gaat het mis...","Als we `git fetch` doen zien we dat we twee parallelle lijnen hebben gemaakt. Oeps. Geeft niet, kan gebeuren. Dus, hoe verder?","Helaas, `git merge --ff-only` doet het niet. Dit keer kunnen we niet gewoon doorspoelen, maar zullen we de veranderingen moeten samenvoegen. Dit kan met `git merge`."],
                  "done": check_heads(main="Merge remote-tracking branch"),
                 },
             6: { "text": ["In dit geval kan git de twee verschillende commits veilig samenvoegen, omdat we in losse bestanden hebben gewerkt. We gaan nog een keertje back in time, en dit keer maken er echt een fubar van..."],
                  "done": check_heads(main="Internationalisatie", remote="Internationalisatie"),
                  "post": nieuw_branch
                 },
             7: { "text": ["We maken wederom wat aanpassingen, maar nu dwars door het bestand `project.py` heen. Open het bestand, en pas het als volgt aan:"],
                  "done": check_file("project.py", aangepast),
                 },
             8: { "text": ["Cool. Laten we kijken wat er nu gebeurt. We doen een `git add project.py` gevolgd door `git commit -m \"Message\"`. Je kan proberen te pushen, maar ook nu weer krijgen we de opdracht om eerst de remote changes te mergen. Sure. `git fetch`, geen verrassingen, maar dan... `git merge`, kan het niet meer voor ons oplossen. We moeten een handmatige merge doen, waarbij we (in PyCharm) de beide versies aan twee kanten hebben met een compromis die we in het midden moeten samenstellen. Als dat gelukt is kunnen we de gemergde file opnieuwe met `git add` toevoegen, een merge commit maken, en dan pas mogen we pushen."],
                  "done": check_heads(main="Merge remote-tracking branch"),
                  "post": manual_merge_branch
                 },
             9: { "text": ["Dat is ook gelukt. Je kunt nu veilig pushen als je wilt. De laatste individuele oefening gaan we nog een merge uitvoeren, die als het goed is weer automatisch kan. Wat er wel nieuw aan is, is dat we nu een tweede branch hebben in plaats van nieuwe aanpassingen op GitHub. Remember the timeline waarin we `nieuw.py` hebben gemaakt en gemerged? Die is niet echt kwijt, maar opgeslagen als een aparte branch genaamd `nieuw`. Branches zijn splitsingen die met opzet gemaakt zijn, om verschillende aanpassingen los van elkaar uit te kunnen voeren. Meestal wordt dit gebruikt voor verschillende features waar mensen parallel aan werken. Deze bestaan langere tijd naast elkaar en worden, en kunnen gemerged worden zodra de feature 'af' is. Soms worden hier nog tussenstappen gebruikt, en heb je bijvoorbeeld branches voor features in ontwikkeling, een branch waarin de code samengevoegd en getest wordt, en een branch waar allen goed geteste code op komt te staan. Nu houden we het simpel, en hebben we twee 'features' waarvan er een al op de main staat. De `check_antwoord`-feature is al op main geintegreerd, maar de eerder gemaakte tweede module (`nieuw.py`) mist nog.","Je kan op dit punt `git checkout` gebruiken om van branch te wisselen, bijvoorbeeld met `git checkout nieuw` om de code op deze branch te bekijken. Probeer dat en ga daarna met `git checkout main` weer terug naar de main-branch. Doe nu `git merge feature` om de beide tijdlijnen weer samen te voegen, en push het resultaat naar GitHub. Dit samenvoegen (en het beheren van de Git en de kwaliteit van de code daarop) kan in veel teams een speciale rol zijn."],
                  "done": check_heads(main="Merge branch 'nieuw'"),
                 },
             10: { "text": ["Je bent klaar met het individuele deel van deze tutorial. Wacht op de rest van je groepje, of kijk of kan helpen als iemand moeite heeft. Nog een paar tips:","- We hebben nu steeds `git fetch` en `git merge` in twee stappen gedaan. Dit is (zeker om het te leren) fijn, zodat je alle stappen kan zien en niet door de merge verrast wordt. In de praktijk worden deze stappen zo vaak na elkaar gebruikt, dat dit ook in 1 keer kan met een `git pull`.","- Je kan `git checkout` niet alleen voor branches gebruiken, maar voor iedere commit. Dit kan handig zijn om even terug te gaan naar een oude versie","- Je kan zelf branches aanmaken met `git branch NAAM` of `git checkout -b NAAM` - die laatste zorgt dat je ook meteen op de nieuwe branch verder gaat. Met `git branch` kan je alle branches bekijken. Voor deze repo is er nog een `setup` branch, met instructies voor docenten die dit met hun klas willen doen, en `demo_code` die alleen geschiedenis van `project.py` bevat zonder deze tutorial.","- In plaats van wachten op je groepsgenoten kun je ook de Oh-My-Git game downloaden (https://blinry.itch.io/oh-my-git) om te oefenen of nieuwe dingen te leren. Je hoort het goed, docent zegt 'ga maar gamen'. It's a trap?"],
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
                print(line)
            if "post" in exercises[n]:
                exercises[n]["post"]()

if __name__ == "__main__":
    exercise(get_state())
