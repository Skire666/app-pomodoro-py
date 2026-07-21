
Dossier racine "app-pomodoro-py"
Fichier dans "app-pomodoro-py/src/pomodoro/main.py"

-------------------

0. Se mettre dans l'environnement (important)
.\venv\Scripts\activate

-------------------

1. Installer PyInstaller
pip install pyinstaller

-------------------

2. Se placer à la racine du projet
cd app-pomodoro-py

-------------------

3. Lancer la compilation

```
pyinstaller --noconfirm --onefile --windowed --name pomodoro --paths src src/pomodoro/main.py --icon "E:\app-pomodoro-py\ress\pomodoro.ico"
```

--paths src : indique à PyInstaller d'ajouter src au chemin de recherche des modules, pour qu'il retrouve bien le package pomodoro si main.py fait des imports du type from pomodoro.timer import Timer
--onefile : un seul .exe
--windowed : pas de console noire derrière ta fenêtre PySide
--name pomodoro : nom de l'exécutable généré

Résultat :
Dossier "build" + " dist"
L'exécutable sera généré dans app-pomodoro-py/dist/pomodoro.exe.

-------------------

Troubleshooting

Si PySide6 pose problème (fenêtre noire/vide, plugin manquant)
```
pyinstaller --noconfirm --onefile --windowed --name pomodoro --paths src --collect-all PySide6 src/pomodoro/main.py
```

Recommandé : passer par un .spec
C'est plus propre de générer un fichier .spec une fois, puis de le versionner :
```
pyi-makespec --onefile --windowed --name pomodoro --paths src src/pomodoro/main.py
```

Va créer un pomodoro.spec à la racine, éditable pour ajouter datas=[...], hiddenimports=[...], etc.
Ensuite tu recompiles simplement avec :

```
pyinstaller pomodoro.spec
```
