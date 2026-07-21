"""French user-facing strings (see AGENTS.md §6).

This module, together with `shared/errors/*_error.py`, is the only source
of French display strings in the project. Views, Presenters, and Services
import from here instead of hardcoding French text inline.
"""

# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

from typing import Final

# Top bar (spec §1)
TOP_BAR_SEARCH_PLACEHOLDER: Final[str] = "Rechercher un pomodoro..."
TOP_BAR_NEW_BUTTON: Final[str] = "+ Nouveau"

# Left navigation (spec §1)
NAV_POMODOROS: Final[str] = "Pomodoros"
NAV_HISTORY: Final[str] = "Historique"

# Pomodoro list (spec §2.1)
LIST_EMPTY_MESSAGE: Final[str] = "Aucun pomodoro pour l'instant"
LIST_EMPTY_CREATE_BUTTON: Final[str] = "+ Créer mon premier pomodoro"
LIST_SORT_NAME: Final[str] = "Nom"
LIST_SORT_DURATION: Final[str] = "Durée"
LIST_SORT_LAST_USED: Final[str] = "Dernière utilisation"
LIST_ACTION_START: Final[str] = "▶ Play"
LIST_ACTION_EDIT: Final[str] = "✎ Edit"
LIST_ACTION_DUPLICATE: Final[str] = "⧉ Copy"
LIST_ACTION_DELETE: Final[str] = "X Del."

# Pomodoro detail (spec §2.2)
DETAIL_TAB_GENERAL: Final[str] = "Général"
DETAIL_TAB_TODO_TEMPLATE: Final[str] = "TODO ({count})"

# Create/edit form (spec §2.3)
FORM_FIELD_NAME: Final[str] = "Nom du pomodoro"
FORM_FIELD_DURATION: Final[str] = "Durée"
FORM_FIELD_SOUND: Final[str] = "Son"
FORM_BUTTON_BROWSE: Final[str] = "Parcourir"
FORM_BUTTON_TEST_SOUND: Final[str] = "▶ Tester"
FORM_FIELD_VOLUME: Final[str] = "Volume"
FORM_FIELD_REPEAT: Final[str] = "Répétitions"
FORM_SAVED_INDICATOR: Final[str] = "✓ Enregistré"
FORM_NO_SOUND_HINT: Final[str] = "Aucun son — la fin du pomodoro sera silencieuse"
FORM_CLOSE_BUTTON: Final[str] = "Fermer"
FORM_DURATION_HOURS_SUFFIX: Final[str] = "h"
FORM_DURATION_MINUTES_SUFFIX: Final[str] = "m"
FORM_DURATION_SECONDS_SUFFIX: Final[str] = "s"
FORM_REPEAT_COUNT_SUFFIX: Final[str] = "fois, toutes les"
FORM_REPEAT_INTERVAL_SUFFIX: Final[str] = "s"
FORM_SOUND_FILE_FILTER: Final[str] = "Fichiers son (*.mp3 *.wav *.ogg)"

# Active session (spec §2.4)
SESSION_PAUSE_BUTTON: Final[str] = "⏸ Pause"
SESSION_RESET_BUTTON: Final[str] = "⟲ Reset"
SESSION_SWITCH_CONFIRM_TEMPLATE: Final[str] = (
    'Un pomodoro est en cours ("{name}"). L\'arrêter et démarrer celui-ci ?'
)
SESSION_COMPLETED_NOTIFICATION_TEMPLATE: Final[str] = "✅ Pomodoro terminé — {name}"
SESSION_COMPLETED_STATE_LABEL: Final[str] = "Terminé ✓"
SESSION_RESTART_BUTTON: Final[str] = "Relancer"
SESSION_BACK_TO_LIST_BUTTON: Final[str] = "Retour à la liste"
SESSION_TODO_IN_PROGRESS_TITLE: Final[str] = "TODO en cours"
SESSION_RESUME_PROMPT_TEMPLATE: Final[str] = (
    'Une session interrompue a été trouvée pour "{name}". Voulez-vous la reprendre ?'
)

# TODO list (spec §2.5)
TODO_LIST_TITLE_TEMPLATE: Final[str] = "TODO ({count})"
TODO_ADD_LINE_BUTTON: Final[str] = "+ Ajouter une ligne"
TODO_DELETE_LIST_BUTTON: Final[str] = "X Supprimer la liste"
TODO_DELETE_LIST_CONFIRM_TEMPLATE: Final[str] = "Supprimer définitivement les {count} lignes de cette liste ?"
TODO_DUPLICATE_SUFFIX: Final[str] = " (copie)"
TODO_STATE_TODO: Final[str] = "À faire"
TODO_STATE_IN_PROGRESS: Final[str] = "En cours"
TODO_STATE_DONE: Final[str] = "Terminé"
TODO_STATE_CANCELLED: Final[str] = "Annulé"
TODO_DELETE_LINE_TOAST: Final[str] = "Ligne supprimée"
TODO_UNDO_BUTTON: Final[str] = "Annuler"
TODO_COLUMN_LABEL_HEADER: Final[str] = "Libellé"
TODO_COLUMN_STATE_HEADER: Final[str] = "État"
TODO_CHANGE_STATE_MENU: Final[str] = "Changer l'état"

# History (spec §2.6)
HISTORY_POMODORO_TAB: Final[str] = "Historique Pomodoro"
HISTORY_TODO_TAB: Final[str] = "Historique TODO"
HISTORY_DELETED_BADGE: Final[str] = "(supprimé)"
HISTORY_STATUS_COMPLETED: Final[str] = "✅ Terminé"
HISTORY_STATUS_INTERRUPTED: Final[str] = "⏹ Interrompu"
HISTORY_COLUMN_NAME: Final[str] = "Nom"
HISTORY_COLUMN_DATE: Final[str] = "Date"
HISTORY_COLUMN_PLANNED_DURATION: Final[str] = "Durée prévue"
HISTORY_COLUMN_STATUS: Final[str] = "Statut"
HISTORY_COLUMN_LABEL: Final[str] = "Libellé"
HISTORY_COLUMN_POMODORO: Final[str] = "Pomodoro associé"
HISTORY_COLUMN_TRANSITION: Final[str] = "Ancien état → Nouvel état"

# Cross-cutting confirmations and toasts (spec §3.2, §3.4)
TOAST_DELETE_TODO_LIST_CONFIRM_TEMPLATE: Final[str] = (
    "Supprimer ce pomodoro et ses {count} ligne(s) TODO associées ?"
)
DIALOG_YES: Final[str] = "Oui"
DIALOG_NO: Final[str] = "Non"
DIALOG_ERROR_TITLE: Final[str] = "Erreur"
DIALOG_CONFIRM_TITLE: Final[str] = "Confirmation"

# Application shell (spec §1)
APP_WINDOW_TITLE: Final[str] = "Pomodoro"


# EOF
