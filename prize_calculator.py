import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
import json
import os
from datetime import datetime, date, timedelta
from calendar import monthrange
import webbrowser
import logging
from logging.handlers import RotatingFileHandler
import traceback

@dataclass
class DateRange:
    start_year: int
    start_month: int
    start_day: Optional[int] = None
    end_year: Optional[int] = None
    end_month: Optional[int] = None
    end_day: Optional[int] = None

    def __str__(self) -> str:
        """Format date range for display"""
        start = f"{self.start_year}-{self.start_month:02d}"
        if self.start_day:
            start += f"-{self.start_day:02d}"

        if not any([self.end_year, self.end_month, self.end_day]):
            return start

        end = f"{self.end_year}-{self.end_month:02d}" if self.end_month else ""
        if self.end_day:
            end += f"-{self.end_day:02d}"

        return f"{start} - {end}" if end else start

    def is_valid(self) -> bool:
        """Validate date range"""
        if not self.end_year and not self.end_month and not self.end_day:
            return True

        start_date = date(self.start_year, self.start_month, self.start_day or 1)
        end_date = date(self.end_year or self.start_year,
                       self.end_month or self.start_month,
                       self.end_day or monthrange(self.end_year or self.start_year,
                                                self.end_month or self.start_month)[1])
        
        return start_date <= end_date

    def overlaps(self, other: 'DateRange') -> bool:
        """Check if this range overlaps with another"""
        start_date = date(self.start_year, self.start_month, self.start_day or 1)
        end_date = date(self.end_year or self.start_year,
                       self.end_month or self.start_month,
                       self.end_day or monthrange(self.end_year or self.start_year,
                                                self.end_month or self.start_month)[1])
        
        other_start = date(other.start_year, other.start_month, other.start_day or 1)
        other_end = date(other.end_year or other.start_year,
                        other.end_month or other.start_month,
                        other.end_day or monthrange(other.end_year or other.start_year,
                                                  other.end_month or other.start_month)[1])
        
        return not (end_date < other_start or start_date > other_end)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'DateRange':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class Prize:
    id: int
    name: str
    quantity: float
    is_special: bool = False
    top_winners: int = 1

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Prize':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class Participant:
    id: int
    name: str
    damage: float
    enabled: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Participant':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class SavedState:
    date_range: DateRange
    event: str
    prizes: List[Prize]
    participants: List[Participant]
    distributions: Dict[int, List[tuple]]
    total_damage: float = 0.0
    saved_date: str = ''

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            "date_range": self.date_range.to_dict(),
            "event": self.event,
            "prizes": [p.to_dict() for p in self.prizes],
            "participants": [p.to_dict() for p in self.participants],
            "distributions": {str(k): v for k, v in self.distributions.items()},
            "total_damage": self.total_damage,
            "saved_date": self.saved_date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SavedState':
        """Create from dictionary"""
        try:
            # Aggiungiamo controlli per assicurarci che tutti i campi necessari siano presenti
            required_fields = ['date_range', 'prizes', 'participants', 'distributions']
            for field in required_fields:
                if field not in data:
                    raise KeyError(f"Campo richiesto mancante: {field}")

            # Estraiamo l'evento con un valore di default vuoto se non presente
            event = data.get("event", "")

            return cls(
                date_range=DateRange.from_dict(data["date_range"]),
                event=event,
                prizes=[Prize.from_dict(p) for p in data["prizes"]],
                participants=[Participant.from_dict(p) for p in data["participants"]],
                distributions={int(k): v for k, v in data.get("distributions", {}).items()},
                total_damage=data.get("total_damage", 0.0),  # 0.0 se non presente
                saved_date=data.get("saved_date", "")  # Stringa vuota se non presente
            )
        except Exception as e:
            raise ValueError(f"Errore nella creazione dello stato da dizionario: {str(e)}")
    
class TranslationManager:
    def __init__(self):
        self.current_language = "it"
        self.translations = {
            "it": {
                    #UI Principale
                    "title": "Distribuzione Premi",
                    "credits": "Crediti",
                    "developer": "Sviluppatore",
                    "donations": "Donazioni",
                    "close": "Chiudi",
                    "settings": "Impostazioni",
                    "backup": "Backup",
                    "import": "Importa",
                    "export": "Esporta",
                    "theme": "Tema",
                    "preferences": "Preferenze",
                    "general": "Generale",
                    "display": "Visualizzazione",

                    #Tab e Sezioni
                    "prizes": "Premi",
                    "participants": "Partecipanti",
                    "distribution": "Distribuzione",
                    "history": "Storico",
                    "current_state": "Stato Corrente",
                    "load_template": "Carica Template",
                    "filters": "Filtri",
                    "preview": "Anteprima",

                    #Campi Input e Label
                    "prize_name": "Nome Premio",
                    "participant": "Partecipante",
                    "quantity": "Quantità",
                    "damage": "Danni",
                    "enabled": "Abilitato",
                    "disabled": "Disabilitato",
                    "percentage": "Percentuale",
                    "total_damage": "Danni Totali",
                    "special_prize": "Premio Speciale",
                    "normal_prize": "Premio Normale",
                    "winners": "Vincitori",
                    "top_winners": "Numero vincitori",
                    "id": "N°",
                    "select_prize": "Seleziona Premio",
                    "total": "Totale",
                    "event": "Evento",
                    "distributions": "Distribuzioni",

                    #Controlli Data
                    "year": "Anno",
                    "month": "Mese",
                    "start_date": "Data Inizio",
                    "end_date": "Data Fine",
                    "start_day": "Giorno Inizio",
                    "end_day": "Giorno Fine",
                    "use_date_range": "Usa Intervallo Date",
                    "date": "Data",
                    "months": "Gennaio,Febbraio,Marzo,Aprile,Maggio,Giugno,Luglio,Agosto,Settembre,Ottobre,Novembre,Dicembre",

                    #Azioni
                    "add": "Aggiungi",
                    "edit": "Modifica",
                    "delete": "Elimina",
                    "save": "Salva",
                    "cancel": "Annulla",
                    "clear": "Pulisci",
                    "load": "Carica",
                    "toggle": "Attiva/Disattiva",
                    "received": "Ricevuto",
                    "refresh": "Aggiorna",
                    "update_state": "Aggiorna Stato",
                    "save_state": "Salva Stato",
                    "update_options": "Aggiorna Opzioni",
                    "backup_now": "Esegui Backup",
                    "restore": "Ripristina",
                    "move_up": "Sposta Su",
                    "move_down": "Sposta Giù",

                    #Input Modalità
                    "single_input": "Input Singolo",
                    "batch_input": "Input Multiplo",
                    "integer_only": "Solo numeri interi",
                    "load_prizes": "Carica Premi",
                    "load_participants": "Carica Partecipanti",
                    "delete_with_hash": "Usa # per eliminare un elemento",
                    "batch_prize_format": "Formato: nome:quantità[:s:vincitori] - Aggiungi 's:N' per premi speciali",
                    "batch_prize_example": "Esempio: mela d'oro:3:s:2 (premio speciale per 2 vincitori)",
                    "batch_participant_format": "Formato: nome:danni",
                    "batch_participant_example": "Esempio: mario:1000",

                    #Backup e Importazione
                    "backup_settings": "Impostazioni Backup",
                    "backup_folder": "Cartella Backup",
                    "enable_auto_backup": "Abilita Backup Automatico",
                    "backup_interval": "Intervallo Backup",
                    "backup_retention": "Conservazione Backup",
                    "keep_backups": "Mantieni Backup",
                    "select_backup": "Seleziona Backup",
                    "import_folder": "Cartella Importazione",
                    "import_settings": "Impostazioni Importazione",
                    "import_actions": "Azioni Importazione",
                    "data_folder": "Cartella Dati",
                    "auto_save": "Salvataggio Automatico",
                    "default_language": "Lingua Predefinita",
                    "font_size": "Dimensione Carattere",
                    "row_height": "Altezza Righe",
                    "tables": "Tabelle",

                    #Messaggi di Errore
                    "error": "Errore",
                    "info": "Informazione",
                    "confirm": "Conferma",
                    "name_required": "Nome richiesto",
                    "quantity_required": "Quantità richiesta",
                    "damage_required": "Danni richiesti",
                    "event_required": "Inserire il nome dell'evento",
                    "start_month_required": "Mese di inizio richiesto",
                    "prizes_and_participants_required": "Premi e partecipanti sono richiesti",
                    "missing_separator": "Manca il separatore ':'",
                    "missing_name": "Nome mancante",
                    "missing_value": "Valore mancante",
                    "missing_winners": "Numero vincitori mancante per premio speciale",
                    "invalid_winners": "Numero vincitori non valido",
                    "invalid_special": "Formato premio speciale non valido",
                    "invalid_quantity": "Quantità non valida",
                    "invalid_damage": "Danni non validi",
                    "invalid_chars": "Caratteri non validi nel nome",
                    "invalid_value": "Valore non valido",
                    "name_exists": "Nome già esistente",
                    "name_exists_msg": "Esiste già un elemento con questo nome",
                    "invalid_input": "Input non valido",
                    "invalid_date_range": "Intervallo date non valido",
                    "date_collision": "Esiste già un evento in queste date",
                    "prize_name_too_short": "Nome premio troppo corto",
                    "prize_name_too_long": "Nome premio troppo lungo",
                    "participant_name_too_short": "Nome partecipante troppo corto",
                    "participant_name_too_long": "Nome partecipante troppo lungo",
                    "event_name_too_long": "Il nome dell'evento non può superare i 50 caratteri",
                    "state_not_found": "Stato non trovato",
                    "state_not_found_with_dates": "Nessuno stato trovato con queste date",
                    "no_elements_to_update": "Nessun elemento da aggiornare",
                    "save_error": "Errore durante il salvataggio",
                    "no_saved_states": "Nessuno stato salvato",
                    "template_load_error": "Errore durante il caricamento del template",
                    "export_error": "Errore durante l'esportazione",
                    "import_error": "Errore durante l'importazione",
                    "backup_error": "Errore durante il backup",
                    "restore_error": "Errore durante il ripristino",
                    "no_backup_selected": "Nessun backup selezionato",
                    "no_backups_available": "Nessun backup disponibile",
                    "quantity_must_be_positive": "La quantità deve essere positiva",
                    "quantity_must_be_integer": "La quantità deve essere un numero intero",
                    "quantity_must_be_number": "La quantità deve essere un numero",
                    "damage_must_be_non_negative": "Il danno deve essere non negativo",
                    "damage_must_be_integer": "Il danno deve essere un numero intero",
                    "damage_must_be_number": "Il danno deve essere un numero",
                    "winners_must_be_positive": "Il numero di vincitori deve essere positivo",
                    "winners_must_be_integer": "Il numero di vincitori deve essere intero",
                    "winners_exceed_participants": "Il numero di vincitori supera il numero di partecipanti",
                    "state_incomplete_load": "Lo stato contiene elementi non ancora caricati. Procedere con il caricamento degli elementi mancanti?",

                    #Conferme
                    "confirm_delete": "Confermare eliminazione?",
                    "confirm_delete_last_prize": "Eliminando l'ultimo premio verrà eliminato anche l'evento. Procedere?",
                    "confirm_delete_last_participant": "Eliminando l'ultimo partecipante verrà eliminato anche l'evento. Procedere?",
                    "confirm_delete_prize": "Sei sicuro di voler eliminare questo premio?",
                    "confirm_delete_participant": "Sei sicuro di voler eliminare questo partecipante?",
                    "confirm_clear_prizes": "Sei sicuro di voler eliminare tutti i premi?",
                    "confirm_clear_participants": "Sei sicuro di voler eliminare tutti i partecipanti?",
                    "confirm_update": "Sei sicuro di voler aggiornare questo stato?",
                    "confirm_update_options": "Confermi l'aggiornamento delle opzioni di immissione?",
                    "ignore_update_options": "Vuoi ignorare le modifiche alle opzioni di immissione? Le modifiche ai dati verranno comunque salvate",
                    "cancel_all_updates": "Vuoi annullare tutte le modifiche? Nessuna modifica verrà salvata",
                    "confirm_restore": "Sei sicuro di voler ripristinare questo backup?",
                    "confirm_new_state": "Ci sono modifiche non salvate. Vuoi procedere con un nuovo stato?",
                    "confirm_discard_changes": "Confermi di voler annullare le modifiche?",

                    #Messaggi di Successo
                    "state_saved": "Stato salvato con successo",
                    "state_updated": "Stato aggiornato con successo",
                    "backup_created": "Backup creato con successo",
                    "restore_completed": "Ripristino completato",
                    "export_completed": "Esportazione completata",
                    "preferences_saved": "Preferenze salvate",
                    "changes_saved": "Modifiche salvate",

                    #Log Messages
                    "log_app_initialized": "Applicazione inizializzata",
                    "log_ui_components_initialized": "Componenti UI inizializzati",
                    "log_styles_configured": "Stili configurati",
                    "log_language_selector_created": "Selettore lingua creato",
                    "log_top_frame_created": "Frame superiore creato",
                    "log_state_frame_created": "Frame stato creato",
                    "log_date_controls_created": "Controlli data creati",
                    "log_date_range_frames_setup": "Frame intervallo date configurati",
                    "log_month_values_updated": "Valori mesi aggiornati",
                    "log_buttons_state_updated": "Stato pulsanti aggiornato",
                    "log_prize_headers_updated": "Intestazioni premi aggiornate",
                    "log_participant_headers_updated": "Intestazioni partecipanti aggiornate",
                    "log_distribution_headers_updated": "Intestazioni distribuzione aggiornate",
                    "log_history_headers_updated": "Intestazioni cronologia aggiornate",
                    "log_tables_content_refreshed": "Contenuto tabelle aggiornato",
                    "log_tables_updated": "Tabelle aggiornate",
                    "log_ui_text_updated": "Testi UI aggiornati",
                    "log_month_combos_setup": "Combo mesi configurate",
                    "log_day_combos_setup": "Combo giorni configurate",
                    "log_year_frame_created": "Frame anno creato",
                    "log_date_range_frame_created": "Frame intervallo date creato",
                    "log_drag_started": "Trascinamento iniziato",
                    "log_drag_motion": "Movimento trascinamento",
                    "log_drag_completed": "Trascinamento completato",
                    "log_prize_mode_toggled": "Modalità premio cambiata",
                    "log_participant_mode_toggled": "Modalità partecipante cambiata",
                    "log_prize_added": "Premio aggiunto: {name}",
                    "log_participant_added": "Partecipante aggiunto: {name}",
                    "log_prize_edited": "Premio modificato: {name}",
                    "log_participant_edited": "Partecipante modificato: {name}",
                    "log_prize_deleted": "Premio eliminato: {name}",
                    "log_participant_deleted": "Partecipante eliminato: {name}",
                    "log_participant_toggled": "Stato partecipante cambiato: {name}",
                    "log_state_saved": "Stato salvato: {event}",
                    "log_state_loaded": "Stato caricato: {event}",
                    "log_distribution_calculated": "Distribuzione calcolata per premio: {prize_id}",
                    "log_language_changed": "Lingua cambiata a: {language}",
                    "log_state_file_saved": "File stato salvato: {filename}",
                    "log_states_loaded": "Stati caricati: {count}",
                    "log_distribution_updated": "Distribuzione aggiornata per premio: {prize_id}",
                    "log_prize_action_handled": "Azione premio gestita: {action}",
                    "log_participant_action_handled": "Azione partecipante gestita: {action}",
                    "log_backup_created": "Backup creato: {filename}",
                    "log_restore_completed": "Ripristino completato: {filename}",
                    "log_preferences_saved": "Preferenze salvate",
                    "log_theme_applied": "Tema applicato: {theme}",
                    "log_data_folder_created": "Cartella dati creata",
                    "log_general_preferences_created": "Preferenze generali create",
                    "log_display_preferences_created": "Preferenze visualizzazione create",
                    "log_backup_preferences_created": "Preferenze backup create",
                    "log_auto_backup_setup": "Setup backup automatico: intervallo={interval}, retention={retention}",
                    "log_old_backup_removed": "Vecchio backup rimosso: {file}",
                    "log_preference_saved": "Preferenza salvata: {key}",
                    "log_sorting_applied": "Ordinamento applicato: {column}",

                    #Log Errors
                    "log_error_ui_setup": "Errore durante la configurazione UI: {error}",
                    "log_error_styles": "Errore configurazione stili: {error}",
                    "log_error_top_frame": "Errore creazione frame superiore: {error}",
                    "log_error_state_frame": "Errore creazione frame stato: {error}",
                    "log_error_date_controls": "Errore creazione controlli data: {error}",
                    "log_error_year_frame": "Errore creazione frame anno: {error}",
                    "log_error_date_range_frame": "Errore creazione frame intervallo date: {error}",
                    "log_error_prize_headers": "Errore aggiornamento intestazioni premi: {error}",
                    "log_error_participant_headers": "Errore aggiornamento intestazioni partecipanti: {error}",
                    "log_error_distribution_headers": "Errore aggiornamento intestazioni distribuzione: {error}",
                    "log_error_history_headers": "Errore aggiornamento intestazioni cronologia: {error}",
                    "log_error_refreshing_tables": "Errore aggiornamento tabelle: {error}",
                    "log_error_sorting_table": "Errore ordinamento tabella: {error}",
                    "log_error_prize_action": "Errore gestione azione premio: {error}",
                    "log_error_participant_action": "Errore gestione azione partecipante: {error}",
                    "log_error_saving_state": "Errore salvataggio stato: {error}",
                    "log_error_loading_state": "Errore caricamento stato: {error}",
                    "log_error_distribution_calculation": "Errore calcolo distribuzione: {error}",
                    "log_error_changing_language": "Errore cambio lingua: {error}",
                    "log_error_drag_drop": "Errore durante drag and drop: {error}",
                    "log_error_validation": "Errore validazione: {error}",
                    "log_error_adding_prizes": "Errore aggiunta premi: {error}",
                    "log_error_adding_participants": "Errore aggiunta partecipanti: {error}",
                    "log_error_updating_ui": "Errore aggiornamento UI: {error}",
                    "log_error_updating_distribution": "Errore aggiornamento distribuzione: {error}",
                    "log_error_backup": "Errore backup: {error}",
                    "log_error_restore": "Errore ripristino: {error}",
                    "log_error_preferences": "Errore preferenze: {error}",
                    "log_error_saving_preferences": "Errore salvataggio preferenze: {error}",
                    "log_error_applying_theme": "Errore applicazione tema: {error}",
                    "log_error_creating_folder": "Errore creazione cartella: {error}",
                    "log_error_month_combos": "Errore configurazione combo mesi: {error}",
                    "log_error_day_combos": "Errore configurazione combo giorni: {error}",
                    "log_error_date_validation": "Errore validazione date: {error}",
                    "log_error_filtering_states": "Errore filtraggio stati: {error}",
                    "log_error_saving_file": "Errore salvataggio file: {error}",
                    "log_error_reading_backup": "Errore lettura backup: {error}",
                    "log_error_preview": "Errore generazione anteprima: {error}",
                    "log_error_getting_preference": "Errore lettura preferenza: {error}",
                    "log_error_saving_preference": "Errore salvataggio preferenza: {error}",
                    "log_error_centering_dialog": "Errore centraggio finestra dialogo: {error}",
                    "log_error_language_selector": "Errore creazione selettore lingua: {error}",
                    "log_error_buttons_state": "Errore aggiornamento stato pulsanti: {error}",
                    "log_error_quantity_validation": "Errore validazione quantità: {error}",
                    "log_error_integer_distribution": "Errore distribuzione numeri interi: {error}",
                    "log_error_prize_mode_toggle": "Errore cambio modalità premio: {error}",
                    "log_error_participant_mode_toggle": "Errore cambio modalità partecipante: {error}",
                    "log_error_parsing_prize": "Errore parsing premio: {error}",
                    "log_error_parsing_participant": "Errore parsing partecipante: {error}",
                    "log_error_updating_button_states": "Errore aggiornamento stato pulsanti: {error}",
                    "log_error_auto_backup": "Errore backup automatico: {error}",
                    "log_error_cleanup_backups": "Errore pulizia vecchi backup: {error}",
                    "log_error_loading_preferences": "Errore caricamento preferenze: {error}",
                    "log_error_applying_preferences": "Errore applicazione preferenze: {error}",
                    "log_error_export": "Errore esportazione: {error}",
                    "log_error_import": "Errore importazione: {error}",
                    "log_error_name_validation": "Errore validazione nome: {error}",
                    "log_error_validating_winners": "Errore validazione vincitori: {error}",
                    "log_error_toggle_winners": "Errore toggle vincitori: {error}",
                    "log_error_toggle_participant": "Errore toggle partecipante: {error}",
                    "log_error_prize_template": "Errore template premio: {error}",
                    "log_error_participant_template": "Errore template partecipante: {error}",
                    "log_error_update_state": "Errore aggiornamento stato: {error}",
                    "log_error_creating_shortcuts": "Errore creazione scorciatoie: {error}",
                    "log_error_showing_settings": "Errore visualizzazione impostazioni: {error}",
                    "log_error_showing_backup_settings": "Errore visualizzazione impostazioni backup: {error}",
                    "log_error_showing_import_settings": "Errore visualizzazione impostazioni importazione: {error}",
                    "log_error_creating_menus": "Errore creazione menu: {error}",
                    "log_error_prize_menu": "Errore menu premio: {error}",
                    "log_error_participant_menu": "Errore menu partecipante: {error}",
                    "log_error_moving_item": "Errore spostamento elemento: {error}",
                    "log_error_credits": "Errore visualizzazione crediti: {error}",
                    "log_error_restore_dialog": "Errore finestra dialogo ripristino: {error}",
                    "log_error_number_format": "Errore formattazione numero: {error}",
                    "log_error_formatting_damages": "Errore formattazione danni: {error}",
                    "log_error_formatting_prizes": "Errore formattazione premi: {error}",
                    "log_error_formatting_distributions": "Errore formattazione distribuzioni: {error}",
                    "log_error_dialog": "Errore finestra dialogo: {error}"
                },
                "en": {
                    #Main UI
                    "title": "Prize Distribution",
                    "credits": "Credits",
                    "developer": "Developer",
                    "donations": "Donations",
                    "close": "Close",
                    "settings": "Settings",
                    "backup": "Backup",
                    "import": "Import",
                    "export": "Export",
                    "theme": "Theme",
                    "preferences": "Preferences",
                    "general": "General",
                    "display": "Display",

                    #Tab e Sezioni
                    "prizes": "Prizes",
                    "participants": "Participants",
                    "distribution": "Distribution",
                    "history": "History",
                    "current_state": "Current State",
                    "load_template": "Load Template",
                    "filters": "Filters",
                    "preview": "Preview",

                    #Campi Input e Label
                    "prize_name": "Prize Name",
                    "participant": "Participant",
                    "quantity": "Quantity",
                    "damage": "Damage",
                    "enabled": "Enabled",
                    "disabled": "Disabled",
                    "percentage": "Percentage",
                    "total_damage": "Total Damage",
                    "special_prize": "Special Prize",
                    "normal_prize": "Normal Prize",
                    "winners": "Winners",
                    "top_winners": "Number of Winners",
                    "id": "#",
                    "select_prize": "Select Prize",
                    "total": "Total",
                    "event": "Event",
                    "distributions": "Distributions",

                    #Controlli Data
                    "year": "Year",
                    "month": "Month",
                    "start_date": "Start Date",
                    "end_date": "End Date",
                    "start_day": "Start Day",
                    "end_day": "End Day",
                    "use_date_range": "Use Date Range",
                    "date": "Date",
                    "months": "January,February,March,April,May,June,July,August,September,October,November,December",

                    #Azioni
                    "add": "Add",
                    "edit": "Edit",
                    "delete": "Delete",
                    "save": "Save",
                    "cancel": "Cancel",
                    "clear": "Clear",
                    "load": "Load",
                    "toggle": "Toggle",
                    "received": "Received",
                    "refresh": "Refresh",
                    "update_state": "Update State",
                    "save_state": "Save State",
                    "update_options": "Update Options",
                    "backup_now": "Backup Now",
                    "restore": "Restore",
                    "move_up": "Move Up",
                    "move_down": "Move Down",

                    #Input Modalità
                    "single_input": "Single Input",
                    "batch_input": "Batch Input",
                    "integer_only": "Integer Only",
                    "load_prizes": "Load Prizes",
                    "load_participants": "Load Participants",
                    "delete_with_hash": "Use # to delete an item",
                    "batch_prize_format": "Format: name:quantity[:s:winners] - Add 's:N' for special prizes",
                    "batch_prize_example": "Example: golden apple:3:s:2 (special prize for 2 winners)",
                    "batch_participant_format": "Format: name:damage",
                    "batch_participant_example": "Example: mario:1000",

                    #Backup e Importazione
                    "backup_settings": "Backup Settings",
                    "backup_folder": "Backup Folder",
                    "enable_auto_backup": "Enable Auto Backup",
                    "backup_interval": "Backup Interval",
                    "backup_retention": "Backup Retention",
                    "keep_backups": "Keep Backups",
                    "select_backup": "Select Backup",
                    "import_folder": "Import Folder",
                    "import_settings": "Import Settings",
                    "import_actions": "Import Actions",
                    "data_folder": "Data Folder",
                    "auto_save": "Auto Save",
                    "default_language": "Default Language",
                    "font_size": "Font Size",
                    "row_height": "Row Height",
                    "tables": "Tables",

                    #Messaggi di Errore
                    "error": "Error",
                    "info": "Information",
                    "confirm": "Confirm",
                    "name_required": "Name required",
                    "quantity_required": "Quantity required",
                    "damage_required": "Damage required",
                    "event_required": "Event name required",
                    "start_month_required": "Start month required",
                    "prizes_and_participants_required": "Prizes and participants are required",
                    "missing_separator": "Missing separator ':'",
                    "missing_name": "Missing name",
                    "missing_value": "Missing value",
                    "missing_winners": "Missing winners count for special prize",
                    "invalid_winners": "Invalid winners count",
                    "invalid_special": "Invalid special prize format",
                    "invalid_quantity": "Invalid quantity",
                    "invalid_damage": "Invalid damage",
                    "invalid_chars": "Invalid characters in name",
                    "invalid_value": "Invalid value",
                    "name_exists": "Name exists",
                    "name_exists_msg": "An element with this name already exists",
                    "invalid_input": "Invalid input",
                    "invalid_date_range": "Invalid date range",
                    "date_collision": "An event already exists on these dates",
                    "prize_name_too_short": "Prize name too short",
                    "prize_name_too_long": "Prize name too long",
                    "participant_name_too_short": "Participant name too short",
                    "participant_name_too_long": "Participant name too long",
                    "event_name_too_long": "Event name cannot exceed 50 characters",
                    "state_not_found": "State not found",
                    "state_not_found_with_dates": "No state found with these dates",
                    "no_elements_to_update": "No elements to update",
                    "save_error": "Error during save",
                    "no_saved_states": "No saved states",
                    "template_load_error": "Error loading template",
                    "export_error": "Error during export",
                    "import_error": "Error during import",
                    "backup_error": "Error during backup",
                    "restore_error": "Error during restore",
                    "no_backup_selected": "No backup selected",
                    "no_backups_available": "No backups available",
                    "quantity_must_be_positive": "Quantity must be positive",
                    "quantity_must_be_integer": "Quantity must be an integer",
                    "quantity_must_be_number": "Quantity must be a number",
                    "damage_must_be_non_negative": "Damage must be non-negative",
                    "damage_must_be_integer": "Damage must be an integer",
                    "damage_must_be_number": "Damage must be a number",
                    "winners_must_be_positive": "Winners count must be positive",
                    "winners_must_be_integer": "Winners count must be an integer",
                    "winners_exceed_participants": "Winners count exceeds number of participants",
                    "state_incomplete_load": "The state contains unloaded elements. Proceed with loading missing elements?",

                    #Conferme
                    "confirm_delete": "Confirm deletion?",
                    "confirm_delete_last_prize": "Deleting the last prize will also delete the event. Proceed?",
                    "confirm_delete_last_participant": "Deleting the last participant will also delete the event. Proceed?",
                    "confirm_delete_prize": "Are you sure you want to delete this prize?",
                    "confirm_delete_participant": "Are you sure you want to delete this participant?",
                    "confirm_clear_prizes": "Are you sure you want to delete all prizes?",
                    "confirm_clear_participants": "Are you sure you want to delete all participants?",
                    "confirm_update": "Are you sure you want to update this state?",
                    "confirm_update_options": "Confirm updating input options?",
                    "ignore_update_options": "Do you want to ignore input option changes? Data changes will still be saved",
                    "cancel_all_updates": "Do you want to cancel all changes? No changes will be saved",
                    "confirm_restore": "Are you sure you want to restore this backup?",
                    "confirm_new_state": "There are unsaved changes. Do you want to proceed with a new state?",
                    "confirm_discard_changes": "Confirm discarding changes?",

                    #Success Messages
                    "state_saved": "State saved successfully",
                    "state_updated": "State updated successfully",
                    "backup_created": "Backup created successfully",
                    "restore_completed": "Restore completed",
                    "export_completed": "Export completed",
                    "preferences_saved": "Preferences saved",
                    "changes_saved": "Changes saved",

                    #Log Messages
                    "log_app_initialized": "Application initialized",
                    "log_ui_components_initialized": "UI components initialized",
                    "log_styles_configured": "Styles configured",
                    "log_language_selector_created": "Language selector created",
                    "log_top_frame_created": "Top frame created",
                    "log_state_frame_created": "State frame created",
                    "log_date_controls_created": "Date controls created",
                    "log_date_range_frames_setup": "Date range frames setup",
                    "log_month_values_updated": "Month values updated",
                    "log_buttons_state_updated": "Button states updated",
                    "log_prize_headers_updated": "Prize headers updated",
                    "log_participant_headers_updated": "Participant headers updated",
                    "log_distribution_headers_updated": "Distribution headers updated",
                    "log_history_headers_updated": "History headers updated",
                    "log_tables_content_refreshed": "Tables content refreshed",
                    "log_tables_updated": "Tables updated",
                    "log_ui_text_updated": "UI text updated",
                    "log_month_combos_setup": "Month combos setup",
                    "log_day_combos_setup": "Day combos setup",
                    "log_year_frame_created": "Year frame created",
                    "log_date_range_frame_created": "Date range frame created",
                    "log_drag_started": "Drag started",
                    "log_drag_motion": "Drag motion",
                    "log_drag_completed": "Drag completed",
                    "log_prize_mode_toggled": "Prize mode toggled",
                    "log_participant_mode_toggled": "Participant mode toggled",
                    "log_prize_added": "Prize added: {name}",
                    "log_participant_added": "Participant added: {name}",
                    "log_prize_edited": "Prize edited: {name}",
                    "log_participant_edited": "Participant edited: {name}",
                    "log_prize_deleted": "Prize deleted: {name}",
                    "log_participant_deleted": "Participant deleted: {name}",
                    "log_participant_toggled": "Participant state toggled: {name}",
                    "log_state_saved": "State saved: {event}",
                    "log_state_loaded": "State loaded: {event}",
                    "log_distribution_calculated": "Distribution calculated for prize: {prize_id}",
                    "log_language_changed": "Language changed to: {language}",
                    "log_state_file_saved": "State file saved: {filename}",
                    "log_states_loaded": "States loaded: {count}",
                    "log_distribution_updated": "Distribution updated for prize: {prize_id}",
                    "log_prize_action_handled": "Prize action handled: {action}",
                    "log_participant_action_handled": "Participant action handled: {action}",
                    "log_backup_created": "Backup created: {filename}",
                    "log_restore_completed": "Restore completed: {filename}",
                    "log_preferences_saved": "Preferences saved",
                    "log_theme_applied": "Theme applied: {theme}",
                    "log_data_folder_created": "Data folder created",
                    "log_general_preferences_created": "General preferences created",
                    "log_display_preferences_created": "Display preferences created",
                    "log_backup_preferences_created": "Backup preferences created",
                    "log_auto_backup_setup": "Auto backup setup: interval={interval}, retention={retention}",
                    "log_old_backup_removed": "Old backup removed: {file}",
                    "log_preference_saved": "Preference saved: {key}",
                    "log_sorting_applied": "Sorting applied: {column}",
                    "log_error_ui_setup": "Error in UI setup: {error}",
                    "log_error_styles": "Error configuring styles: {error}",
                    "log_error_top_frame": "Error creating top frame: {error}",
                    "log_error_state_frame": "Error creating state frame: {error}",
                    "log_error_date_controls": "Error creating date controls: {error}",
                    "log_error_year_frame": "Error creating year frame: {error}",
                    "log_error_date_range_frame": "Error creating date range frame: {error}",
                    "log_error_prize_headers": "Error updating prize headers: {error}",
                    "log_error_participant_headers": "Error updating participant headers: {error}",
                    "log_error_distribution_headers": "Error updating distribution headers: {error}",
                    "log_error_history_headers": "Error updating history headers: {error}",
                    "log_error_refreshing_tables": "Error refreshing tables: {error}",
                    "log_error_sorting_table": "Error sorting table: {error}",
                    "log_error_prize_action": "Error handling prize action: {error}",
                    "log_error_participant_action": "Error handling participant action: {error}",
                    "log_error_saving_state": "Error saving state: {error}",
                    "log_error_loading_state": "Error loading state: {error}",
                    "log_error_distribution_calculation": "Error calculating distribution: {error}",
                    "log_error_changing_language": "Error changing language: {error}",
                    "log_error_drag_drop": "Error during drag and drop: {error}",
                    "log_error_validation": "Error in validation: {error}",
                    "log_error_adding_prizes": "Error adding prizes: {error}",
                    "log_error_adding_participants": "Error adding participants: {error}",
                    "log_error_updating_ui": "Error updating UI: {error}",
                    "log_error_updating_distribution": "Error updating distribution: {error}",
                    "log_error_backup": "Error during backup: {error}",
                    "log_error_restore": "Error during restore: {error}",
                    "log_error_preferences": "Error in preferences: {error}",
                    "log_error_saving_preferences": "Error saving preferences: {error}",
                    "log_error_applying_theme": "Error applying theme: {error}",
                    "log_error_creating_folder": "Error creating folder: {error}",
                    "log_error_month_combos": "Error setting up month combos: {error}",
                    "log_error_day_combos": "Error setting up day combos: {error}",
                    "log_error_date_validation": "Error validating dates: {error}",
                    "log_error_filtering_states": "Error filtering states: {error}",
                    "log_error_saving_file": "Error saving file: {error}",
                    "log_error_reading_backup": "Error reading backup: {error}",
                    "log_error_preview": "Error generating preview: {error}",
                    "log_error_getting_preference": "Error getting preference: {error}",
                    "log_error_saving_preference": "Error saving preference: {error}",
                    "log_error_centering_dialog": "Error centering dialog: {error}",
                    "log_error_language_selector": "Error creating language selector: {error}",
                    "log_error_buttons_state": "Error updating buttons state: {error}",
                    "log_error_quantity_validation": "Error validating quantity: {error}",
                    "log_error_integer_distribution": "Error in integer distribution: {error}",
                    "log_error_prize_mode_toggle": "Error toggling prize mode: {error}",
                    "log_error_participant_mode_toggle": "Error toggling participant mode: {error}",
                    "log_error_parsing_prize": "Error parsing prize: {error}",
                    "log_error_parsing_participant": "Error parsing participant: {error}",
                    "log_error_updating_button_states": "Error updating button states: {error}",
                    "log_error_auto_backup": "Error in auto backup: {error}",
                    "log_error_cleanup_backups": "Error cleaning up old backups: {error}",
                    "log_error_loading_preferences": "Error loading preferences: {error}",
                    "log_error_applying_preferences": "Error applying preferences: {error}",
                    "log_error_export": "Error during export: {error}",
                    "log_error_import": "Error during import: {error}",
                    "log_error_name_validation": "Error validating name: {error}",
                    "log_error_validating_winners": "Error validating winners: {error}",
                    "log_error_toggle_winners": "Error toggling winners: {error}",
                    "log_error_toggle_participant": "Error toggling participant: {error}",
                    "log_error_prize_template": "Error in prize template: {error}",
                    "log_error_participant_template": "Error in participant template: {error}",
                    "log_error_update_state": "Error updating state: {error}",
                    "log_error_creating_shortcuts": "Error creating shortcuts: {error}",
                    "log_error_showing_settings": "Error showing settings: {error}",
                    "log_error_showing_backup_settings": "Error showing backup settings: {error}",
                    "log_error_showing_import_settings": "Error showing import settings: {error}",
                    "log_error_creating_menus": "Error creating menus: {error}",
                    "log_error_prize_menu": "Error in prize menu: {error}",
                    "log_error_participant_menu": "Error in participant menu: {error}",
                    "log_error_moving_item": "Error moving item: {error}",
                    "log_error_credits": "Error showing credits: {error}",
                    "log_error_restore_dialog": "Error in restore dialog: {error}",
                    "log_error_number_format": "Error formatting number: {error}",
                    "log_error_formatting_damages": "Error formatting damages: {error}",
                    "log_error_formatting_prizes": "Error formatting prizes: {error}",
                    "log_error_formatting_distributions": "Error formatting distributions: {error}",
                    "log_error_dialog": "Error in dialog: {error}"
                },
                "fr": {
                    #Interface Principale
                    "title": "Distribution des Prix",
                    "credits": "Crédits",
                    "developer": "Développeur",
                    "donations": "Dons",
                    "close": "Fermer",
                    "settings": "Paramètres",
                    "backup": "Sauvegarde",
                    "import": "Importer",
                    "export": "Exporter",
                    "theme": "Thème",
                    "preferences": "Préférences",
                    "general": "Général",
                    "display": "Affichage",

                    #Onglets et Sections
                    "prizes": "Prix",
                    "participants": "Participants",
                    "distribution": "Distribution",
                    "history": "Historique",
                    "current_state": "État Actuel",
                    "load_template": "Charger Modèle",
                    "filters": "Filtres",
                    "preview": "Aperçu",

                    #Champs et Étiquettes
                    "prize_name": "Nom du Prix",
                    "participant": "Participant",
                    "quantity": "Quantité",
                    "damage": "Dégâts",
                    "enabled": "Activé",
                    "disabled": "Désactivé",
                    "percentage": "Pourcentage",
                    "total_damage": "Dégâts Totaux",
                    "special_prize": "Prix Spécial",
                    "normal_prize": "Prix Normal",
                    "winners": "Gagnants",
                    "top_winners": "Nombre de Gagnants",
                    "id": "N°",
                    "select_prize": "Sélectionner Prix",
                    "total": "Total",
                    "event": "Événement",
                    "distributions": "Distributions",

                    #Contrôles de Date
                    "year": "Année",
                    "month": "Mois",
                    "start_date": "Date de Début",
                    "end_date": "Date de Fin",
                    "start_day": "Jour de Début",
                    "end_day": "Jour de Fin",
                    "use_date_range": "Utiliser Plage de Dates",
                    "date": "Date",
                    "months": "Janvier,Février,Mars,Avril,Mai,Juin,Juillet,Août,Septembre,Octobre,Novembre,Décembre",

                    #Actions
                    "add": "Ajouter",
                    "edit": "Modifier",
                    "delete": "Supprimer",
                    "save": "Enregistrer",
                    "cancel": "Annuler",
                    "clear": "Effacer",
                    "load": "Charger",
                    "toggle": "Basculer",
                    "received": "Reçu",
                    "refresh": "Actualiser",
                    "update_state": "Mettre à Jour l'État",
                    "save_state": "Enregistrer l'État",
                    "update_options": "Mettre à Jour les Options",
                    "backup_now": "Sauvegarder Maintenant",
                    "restore": "Restaurer",
                    "move_up": "Monter",
                    "move_down": "Descendre",

                    #Modes de Saisie
                    "single_input": "Saisie Unique",
                    "batch_input": "Saisie Multiple",
                    "integer_only": "Nombres Entiers Uniquement",
                    "load_prizes": "Charger Prix",
                    "load_participants": "Charger Participants",
                    "delete_with_hash": "Utilisez # pour supprimer un élément",
                    "batch_prize_format": "Format: nom:quantité[:s:gagnants] - Ajoutez 's:N' pour les prix spéciaux",
                    "batch_prize_example": "Exemple: pomme d'or:3:s:2 (prix spécial pour 2 gagnants)",
                    "batch_participant_format": "Format: nom:dégâts",
                    "batch_participant_example": "Exemple: mario:1000",

                    #Sauvegarde et Importation
                    "backup_settings": "Paramètres de Sauvegarde",
                    "backup_folder": "Dossier de Sauvegarde",
                    "enable_auto_backup": "Activer Sauvegarde Auto",
                    "backup_interval": "Intervalle de Sauvegarde",
                    "backup_retention": "Rétention des Sauvegardes",
                    "keep_backups": "Conserver Sauvegardes",
                    "select_backup": "Sélectionner Sauvegarde",
                    "import_folder": "Dossier d'Importation",
                    "import_settings": "Paramètres d'Importation",
                    "import_actions": "Actions d'Importation",
                    "data_folder": "Dossier de Données",
                    "auto_save": "Sauvegarde Automatique",
                    "default_language": "Langue par Défaut",
                    "font_size": "Taille de Police",
                    "row_height": "Hauteur des Lignes",
                    "tables": "Tableaux",

                    #Messages d'Erreur
                    "error": "Erreur",
                    "info": "Information",
                    "confirm": "Confirmer",
                    "name_required": "Nom requis",
                    "quantity_required": "Quantité requise",
                    "damage_required": "Dégâts requis",
                    "event_required": "Nom de l'événement requis",
                    "start_month_required": "Mois de début requis",
                    "prizes_and_participants_required": "Prix et participants requis",
                    "missing_separator": "Séparateur ':' manquant",
                    "missing_name": "Nom manquant",
                    "missing_value": "Valeur manquante",
                    "missing_winners": "Nombre de gagnants manquant pour le prix spécial",
                    "invalid_winners": "Nombre de gagnants invalide",
                    "invalid_special": "Format de prix spécial invalide",
                    "invalid_quantity": "Quantité invalide",
                    "invalid_damage": "Dégâts invalides",
                    "invalid_chars": "Caractères invalides dans le nom",
                    "invalid_value": "Valeur invalide",
                    "name_exists": "Nom déjà existant",
                    "name_exists_msg": "Un élément avec ce nom existe déjà",
                    "invalid_input": "Saisie invalide",
                    "invalid_date_range": "Plage de dates invalide",
                    "date_collision": "Un événement existe déjà à ces dates",
                    "prize_name_too_short": "Nom du prix trop court",
                    "prize_name_too_long": "Nom du prix trop long",
                    "participant_name_too_short": "Nom du participant trop court",
                    "participant_name_too_long": "Nom du participant trop long",
                    "event_name_too_long": "Le nom de l'événement ne peut pas dépasser 50 caractères",
                    "state_not_found": "État non trouvé",
                    "state_not_found_with_dates": "Aucun état trouvé avec ces dates",
                    "no_elements_to_update": "Aucun élément à mettre à jour",
                    "save_error": "Erreur lors de l'enregistrement",
                    "no_saved_states": "Aucun état sauvegardé",
                    "template_load_error": "Erreur lors du chargement du modèle",
                    "export_error": "Erreur lors de l'exportation",
                    "import_error": "Erreur lors de l'importation",
                    "backup_error": "Erreur lors de la sauvegarde",
                    "restore_error": "Erreur lors de la restauration",
                    "no_backup_selected": "Aucune sauvegarde sélectionnée",
                    "no_backups_available": "Aucune sauvegarde disponible",
                    "quantity_must_be_positive": "La quantité doit être positive",
                    "quantity_must_be_integer": "La quantité doit être un nombre entier",
                    "quantity_must_be_number": "La quantité doit être un nombre",
                    "damage_must_be_non_negative": "Les dégâts doivent être non négatifs",
                    "damage_must_be_integer": "Les dégâts doivent être un nombre entier",
                    "damage_must_be_number": "Les dégâts doivent être un nombre",
                    "winners_must_be_positive": "Le nombre de gagnants doit être positif",
                    "winners_must_be_integer": "Le nombre de gagnants doit être un nombre entier",
                    "winners_exceed_participants": "Le nombre de gagnants dépasse le nombre de participants",
                    "state_incomplete_load": "L'état contient des éléments non chargés. Procéder au chargement des éléments manquants ?",

                    #Confirmations
                    "confirm_delete": "Confirmer la suppression ?",
                    "confirm_delete_last_prize": "La suppression du dernier prix supprimera également l'événement. Continuer ?",
                    "confirm_delete_last_participant": "La suppression du dernier participant supprimera également l'événement. Continuer ?",
                    "confirm_delete_prize": "Êtes-vous sûr de vouloir supprimer ce prix ?",
                    "confirm_delete_participant": "Êtes-vous sûr de vouloir supprimer ce participant ?",
                    "confirm_clear_prizes": "Êtes-vous sûr de vouloir supprimer tous les prix ?",
                    "confirm_clear_participants": "Êtes-vous sûr de vouloir supprimer tous les participants ?",
                    "confirm_update": "Êtes-vous sûr de vouloir mettre à jour cet état ?",
                    "confirm_update_options": "Confirmer la mise à jour des options ?",
                    "ignore_update_options": "Voulez-vous ignorer les modifications des options ? Les modifications de données seront conservées",
                    "cancel_all_updates": "Voulez-vous annuler toutes les modifications ? Aucune modification ne sera enregistrée",
                    "confirm_restore": "Êtes-vous sûr de vouloir restaurer cette sauvegarde ?",
                    "confirm_new_state": "Il y a des modifications non sauvegardées. Voulez-vous continuer avec un nouvel état ?",
                    "confirm_discard_changes": "Confirmer l'annulation des modifications ?",

                    #Messages de Succès
                    "state_saved": "État enregistré avec succès",
                    "state_updated": "État mis à jour avec succès",
                    "backup_created": "Sauvegarde créée avec succès",
                    "restore_completed": "Restauration terminée",
                    "export_completed": "Exportation terminée",
                    "preferences_saved": "Préférences enregistrées",
                    "changes_saved": "Modifications enregistrées",

                    #Messages de Journal
                    "log_app_initialized": "Application initialisée",
                    "log_ui_components_initialized": "Composants UI initialisés",
                    "log_styles_configured": "Styles configurés",
                    "log_language_selector_created": "Sélecteur de langue créé",
                    "log_top_frame_created": "Cadre supérieur créé",
                    "log_state_frame_created": "Cadre d'état créé",
                    "log_date_controls_created": "Contrôles de date créés",
                    "log_date_range_frames_setup": "Cadres de plage de dates configurés",
                    "log_month_values_updated": "Valeurs des mois mises à jour",
                    "log_buttons_state_updated": "État des boutons mis à jour",
                    "log_prize_headers_updated": "En-têtes des prix mis à jour",
                    "log_participant_headers_updated": "En-têtes des participants mis à jour",
                    "log_distribution_headers_updated": "En-têtes de distribution mis à jour",
                    "log_history_headers_updated": "En-têtes d'historique mis à jour",
                    "log_tables_content_refreshed": "Contenu des tableaux actualisé",
                    "log_tables_updated": "Tableaux mis à jour",
                    "log_ui_text_updated": "Texte UI mis à jour",
                    "log_month_combos_setup": "Combos des mois configurés",
                    "log_day_combos_setup": "Combos des jours configurés",
                    "log_year_frame_created": "Cadre année créé",
                    "log_date_range_frame_created": "Cadre plage de dates créé",
                    "log_drag_started": "Glisser commencé",
                    "log_drag_motion": "Mouvement de glissement",
                    "log_drag_completed": "Glisser terminé",
                    "log_prize_mode_toggled": "Mode prix basculé",
                    "log_participant_mode_toggled": "Mode participant basculé",
                    "log_prize_added": "Prix ajouté : {name}",
                    "log_participant_added": "Participant ajouté : {name}",
                    "log_prize_edited": "Prix modifié : {name}",
                    "log_participant_edited": "Participant modifié : {name}",
                    "log_prize_deleted": "Prix supprimé : {name}",
                    "log_participant_deleted": "Participant supprimé : {name}",
                    "log_participant_toggled": "État du participant basculé : {name}",
                    "log_state_saved": "État enregistré : {event}",
                    "log_state_loaded": "État chargé : {event}",
                    "log_distribution_calculated": "Distribution calculée pour le prix : {prize_id}",
                    "log_language_changed": "Langue changée en : {language}",
                    "log_state_file_saved": "Fichier d'état enregistré : {filename}",
                    "log_states_loaded": "États chargés : {count}",
                    "log_distribution_updated": "Distribution mise à jour pour le prix : {prize_id}",
                    "log_prize_action_handled": "Action prix traitée : {action}",
                    "log_participant_action_handled": "Action participant traitée : {action}",
                    "log_backup_created": "Sauvegarde créée : {filename}",
                    "log_restore_completed": "Restauration terminée : {filename}",
                    "log_preferences_saved": "Préférences enregistrées",
                    "log_theme_applied": "Thème appliqué : {theme}",
                    "log_data_folder_created": "Dossier de données créé",
                    "log_general_preferences_created": "Préférences générales créées",
                    "log_display_preferences_created": "Préférences d'affichage créées",
                    "log_backup_preferences_created": "Préférences de sauvegarde créées",
                    "log_auto_backup_setup": "Configuration sauvegarde auto : intervalle={interval}, rétention={retention}",
                    "log_old_backup_removed": "Ancienne sauvegarde supprimée : {file}",
                    "log_preference_saved": "Préférence enregistrée : {key}",
                    "log_sorting_applied": "Tri appliqué : {column}",
                    
                    #Erreurs de Journal (suite)
                    "log_error_ui_setup": "Erreur lors de la configuration UI : {error}",
                    "log_error_styles": "Erreur de configuration des styles : {error}",
                    "log_error_top_frame": "Erreur de création du cadre supérieur : {error}",
                    "log_error_state_frame": "Erreur de création du cadre d'état : {error}",
                    "log_error_date_controls": "Erreur de création des contrôles de date : {error}",
                    "log_error_year_frame": "Erreur de création du cadre année : {error}",
                    "log_error_date_range_frame": "Erreur de création du cadre plage de dates : {error}",
                    "log_error_prize_headers": "Erreur de mise à jour des en-têtes de prix : {error}",
                    "log_error_participant_headers": "Erreur de mise à jour des en-têtes de participants : {error}",
                    "log_error_distribution_headers": "Erreur de mise à jour des en-têtes de distribution : {error}",
                    "log_error_history_headers": "Erreur de mise à jour des en-têtes d'historique : {error}",
                    "log_error_refreshing_tables": "Erreur d'actualisation des tableaux : {error}",
                    "log_error_sorting_table": "Erreur de tri du tableau : {error}",
                    "log_error_prize_action": "Erreur lors de l'action sur le prix : {error}",
                    "log_error_participant_action": "Erreur lors de l'action sur le participant : {error}",
                    "log_error_saving_state": "Erreur lors de l'enregistrement de l'état : {error}",
                    "log_error_loading_state": "Erreur lors du chargement de l'état : {error}",
                    "log_error_distribution_calculation": "Erreur de calcul de la distribution : {error}",
                    "log_error_changing_language": "Erreur de changement de langue : {error}",
                    "log_error_drag_drop": "Erreur lors du glisser-déposer : {error}",
                    "log_error_validation": "Erreur de validation : {error}",
                    "log_error_adding_prizes": "Erreur lors de l'ajout des prix : {error}",
                    "log_error_adding_participants": "Erreur lors de l'ajout des participants : {error}",
                    "log_error_updating_ui": "Erreur de mise à jour de l'UI : {error}",
                    "log_error_updating_distribution": "Erreur de mise à jour de la distribution : {error}",
                    "log_error_backup": "Erreur lors de la sauvegarde : {error}",
                    "log_error_restore": "Erreur lors de la restauration : {error}",
                    "log_error_preferences": "Erreur dans les préférences : {error}",
                    "log_error_saving_preferences": "Erreur d'enregistrement des préférences : {error}",
                    "log_error_applying_theme": "Erreur d'application du thème : {error}",
                    "log_error_creating_folder": "Erreur de création du dossier : {error}",
                    "log_error_month_combos": "Erreur de configuration des combos mois : {error}",
                    "log_error_day_combos": "Erreur de configuration des combos jours : {error}",
                    "log_error_date_validation": "Erreur de validation des dates : {error}",
                    "log_error_filtering_states": "Erreur de filtrage des états : {error}",
                    "log_error_saving_file": "Erreur d'enregistrement du fichier : {error}",
                    "log_error_reading_backup": "Erreur de lecture de la sauvegarde : {error}",
                    "log_error_preview": "Erreur de génération de l'aperçu : {error}",
                    "log_error_getting_preference": "Erreur de lecture de préférence : {error}",
                    "log_error_saving_preference": "Erreur d'enregistrement de préférence : {error}",
                    "log_error_centering_dialog": "Erreur de centrage de la fenêtre : {error}",
                    "log_error_language_selector": "Erreur de création du sélecteur de langue : {error}",
                    "log_error_buttons_state": "Erreur de mise à jour de l'état des boutons : {error}",
                    "log_error_quantity_validation": "Erreur de validation de la quantité : {error}",
                    "log_error_integer_distribution": "Erreur de distribution des entiers : {error}",
                    "log_error_prize_mode_toggle": "Erreur de basculement du mode prix : {error}",
                    "log_error_participant_mode_toggle": "Erreur de basculement du mode participant : {error}",
                    "log_error_parsing_prize": "Erreur d'analyse du prix : {error}",
                    "log_error_parsing_participant": "Erreur d'analyse du participant : {error}",
                    "log_error_updating_button_states": "Erreur de mise à jour des états des boutons : {error}",
                    "log_error_auto_backup": "Erreur de sauvegarde automatique : {error}",
                    "log_error_cleanup_backups": "Erreur de nettoyage des anciennes sauvegardes : {error}",
                    "log_error_loading_preferences": "Erreur de chargement des préférences : {error}",
                    "log_error_applying_preferences": "Erreur d'application des préférences : {error}",
                    "log_error_export": "Erreur lors de l'exportation : {error}",
                    "log_error_import": "Erreur lors de l'importation : {error}",
                    "log_error_name_validation": "Erreur de validation du nom : {error}",
                    "log_error_validating_winners": "Erreur de validation des gagnants : {error}",
                    "log_error_toggle_winners": "Erreur de basculement des gagnants : {error}",
                    "log_error_toggle_participant": "Erreur de basculement du participant : {error}",
                    "log_error_prize_template": "Erreur dans le modèle de prix : {error}",
                    "log_error_participant_template": "Erreur dans le modèle de participant : {error}",
                    "log_error_update_state": "Erreur de mise à jour de l'état : {error}",
                    "log_error_creating_shortcuts": "Erreur de création des raccourcis : {error}",
                    "log_error_showing_settings": "Erreur d'affichage des paramètres : {error}",
                    "log_error_showing_backup_settings": "Erreur d'affichage des paramètres de sauvegarde : {error}",
                    "log_error_showing_import_settings": "Erreur d'affichage des paramètres d'importation : {error}",
                    "log_error_creating_menus": "Erreur de création des menus : {error}",
                    "log_error_prize_menu": "Erreur dans le menu des prix : {error}",
                    "log_error_participant_menu": "Erreur dans le menu des participants : {error}",
                    "log_error_moving_item": "Erreur de déplacement de l'élément : {error}",
                    "log_error_credits": "Erreur d'affichage des crédits : {error}",
                    "log_error_restore_dialog": "Erreur dans la fenêtre de restauration : {error}",
                    "log_error_number_format": "Erreur de formatage de nombre : {error}",
                    "log_error_formatting_damages": "Erreur de formatage des dégâts : {error}",
                    "log_error_formatting_prizes": "Erreur de formatage des prix : {error}",
                    "log_error_formatting_distributions": "Erreur de formatage des distributions : {error}",
                    "log_error_dialog": "Erreur dans la fenêtre de dialogue : {error}"
                },
                "ru": {
                    #Основной Интерфейс
                    "title": "Распределение Призов",
                    "credits": "О Программе",
                    "developer": "Разработчик",
                    "donations": "Пожертвования",
                    "close": "Закрыть",
                    "settings": "Настройки",
                    "backup": "Резервное Копирование",
                    "import": "Импорт",
                    "export": "Экспорт",
                    "theme": "Тема",
                    "preferences": "Настройки",
                    "general": "Общие",
                    "display": "Отображение",

                    #Вкладки и Разделы
                    "prizes": "Призы",
                    "participants": "Участники",
                    "distribution": "Распределение",
                    "history": "История",
                    "current_state": "Текущее Состояние",
                    "load_template": "Загрузить Шаблон",
                    "filters": "Фильтры",
                    "preview": "Предпросмотр",

                    #Поля и Метки
                    "prize_name": "Название Приза",
                    "participant": "Участник",
                    "quantity": "Количество",
                    "damage": "Урон",
                    "enabled": "Включен",
                    "disabled": "Отключен",
                    "percentage": "Процент",
                    "total_damage": "Общий Урон",
                    "special_prize": "Специальный Приз",
                    "normal_prize": "Обычный Приз",
                    "winners": "Победители",
                    "top_winners": "Количество Победителей",
                    "id": "№",
                    "select_prize": "Выбрать Приз",
                    "total": "Итого",
                    "event": "Событие",
                    "distributions": "Распределения",

                    #Управление Датами
                    "year": "Год",
                    "month": "Месяц",
                    "start_date": "Дата Начала",
                    "end_date": "Дата Окончания",
                    "start_day": "День Начала",
                    "end_day": "День Окончания",
                    "use_date_range": "Использовать Диапазон Дат",
                    "date": "Дата",
                    "months": "Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь",

                    #Действия
                    "add": "Добавить",
                    "edit": "Изменить",
                    "delete": "Удалить",
                    "save": "Сохранить",
                    "cancel": "Отмена",
                    "clear": "Очистить",
                    "load": "Загрузить",
                    "toggle": "Переключить",
                    "received": "Получено",
                    "refresh": "Обновить",
                    "update_state": "Обновить Состояние",
                    "save_state": "Сохранить Состояние",
                    "update_options": "Обновить Параметры",
                    "backup_now": "Создать Резервную Копию",
                    "restore": "Восстановить",
                    "move_up": "Переместить Вверх",
                    "move_down": "Переместить Вниз",

                    #Режимы Ввода
                    "single_input": "Одиночный Ввод",
                    "batch_input": "Пакетный Ввод",
                    "integer_only": "Только Целые Числа",
                    "load_prizes": "Загрузить Призы",
                    "load_participants": "Загрузить Участников",
                    "delete_with_hash": "Используйте # для удаления элемента",
                    "batch_prize_format": "Формат: название:количество[:s:победители] - Добавьте 's:N' для специальных призов",
                    "batch_prize_example": "Пример: золотое яблоко:3:s:2 (специальный приз для 2 победителей)",
                    "batch_participant_format": "Формат: имя:урон",
                    "batch_participant_example": "Пример: mario:1000",

                    #Резервное Копирование и Импорт
                    "backup_settings": "Настройки Резервного Копирования",
                    "backup_folder": "Папка Резервных Копий",
                    "enable_auto_backup": "Включить Автоматическое Копирование",
                    "backup_interval": "Интервал Копирования",
                    "backup_retention": "Хранение Копий",
                    "keep_backups": "Сохранять Копии",
                    "select_backup": "Выбрать Копию",
                    "import_folder": "Папка Импорта",
                    "import_settings": "Настройки Импорта",
                    "import_actions": "Действия Импорта",
                    "data_folder": "Папка Данных",
                    "auto_save": "Автосохранение",
                    "default_language": "Язык по Умолчанию",
                    "font_size": "Размер Шрифта",
                    "row_height": "Высота Строк",
                    "tables": "Таблицы",

                    #Сообщения об Ошибках
                    "error": "Ошибка",
                    "info": "Информация",
                    "confirm": "Подтверждение",
                    "name_required": "Требуется имя",
                    "quantity_required": "Требуется количество",
                    "damage_required": "Требуется урон",
                    "event_required": "Требуется название события",
                    "start_month_required": "Требуется месяц начала",
                    "prizes_and_participants_required": "Требуются призы и участники",
                    "missing_separator": "Отсутствует разделитель ':'",
                    "missing_name": "Отсутствует имя",
                    "missing_value": "Отсутствует значение",
                    "missing_winners": "Отсутствует количество победителей для специального приза",
                    "invalid_winners": "Неверное количество победителей",
                    "invalid_special": "Неверный формат специального приза",
                    "invalid_quantity": "Неверное количество",
                    "invalid_damage": "Неверный урон",
                    "invalid_chars": "Недопустимые символы в имени",
                    "invalid_value": "Неверное значение",
                    "name_exists": "Имя уже существует",
                    "name_exists_msg": "Элемент с таким именем уже существует",
                    "invalid_input": "Неверный ввод",
                    "invalid_date_range": "Неверный диапазон дат",
                    "date_collision": "На эти даты уже существует событие",
                    "prize_name_too_short": "Слишком короткое название приза",
                    "prize_name_too_long": "Слишком длинное название приза",
                    "participant_name_too_short": "Слишком короткое имя участника",
                    "participant_name_too_long": "Слишком длинное имя участника",
                    "event_name_too_long": "Название события не может превышать 50 символов",
                    "state_not_found": "Состояние не найдено",
                    "state_not_found_with_dates": "Не найдено состояние с этими датами",
                    "no_elements_to_update": "Нет элементов для обновления",
                    "save_error": "Ошибка при сохранении",
                    "no_saved_states": "Нет сохраненных состояний",
                    "template_load_error": "Ошибка загрузки шаблона",
                    "export_error": "Ошибка при экспорте",
                    "import_error": "Ошибка при импорте",
                    "backup_error": "Ошибка при создании резервной копии",
                    "restore_error": "Ошибка при восстановлении",
                    "no_backup_selected": "Не выбрана резервная копия",
                    "no_backups_available": "Нет доступных резервных копий",
                    "quantity_must_be_positive": "Количество должно быть положительным",
                    "quantity_must_be_integer": "Количество должно быть целым числом",
                    "quantity_must_be_number": "Количество должно быть числом",
                    "damage_must_be_non_negative": "Урон не может быть отрицательным",
                    "damage_must_be_integer": "Урон должен быть целым числом",
                    "damage_must_be_number": "Урон должен быть числом",
                    "winners_must_be_positive": "Количество победителей должно быть положительным",
                    "winners_must_be_integer": "Количество победителей должно быть целым числом",
                    "winners_exceed_participants": "Количество победителей превышает количество участников",
                    "state_incomplete_load": "Состояние содержит незагруженные элементы. Продолжить загрузку недостающих элементов?",

                    #Подтверждения
                    "confirm_delete": "Подтвердить удаление?",
                    "confirm_delete_last_prize": "Удаление последнего приза также удалит событие. Продолжить?",
                    "confirm_delete_last_participant": "Удаление последнего участника также удалит событие. Продолжить?",
                    "confirm_delete_prize": "Вы уверены, что хотите удалить этот приз?",
                    "confirm_delete_participant": "Вы уверены, что хотите удалить этого участника?",
                    "confirm_clear_prizes": "Вы уверены, что хотите удалить все призы?",
                    "confirm_clear_participants": "Вы уверены, что хотите удалить всех участников?",
                    "confirm_update": "Вы уверены, что хотите обновить это состояние?",
                    "confirm_update_options": "Подтвердить обновление параметров?",
                    "ignore_update_options": "Пропустить изменения параметров? Изменения данных будут сохранены",
                    "cancel_all_updates": "Отменить все изменения? Ничего не будет сохранено",
                    "confirm_restore": "Вы уверены, что хотите восстановить эту копию?",
                    "confirm_new_state": "Есть несохраненные изменения. Продолжить с новым состоянием?",
                    "confirm_discard_changes": "Подтвердить отмену изменений?",

                    #Сообщения об Успехе
                    "state_saved": "Состояние успешно сохранено",
                    "state_updated": "Состояние успешно обновлено",
                    "backup_created": "Резервная копия создана",
                    "restore_completed": "Восстановление завершено",
                    "export_completed": "Экспорт завершен",
                    "preferences_saved": "Настройки сохранены",
                    "changes_saved": "Изменения сохранены",

                    #Сообщения Журнала
                    "log_app_initialized": "Приложение инициализировано",
                    "log_ui_components_initialized": "Компоненты интерфейса инициализированы",
                    "log_styles_configured": "Стили настроены",
                    "log_language_selector_created": "Создан выбор языка",
                    "log_top_frame_created": "Создана верхняя рамка",
                    "log_state_frame_created": "Создана рамка состояния",
                    "log_date_controls_created": "Созданы элементы управления датами",
                    "log_date_range_frames_setup": "Настроены рамки диапазона дат",
                    "log_month_values_updated": "Обновлены значения месяцев",
                    "log_buttons_state_updated": "Обновлено состояние кнопок",
                    "log_prize_headers_updated": "Обновлены заголовки призов",
                    "log_participant_headers_updated": "Обновлены заголовки участников",
                    "log_distribution_headers_updated": "Обновлены заголовки распределения",
                    "log_history_headers_updated": "Обновлены заголовки истории",
                    "log_tables_content_refreshed": "Обновлено содержимое таблиц",
                    "log_tables_updated": "Таблицы обновлены",
                    "log_ui_text_updated": "Текст интерфейса обновлен",
                    "log_month_combos_setup": "Настроены комбо месяцев",
                    "log_day_combos_setup": "Настроены комбо дней",
                    "log_year_frame_created": "Создана рамка года",
                    "log_date_range_frame_created": "Создана рамка диапазона дат",
                    "log_drag_started": "Начато перетаскивание",
                    "log_drag_motion": "Движение перетаскивания",
                    "log_drag_completed": "Перетаскивание завершено",
                    "log_prize_mode_toggled": "Переключен режим призов",
                    "log_participant_mode_toggled": "Переключен режим участников",
                    "log_prize_added": "Добавлен приз: {name}",
                    "log_participant_added": "Добавлен участник: {name}",
                    "log_prize_edited": "Изменен приз: {name}",
                    "log_participant_edited": "Изменен участник: {name}",
                    "log_prize_deleted": "Удален приз: {name}",
                    "log_participant_deleted": "Удален участник: {name}",
                    "log_participant_toggled": "Переключено состояние участника: {name}",
                    "log_state_saved": "Сохранено состояние: {event}",
                    "log_state_loaded": "Загружено состояние: {event}",
                    "log_distribution_calculated": "Рассчитано распределение для приза: {prize_id}",
                    "log_language_changed": "Изменен язык на: {language}",
                    "log_state_file_saved": "Сохранен файл состояния: {filename}",
                    "log_states_loaded": "Загружено состояний: {count}",
                    "log_distribution_updated": "Обновлено распределение для приза: {prize_id}",
                    "log_prize_action_handled": "Обработано действие с призом: {action}",
                    "log_participant_action_handled": "Обработано действие с участником: {action}",
                    "log_backup_created": "Создана резервная копия: {filename}",
                    "log_restore_completed": "Восстановление завершено: {filename}",
                    "log_preferences_saved": "Настройки сохранены",
                    "log_theme_applied": "Применена тема: {theme}",
                    "log_data_folder_created": "Создана папка данных",
                    "log_general_preferences_created": "Созданы общие настройки",
                    "log_display_preferences_created": "Созданы настройки отображения",
                    "log_backup_preferences_created": "Созданы настройки резервного копирования",
                    "log_auto_backup_setup": "Настроено автоматическое копирование: интервал={interval}, хранение={retention}",
                    "log_old_backup_removed": "Удалена старая копия: {file}",
                    "log_preference_saved": "Сохранена настройка: {key}",
                    "log_sorting_applied": "Применена сортировка: {column}",

                    #Ошибки Журнала
                    "log_error_ui_setup": "Ошибка настройки интерфейса: {error}",
                    "log_error_styles": "Ошибка настройки стилей: {error}",
                    "log_error_top_frame": "Ошибка создания верхней рамки: {error}",
                    "log_error_state_frame": "Ошибка создания рамки состояния: {error}",
                    "log_error_date_controls": "Ошибка создания элементов управления датами: {error}",
                    "log_error_year_frame": "Ошибка создания рамки года: {error}",
                    "log_error_date_range_frame": "Ошибка создания рамки диапазона дат: {error}",
                    "log_error_prize_headers": "Ошибка обновления заголовков призов: {error}",
                    "log_error_participant_headers": "Ошибка обновления заголовков участников: {error}",
                    "log_error_distribution_headers": "Ошибка обновления заголовков распределения: {error}",
                    "log_error_history_headers": "Ошибка обновления заголовков истории: {error}",
                    "log_error_refreshing_tables": "Ошибка обновления таблиц: {error}",
                    "log_error_sorting_table": "Ошибка сортировки таблицы: {error}",
                    "log_error_prize_action": "Ошибка обработки действия с призом: {error}",
                    "log_error_participant_action": "Ошибка обработки действия с участником: {error}",
                    "log_error_saving_state": "Ошибка сохранения состояния: {error}",
                    "log_error_loading_state": "Ошибка загрузки состояния: {error}",
                    "log_error_distribution_calculation": "Ошибка расчета распределения: {error}",
                    "log_error_changing_language": "Ошибка смены языка: {error}",
                    "log_error_drag_drop": "Ошибка перетаскивания: {error}",
                    "log_error_validation": "Ошибка проверки: {error}",
                    "log_error_adding_prizes": "Ошибка добавления призов: {error}",
                    "log_error_adding_participants": "Ошибка добавления участников: {error}",
                    "log_error_updating_ui": "Ошибка обновления интерфейса: {error}",
                    "log_error_updating_distribution": "Ошибка обновления распределения: {error}",
                    "log_error_backup": "Ошибка резервного копирования: {error}",
                    "log_error_restore": "Ошибка восстановления: {error}",
                    "log_error_preferences": "Ошибка настроек: {error}",
                    "log_error_saving_preferences": "Ошибка сохранения настроек: {error}",
                    "log_error_applying_theme": "Ошибка применения темы: {error}",
                    "log_error_creating_folder": "Ошибка создания папки: {error}",
                    "log_error_month_combos": "Ошибка настройки комбо месяцев: {error}",
                    "log_error_day_combos": "Ошибка настройки комбо дней: {error}",
                    "log_error_date_validation": "Ошибка проверки дат: {error}",
                    "log_error_filtering_states": "Ошибка фильтрации состояний: {error}",
                    "log_error_saving_file": "Ошибка сохранения файла: {error}",
                    "log_error_reading_backup": "Ошибка чтения резервной копии: {error}",
                    "log_error_preview": "Ошибка создания предпросмотра: {error}",
                    "log_error_getting_preference": "Ошибка получения настройки: {error}",
                    "log_error_saving_preference": "Ошибка сохранения настройки: {error}",
                    "log_error_centering_dialog": "Ошибка центрирования диалога: {error}",
                    "log_error_language_selector": "Ошибка создания выбора языка: {error}",
                    "log_error_buttons_state": "Ошибка обновления состояния кнопок: {error}",
                    "log_error_quantity_validation": "Ошибка проверки количества: {error}",
                    "log_error_integer_distribution": "Ошибка распределения целых чисел: {error}",
                    "log_error_prize_mode_toggle": "Ошибка переключения режима призов: {error}",
                    "log_error_participant_mode_toggle": "Ошибка переключения режима участников: {error}",
                    "log_error_parsing_prize": "Ошибка разбора приза: {error}",
                    "log_error_parsing_participant": "Ошибка разбора участника: {error}",
                    "log_error_updating_button_states": "Ошибка обновления состояний кнопок: {error}",
                    "log_error_auto_backup": "Ошибка автоматического копирования: {error}",
                    "log_error_cleanup_backups": "Ошибка очистки старых копий: {error}",
                    "log_error_loading_preferences": "Ошибка загрузки настроек: {error}",
                    "log_error_applying_preferences": "Ошибка применения настроек: {error}",
                    "log_error_export": "Ошибка экспорта: {error}",
                    "log_error_import": "Ошибка импорта: {error}",
                    "log_error_name_validation": "Ошибка проверки имени: {error}",
                    "log_error_validating_winners": "Ошибка проверки победителей: {error}",
                    "log_error_toggle_winners": "Ошибка переключения победителей: {error}",
                    "log_error_toggle_participant": "Ошибка переключения участника: {error}",
                    "log_error_prize_template": "Ошибка шаблона приза: {error}",
                    "log_error_participant_template": "Ошибка шаблона участника: {error}",
                    "log_error_update_state": "Ошибка обновления состояния: {error}",
                    "log_error_creating_shortcuts": "Ошибка создания горячих клавиш: {error}",
                    "log_error_showing_settings": "Ошибка отображения настроек: {error}",
                    "log_error_showing_backup_settings": "Ошибка отображения настроек резервного копирования: {error}",
                    "log_error_showing_import_settings": "Ошибка отображения настроек импорта: {error}",
                    "log_error_creating_menus": "Ошибка создания меню: {error}",
                    "log_error_prize_menu": "Ошибка меню призов: {error}",
                    "log_error_participant_menu": "Ошибка меню участников: {error}",
                    "log_error_moving_item": "Ошибка перемещения элемента: {error}",
                    "log_error_credits": "Ошибка отображения информации о программе: {error}",
                    "log_error_restore_dialog": "Ошибка диалога восстановления: {error}",
                    "log_error_number_format": "Ошибка форматирования числа: {error}",
                    "log_error_formatting_damages": "Ошибка форматирования урона: {error}",
                    "log_error_formatting_prizes": "Ошибка форматирования призов: {error}",
                    "log_error_formatting_distributions": "Ошибка форматирования распределений: {error}",
                    "log_error_dialog": "Ошибка диалогового окна: {error}"
                }
            }
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        """Setup del logger con rotazione file"""
        logger = logging.getLogger('PrizeDistribution')
        logger.setLevel(logging.DEBUG)
        
        handler = RotatingFileHandler(
            'prize_distribution.log',
            maxBytes=1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - [%(language)s] - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    def get_text(self, key: str, **kwargs) -> str:
        """Get translated text with optional formatting"""
        text = self.translations.get(self.current_language, {}).get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def log(self, level: str, key: str, **kwargs):
        """Log message with current language translation"""
        message = self.get_text(key, **kwargs)
        extra = {'language': self.current_language}
        
        if level == 'debug':
            self.logger.debug(message, extra=extra)
        elif level == 'info':
            self.logger.info(message, extra=extra)
        elif level == 'warning':
            self.logger.warning(message, extra=extra)
        elif level == 'error':
            self.logger.error(message, extra=extra)
        elif level == 'critical':
            self.logger.critical(message, extra=extra)

class PrizeDistributionApp:
    def __init__(self):
        """Inizializzazione dell'applicazione"""
        self.root = tk.Tk()
        
        # Flags per le lingue
        self.language_flags = {
            "it": "\U0001F1EE\U0001F1F9",  # 🇮🇹
            "en": "\U0001F1EC\U0001F1E7",  # 🇬🇧
            "fr": "\U0001F1EB\U0001F1F7",  # 🇫🇷
            "ru": "\U0001F1F7\U0001F1FA"   # 🇷🇺
        }
        
        # Manager traduzioni
        self.translation_manager = TranslationManager()
        
        # Imposta il titolo iniziale
        def center_window():
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 1400
            window_height = 900
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.root.title(self.translation_manager.get_text("title"))
        center_window() 
        
        # Inizializza strutture dati
        self.initialize_data_structures()
        
        # Inizializza componenti UI
        self.initialize_ui_components()
        
        # Setup UI
        self.setup_ui()
        
        # Carica stati salvati
        self.load_saved_states()

        # Carica preferenze
        self.load_preferences()
        
        # Setup backup automatico se abilitato
        if self.get_preference("auto_backup", True):
            interval = self.get_preference("backup_interval", 3)
            self.setup_auto_backup(interval, 10)
        
        self.translation_manager.log("info", "log_app_initialized")

    def initialize_data_structures(self):
        """Inizializzazione delle strutture dati"""
        # Liste principali
        self.prizes: List[Prize] = []
        self.participants: List[Participant] = []
        self.next_prize_id = 1
        self.next_participant_id = 1
        
        # Gestione cronologia
        self.history_year = None
        self.history_month = None
        self.history_event = None
        self.history_table = None
        
        # Stati salvati
        self.saved_states: List[SavedState] = []
        self.current_state: Optional[SavedState] = None
        self.data_folder = "saved_states"
        
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
            self.translation_manager.log("info", "log_data_folder_created")

    def initialize_ui_components(self):
        """Inizializzazione dei componenti UI"""
        # Variabili di controllo
        self.use_date_range = tk.BooleanVar(value=False)
        self.integer_only = tk.BooleanVar(value=True)
        self.is_special = tk.BooleanVar(value=False)
        
        # Frame date
        self.start_date_frame = None
        self.end_date_frame = None
        self.start_month = None
        self.start_day = None
        self.end_month = None
        self.end_day = None
        
        # Componenti principali
        self.notebook = None
        self.prize_selector = None
        self.selected_prize = None
        self.prizes_table = None
        self.participants_table = None
        self.distribution_table = None
        
        # Label e pulsanti
        self.top_winners_label = None
        self.top_winners = None
        self.total_damage_label = None
        self.clear_prizes_button = None
        self.clear_participants_button = None
        self.save_state_button = None
        self.update_state_button = None

        self.translation_manager.log("debug", "log_ui_components_initialized")

    def setup_ui(self):
        """Setup dell'interfaccia utente"""
        try:
            # Setup stili
            self.setup_styles()
            
            # Creazione componenti principali
            self.create_top_frame()
            self.create_state_frame()
            self.create_notebook()
            self.create_bottom_frame()
            self.toggle_prize_mode()
            self.toggle_participant_mode()
            
            self.translation_manager.log("info", "log_ui_setup_completed")
        except Exception as e:
            self.translation_manager.log("error", "log_error_ui_setup", error=str(e))
            messagebox.showerror(
                self.translation_manager.get_text("msg_error_title"),
                self.translation_manager.get_text("msg_error_ui_setup")
            )
            raise

    def setup_styles(self):
        """Configurazione degli stili"""
        try:
            style = ttk.Style()
            style.configure("Treeview", rowheight=30)
            style.configure("Dialog.TFrame", padding=20)
            style.configure("Dialog.TLabel", font=("TkDefaultFont", 10))
            style.configure("Dialog.TButton", padding=5)
            
            self.translation_manager.log("debug", "log_styles_configured")
        except Exception as e:
            self.translation_manager.log("error", "log_error_styles", error=str(e))
            raise

    def create_top_frame(self):
        """Creazione della barra superiore"""
        try:
            self.top_frame = ttk.Frame(self.root)
            self.top_frame.pack(fill="x", padx=5, pady=5)
            
            self.settings_button = ttk.Button(
                self.top_frame,
                text=self.translation_manager.get_text("settings"),
                command=self.show_settings
            )
            self.settings_button.pack(side="left", padx=5)
            
            # Credits
            self.credits_button = ttk.Button(
                self.top_frame,
                text=self.translation_manager.get_text("credits"),
                command=self.show_credits
            )
            self.credits_button.pack(side="left")
            
            # Language selector
            self.create_language_selector()
            
            self.translation_manager.log("debug", "log_top_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_top_frame", error=str(e))
            raise

    def create_language_selector(self):
        """Creazione del selettore lingua"""
        try:
            self.language_frame = ttk.Frame(self.top_frame)
            self.language_frame.pack(side="right", padx=5)
            
            self.language_var = tk.StringVar(value=self.translation_manager.current_language)
            
            # Popola il menu con le bandiere
            language_values = [
                f"{self.language_flags[lang]} {lang.upper()}" 
                for lang in self.language_flags.keys()
            ]
            
            self.language_menu = ttk.Combobox(
                self.language_frame,
                textvariable=self.language_var,
                values=language_values,
                state="readonly",
                width=10
            )
            self.language_menu.pack(side="right", padx=5)
            
            # Bind cambio lingua
            self.language_menu.bind(
                '<<ComboboxSelected>>', 
                lambda e: self.change_language(
                    self.language_menu.get().split()[-1].lower()
                )
            )
            
            self.translation_manager.log("debug", "log_language_selector_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_language_selector", error=str(e))
            raise

    def create_state_frame(self):
        """Creazione del frame di gestione stato"""
        try:
            self.state_frame = ttk.Frame(self.root)
            self.state_frame.pack(fill="x", padx=5, pady=5)
            
            # Frame stato corrente
            self.current_state_frame = ttk.LabelFrame(
                self.state_frame,
                text=self.translation_manager.get_text("current_state")
            )
            self.current_state_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            # Creazione controlli
            self.create_date_controls()
            self.create_event_controls()
            self.create_template_frame()
            
            self.translation_manager.log("debug", "log_state_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_state_frame", error=str(e))
            raise

    def create_date_controls(self):
        """Creazione dei controlli per le date"""
        try:
            # Frame anno
            self.create_year_frame()
            
            # Frame date
            self.create_date_range_frame()
            
            # Setup frames per intervallo date
            self.setup_date_range_frames()
            
            self.translation_manager.log("debug", "log_date_controls_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_date_controls", error=str(e))
            raise

    def create_year_frame(self):
        """Creazione del frame anno"""
        try:
            self.year_frame = ttk.Frame(self.current_state_frame)
            self.year_frame.pack(fill="x", padx=5, pady=2)
            
            # Label anno
            self.year_label = ttk.Label(
                self.year_frame,
                text=self.translation_manager.get_text("year")
            )
            self.year_label.pack(side="left", padx=5)
            
            # Combobox anno
            current_year = datetime.now().year
            self.year_var = tk.StringVar(value=str(current_year))
            
            years = [str(year) for year in range(2020, current_year + 2)]
            self.year_combo = ttk.Combobox(
                self.year_frame,
                textvariable=self.year_var,
                values=years,
                width=6,
                state="readonly"
            )
            self.year_combo.pack(side="left", padx=5)
            
            # Bind per aggiornamento giorni
            self.year_combo.bind('<<ComboboxSelected>>', self.update_days)
            
            self.translation_manager.log("debug", "log_year_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_year_frame", error=str(e))
            raise

    def create_date_range_frame(self):
        """Creazione del frame intervallo date"""
        try:
            self.date_frame = ttk.Frame(self.current_state_frame)
            self.date_frame.pack(fill="x", padx=5, pady=2)
            
            # Checkbox uso intervallo
            self.use_date_range_check = ttk.Checkbutton(
                self.date_frame,
                text=self.translation_manager.get_text("use_date_range"),
                variable=self.use_date_range,
                command=self.toggle_date_range
            )
            self.use_date_range_check.pack(side="left", padx=5)
            
            self.translation_manager.log("debug", "log_date_range_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_date_range_frame", error=str(e))
            raise

    def setup_date_range_frames(self):
        """Setup dei frame per l'intervallo date"""
        try:
            # Frame data inizio
            self.start_date_frame = ttk.Frame(self.date_frame)
            self.start_date_label = ttk.Label(
                self.start_date_frame,
                text=self.translation_manager.get_text("start_date")
            )
            self.start_date_label.pack(side="left", padx=5)
            
            # Frame data fine
            self.end_date_frame = ttk.Frame(self.date_frame)
            self.end_date_label = ttk.Label(
                self.end_date_frame,
                text=self.translation_manager.get_text("end_date")
            )
            self.end_date_label.pack(side="left", padx=5)
            
            # Setup combobox mesi
            self.setup_month_combos()
            
            # Setup combobox giorni
            self.setup_day_combos()
            
            self.translation_manager.log("debug", "log_date_range_frames_setup")
        except Exception as e:
            self.translation_manager.log("error", "log_error_date_range_frames", error=str(e))
            raise

    def setup_month_combos(self):
        """Setup delle combo box per i mesi"""
        try:
            # Ottieni lista mesi tradotta
            months = [(f"{i:02d}", nome) for i, nome in
                     enumerate(self.translation_manager.get_text("months").split(","), 1)]
            month_values = [''] + [f"{m[0]} - {m[1]}" for m in months]
            
            # Combo mese inizio
            month_values = [''] + [f"{i:02d}" for i in range(1, 13)]
            self.start_month = ttk.Combobox(
                self.start_date_frame,
                values=month_values,
                state="readonly",
                width=15
            )
            self.start_month.pack(side="left", padx=5)
            
            # Combo mese fine
            self.end_month = ttk.Combobox(
                self.end_date_frame,
                values=month_values,
                width=15,
                state="readonly"
            )
            self.end_month.pack(side="left", padx=5)
            
            # Bind eventi
            self.start_month.bind('<<ComboboxSelected>>', self.update_days)
            self.end_month.bind('<<ComboboxSelected>>', self.update_days)
            
            self.translation_manager.log("debug", "log_month_combos_setup")
        except Exception as e:
            self.translation_manager.log("error", "log_error_month_combos", error=str(e))
            raise

    def setup_day_combos(self):
        """Setup delle combo box per i giorni"""
        try:
            # Combo giorno inizio
            self.start_day = ttk.Combobox(
                self.start_date_frame,
                width=3,
                state="readonly"
            )
            self.start_day.pack(side="left", padx=5)
            
            # Combo giorno fine
            self.end_day = ttk.Combobox(
                self.end_date_frame,
                width=3,
                state="readonly"
            )
            self.end_day.pack(side="left", padx=5)
            
            self.translation_manager.log("debug", "log_day_combos_setup")
        except Exception as e:
            self.translation_manager.log("error", "log_error_day_combos", error=str(e))
            raise

    def create_event_controls(self):
        """Creazione dei controlli per l'evento"""
        try:
            self.event_frame = ttk.Frame(self.current_state_frame)
            self.event_frame.pack(fill="x", padx=5, pady=2)
            
            # Label evento
            self.event_label = ttk.Label(
                self.event_frame,
                text=self.translation_manager.get_text("event")
            )
            self.event_label.pack(side="left", padx=5)
            
            # Entry evento
            self.event_var = tk.StringVar()
            self.event_var.trace_add("write", self.validate_event_name)
            
            self.event_entry = ttk.Entry(
                self.event_frame,
                textvariable=self.event_var,
                validate="key",
                validatecommand=(self.root.register(self.validate_event_name), '%d', '%s', '%P')
            )
            self.event_entry.pack(side="left", fill="x", expand=True, padx=5)
            
            
            self.translation_manager.log("debug", "log_event_controls_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_event_controls", error=str(e))
            raise

    def create_total_damage_label(self):
        """Creazione label danni totali"""
        try:
            self.total_damage_label = ttk.Label(
                self.event_frame,
                text=f"{self.translation_manager.get_text('total_damage')}: 0"
            )
            self.total_damage_label.pack(side="right", padx=5)
            
            self.translation_manager.log("debug", "log_damage_label_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_damage_label", error=str(e))
            raise

    def create_template_frame(self):
        """Creazione del frame template"""
        try:
            self.template_frame = ttk.LabelFrame(
                self.state_frame,
                text=self.translation_manager.get_text("load_template")
            )
            self.template_frame.pack(side="right", fill="x", padx=5)
            
            # Pulsante carica premi
            self.load_prizes_button = ttk.Button(
                self.template_frame,
                text=self.translation_manager.get_text("load_prizes"),
                command=self.load_prizes_template
            )
            self.load_prizes_button.pack(side="left", padx=5, pady=5)
            
            # Pulsante carica partecipanti
            self.load_participants_button = ttk.Button(
                self.template_frame,
                text=self.translation_manager.get_text("load_participants"),
                command=self.load_participants_template
            )
            self.load_participants_button.pack(side="left", padx=5, pady=5)
            
            self.translation_manager.log("debug", "log_template_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_template_frame", error=str(e))
            raise

    def validate_event_name(self, action, text_before, text_after) -> bool:
        """Validazione nome evento"""
        if not text_after or len(text_after) <= 50:  # lunghezza massima 50 caratteri
            return True
        messagebox.showerror(
            self.translation_manager.get_text("error"),
            self.translation_manager.get_text("event_name_too_long")
        )
        return False

    def check_save_buttons_state(self):
        """Controllo dello stato dei pulsanti di salvataggio"""
        try:
            # Per il pulsante aggiorna, basta almeno un elemento in una tabella
            has_any_content = bool(self.prizes or self.participants)
            self.update_state_button["state"] = "normal" if has_any_content else "disabled"
            
            # Per il pulsante salva, servono elementi in entrambe le tabelle
            has_both_content = bool(self.prizes and self.participants)
            self.save_state_button["state"] = "normal" if has_both_content else "disabled"
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_buttons_state", error=str(e))
                
            self.translation_manager.log("debug", "log_buttons_state_updated")

        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_button_state",
                error=str(e)
            )
            raise

    def toggle_date_range(self):
        """Toggle della visibilità dei frame delle date"""
        try:
            if self.use_date_range.get():
                self.start_date_frame.pack(side="left", fill="x", expand=True)
                self.end_date_frame.pack(side="left", fill="x", expand=True)
            else:
                self.start_date_frame.pack_forget()
                self.end_date_frame.pack_forget()
                # Pulisce le selezioni delle date
                self.start_month.set('')
                self.start_day.set('')
                self.end_month.set('')
                self.end_day.set('')
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_toggle_date_range", error=str(e))

    def update_days(self, *args):
        """Aggiornamento giorni disponibili nelle combo"""
        try:
            year = int(self.year_var.get())
            
            # Opzione vuota per deselezionare
            empty_option = ['']
            
            # Aggiorna giorni inizio
            start_month_val = self.start_month.get()
            if start_month_val and ' - ' in start_month_val:
                month = int(start_month_val.split(' - ')[0])
                _, last_day = monthrange(year, month)
                days = [str(d).zfill(2) for d in range(1, last_day + 1)]
                self.start_day['values'] = empty_option + days
                if self.start_day.get() not in (empty_option + days):
                    self.start_day.set('')
            else:
                self.start_day['values'] = empty_option
                self.start_day.set('')
            
            # Aggiorna giorni fine
            end_month_val = self.end_month.get()
            if end_month_val and ' - ' in end_month_val:
                month = int(end_month_val.split(' - ')[0])
                _, last_day = monthrange(year, month)
                days = [str(d).zfill(2) for d in range(1, last_day + 1)]
                self.end_day['values'] = empty_option + days
                if self.end_day.get() not in (empty_option + days):
                    self.end_day.set('')
            else:
                self.end_day['values'] = empty_option
                self.end_day.set('')
                
        except ValueError:
            pass

    def change_language(self, new_language):
        """Gestione cambio lingua"""
        try:
            if new_language in self.language_flags:
                # Imposta la lingua nel translation manager
                self.translation_manager.current_language = new_language
                
                # Aggiorna mesi nelle combo con le nuove traduzioni
                months = [(f"{i:02d}", nome) for i, nome in 
                        enumerate(self.translation_manager.get_text("months").split(","), 1)]
                month_values = [''] + [f"{m[0]} - {m[1]}" for m in months]
                
                # Aggiorna combo mantenendo selezione
                for combo in [self.start_month, self.end_month]:
                    current = combo.get()
                    if current and ' - ' in current:
                        month_num = current.split(' - ')[0]
                        combo['values'] = month_values
                        # Trova e imposta il valore corrispondente nella nuova lingua
                        for val in month_values:
                            if val.startswith(month_num):
                                combo.set(val)
                                break
                    else:
                        combo['values'] = month_values
                        combo.set('')
                
                # Forza l'aggiornamento di tutte le UI
                self.update_ui_text()
                self.update_tables()
                
                self.translation_manager.log(
                    "debug",
                    "log_language_changed",
                    language=new_language
                )
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_changing_language", error=str(e))

    def toggle_prize_mode(self, *args):
        """Toggle tra input singolo e multiplo per premi"""
        try:
            for frame in [self.single_prize_frame, self.batch_prize_frame]:
                frame.pack_forget()
                
            if self.prize_input_mode.get() == "single":
                self.single_prize_frame.pack(fill="x", expand=True)
                self.special_prize_frame.pack(side="left", padx=5)
            else:
                self.batch_prize_frame.pack(fill="x", expand=True)
                self.special_prize_frame.pack_forget()
                
            self.translation_manager.log("debug", "log_prize_mode_toggled")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_mode_toggle", error=str(e))

    def load_prizes_template(self):
        """Caricamento template premi"""
        try:
            if not self.saved_states:
                messagebox.showinfo(
                    self.translation_manager.get_text("info"),
                    self.translation_manager.get_text("no_saved_states")
                )
                return
                
            # Carica la finestra di dialogo per selezionare lo stato
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("load_template"))
            dialog.geometry("400x300")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            # Lista degli stati
            listbox = tk.Listbox(dialog)
            listbox.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Popola la lista
            for state in self.saved_states:
                listbox.insert(tk.END, f"{state.date_range} - {state.event}")
            
            def load_selected():
                selection = listbox.curselection()
                if not selection:
                    return
                
                state = self.saved_states[selection[0]]
                text = "\n".join([
                    f"{prize.name}:"
                    for prize in state.prizes
                ])
                
                self.prize_input_mode.set("batch")
                self.prize_text.delete("1.0", tk.END)
                self.prize_text.insert("1.0", text)
                dialog.destroy()

                # Sposta alla tab premi
                self.notebook.select(0)
                
            # Pulsanti
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Button(
                button_frame, 
                text=self.translation_manager.get_text("load"),
                command=load_selected
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            ).pack(side="right", padx=5)
                
            self.translation_manager.log("info", "log_prize_template_loaded")
            
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_prize_template",
                error=f"Detailed error: {str(e)}\n{traceback.format_exc()}"
            )
            print(f"Error loading prize template: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror(
                self.translation_manager.get_text("error"),
                self.translation_manager.get_text("template_load_error")
            )

    def load_participants_template(self):
        """Caricamento template partecipanti"""
        try:
            if not self.saved_states:
                messagebox.showinfo(
                    self.translation_manager.get_text("info"),
                    self.translation_manager.get_text("no_saved_states")
                )
                return
                
            # Carica la finestra di dialogo per selezionare lo stato
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("load_template"))
            dialog.geometry("400x300")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            # Lista degli stati
            listbox = tk.Listbox(dialog)
            listbox.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Popola la lista
            for state in self.saved_states:
                listbox.insert(tk.END, f"{state.date_range} - {state.event}")
            
            def load_selected():
                selection = listbox.curselection()
                if not selection:
                    return
                
                state = self.saved_states[selection[0]]
                text = "\n".join([
                    f"{participant.name}:"
                    for participant in state.participants
                ])
                
                self.participant_input_mode.set("batch")
                self.participant_text.delete("1.0", tk.END)
                self.participant_text.insert("1.0", text)
                dialog.destroy()

                # Sposta alla tab partecipanti
                self.notebook.select(1)
                
            # Pulsanti
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill="x", padx=5, pady=5)
            
            ttk.Button(
                button_frame, 
                text=self.translation_manager.get_text("load"),
                command=load_selected
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            ).pack(side="right", padx=5)
                
            self.translation_manager.log("info", "log_participant_template_loaded")
            
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_participant_template",
                error=f"Detailed error: {str(e)}\n{traceback.format_exc()}"
            )
            print(f"Error loading participant template: {str(e)}")
            print(traceback.format_exc())
            messagebox.showerror(
                self.translation_manager.get_text("error"),
                self.translation_manager.get_text("template_load_error")
            )

    def create_notebook(self):
        """Creazione del notebook principale"""
        try:
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
                    
            # Setup delle tab
            self.setup_prizes_tab()
            self.setup_participants_tab()
            self.setup_distribution_tab()
            self.setup_history_tab()
                    
            # Bind cambio tab
            self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)
                    
            self.translation_manager.log("info", "log_notebook_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_notebook", error=str(e))
            raise

    def setup_prizes_tab(self):
        """Setup della tab premi"""
        try:
            # Frame principale
            self.prizes_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                self.prizes_frame,
                text=self.translation_manager.get_text("prizes")
            )
            
            # Frame input premi
            self.create_prize_input_frame()
            
            # Tabella premi
            self.create_prizes_table()

            #tasto aggiungi
            self.prize_name_entry.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            self.prize_quantity_entry.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            self.prize_text.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            
            self.translation_manager.log("debug", "log_prizes_tab_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prizes_tab", error=str(e))
            raise

    def create_prize_input_frame(self):
        """Creazione del frame di input premi"""
        try:
            self.prize_input_frame = ttk.LabelFrame(self.prizes_frame)
            self.prize_input_frame.pack(fill="x", padx=5, pady=5)
            
            # Modalità input
            self.create_prize_input_mode()
            
            # Container input
            self.prize_input_container = ttk.Frame(self.prize_input_frame)
            self.prize_input_container.pack(fill="x", padx=5, pady=5)
            
            # Frame input singolo e multiplo
            self.create_single_prize_frame()
            self.create_batch_prize_frame()
            
            # Frame pulsanti
            self.create_prize_buttons()
            
            # Bind modalità input
            self.prize_input_mode.trace_add("write", self.toggle_prize_mode)
            
            self.translation_manager.log("debug", "log_prize_input_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_input_frame", error=str(e))
            raise

    def create_prize_input_mode(self):
        """Creazione dei controlli modalità input premi"""
        try:
            self.prize_mode_frame = ttk.Frame(self.prize_input_frame)
            self.prize_mode_frame.pack(fill="x", padx=5, pady=5)
            
            self.prize_input_mode = tk.StringVar(value="single")
            
            # Radio input singolo
            self.single_input_radio = ttk.Radiobutton(
                self.prize_mode_frame,
                text=self.translation_manager.get_text("single_input"),
                variable=self.prize_input_mode,
                value="single"
            )
            self.single_input_radio.pack(side="left", padx=5)
            
            # Radio input multiplo
            self.batch_input_radio = ttk.Radiobutton(
                self.prize_mode_frame,
                text=self.translation_manager.get_text("batch_input"),
                variable=self.prize_input_mode,
                value="batch"
            )
            self.batch_input_radio.pack(side="left", padx=5)

            # Label informativa
            self.prize_delete_info = ttk.Label(
                self.prize_mode_frame,
                text=self.translation_manager.get_text("delete_with_hash"),
                font=("TkDefaultFont", 9, "italic")
            )
            self.prize_delete_info.pack(side="left", padx=10)
            
            self.translation_manager.log("debug", "log_prize_input_mode_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_input_mode", error=str(e))
            raise

    def create_single_prize_frame(self):
        """Creazione frame input premio singolo"""
        try:
            self.single_prize_frame = ttk.Frame(self.prize_input_container)
            
            # Nome premio
            self.prize_name_label = ttk.Label(
                self.single_prize_frame,
                text=self.translation_manager.get_text("prize_name")
            )
            self.prize_name_label.pack(side="left", padx=5)
            
            self.prize_name_entry = ttk.Entry(
                self.single_prize_frame,
                width=20,
                validate="key",
                validatecommand=(self.root.register(
                    lambda action, prev, new: self.validate_prize_name(action, prev, new)
                ), '%d', '%s', '%P')
            )
            self.prize_name_entry.pack(side="left", padx=5)
            
            # Quantità
            self.quantity_label = ttk.Label(
                self.single_prize_frame,
                text=self.translation_manager.get_text("quantity")
            )
            self.quantity_label.pack(side="left", padx=5)
            
            self.prize_quantity_entry = ttk.Entry(
                self.single_prize_frame,
                width=10,
                validate="key",
                validatecommand=(self.root.register(
                    lambda action, prev, new: self.validate_quantity(action, prev, new)
                ), '%d', '%s', '%P')
            )
            self.prize_quantity_entry.pack(side="left", padx=5)
            
            # Premio speciale
            self.create_special_prize_frame()
            
            self.translation_manager.log("debug", "log_single_prize_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_single_prize_frame", error=str(e))
            raise

    def create_special_prize_frame(self):
        """Creazione frame premio speciale"""
        try:
            self.special_prize_frame = ttk.Frame(self.single_prize_frame)
            self.special_prize_frame.pack(side="left", padx=5)
            
            self.is_special = tk.BooleanVar()
            self.special_prize_check = ttk.Checkbutton(
                self.special_prize_frame,
                text=self.translation_manager.get_text("special_prize"),
                variable=self.is_special,
                command=self.toggle_top_winners
            )
            self.special_prize_check.pack(side="left", padx=5)
            
            self.top_winners_label = ttk.Label(
                self.special_prize_frame,
                text=self.translation_manager.get_text("top_winners")
            )
            
            self.top_winners = ttk.Entry(
                self.special_prize_frame,
                width=5,
                validate="key",
                validatecommand=(self.root.register(self.validate_winners), '%P')
            )
            self.top_winners.insert(0, "1")
            
            self.translation_manager.log("debug", "log_special_prize_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_special_prize_frame", error=str(e))
            raise

    def create_batch_prize_frame(self):
        """Creazione frame input premi multipli"""
        try:
            self.batch_prize_frame = ttk.Frame(self.prize_input_container)
            
            # Area testo
            self.prize_text = tk.Text(self.batch_prize_frame, height=5)
            self.prize_text.pack(fill="x", padx=5, pady=5)
            
            # Frame formato
            self.format_frame = ttk.Frame(self.batch_prize_frame)
            self.format_frame.pack(fill="x", padx=5)
            
            # Etichette formato
            self.batch_format_label = ttk.Label(
                self.format_frame,
                text=self.translation_manager.get_text("batch_prize_format"),
                wraplength=400
            )
            self.batch_format_label.pack(pady=2)
            
            self.batch_example_label = ttk.Label(
                self.format_frame,
                text=self.translation_manager.get_text("batch_prize_example"),
                font=("TkDefaultFont", 9, "italic"),
                wraplength=400
            )
            self.batch_example_label.pack(pady=2)
            
            self.translation_manager.log("debug", "log_batch_prize_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_batch_prize_frame", error=str(e))
            raise

    def create_prize_buttons(self):
        """Creazione pulsanti gestione premi"""
        try:
            self.button_frame = ttk.Frame(self.prize_input_frame)
            self.button_frame.pack(fill="x", padx=5, pady=5)
            
            # Pulsante pulizia
            self.clear_prizes_button = ttk.Button(
                self.button_frame,
                text=self.translation_manager.get_text("clear"),
                command=self.clear_prizes,
                state="disabled"
            )
            self.clear_prizes_button.pack(side="left", padx=5)
            
            # Pulsante aggiungi
            self.add_prizes_button = ttk.Button(
                self.button_frame,
                text=self.translation_manager.get_text("add"),
                command=self.add_prizes,
                state="disabled"
            )
            self.add_prizes_button.pack(side="left", padx=5)
            
            self.translation_manager.log("debug", "log_prize_buttons_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_buttons", error=str(e))
            raise

    def create_prizes_table(self):
        """Creazione tabella premi"""
        try:
            self.table_frame = ttk.Frame(self.prizes_frame)
            self.table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Creazione tabella
            self.prizes_table = ttk.Treeview(
                self.table_frame,
                columns=("id", "name", "quantity", "special", "winners", "edit", "delete"),
                show="headings",
                height=10
            )
            
            # Scrollbar
            self.prizes_scrollbar = ttk.Scrollbar(
                self.table_frame,
                orient="vertical",
                command=self.prizes_table.yview
            )
            self.prizes_table.configure(yscrollcommand=self.prizes_scrollbar.set)
            
            self.prizes_table.pack(side="left", fill="both", expand=True)
            self.prizes_scrollbar.pack(side="right", fill="y")
            
            # Configurazione colonne
            columns = [
                ("id", self.translation_manager.get_text("id"), 50, "center"),
                ("name", self.translation_manager.get_text("prize_name"), 200, "center"),
                ("quantity", self.translation_manager.get_text("quantity"), 100, "center"),
                ("special", self.translation_manager.get_text("special_prize"), 100, "center"),
                ("winners", self.translation_manager.get_text("winners"), 100, "center"),
                ("edit", self.translation_manager.get_text("edit"), 50, "center"),
                ("delete", self.translation_manager.get_text("delete"), 50, "center")
            ]
            
            for col, heading, width, anchor in columns:
                self.prizes_table.column(col, width=width, anchor=anchor)
                self.prizes_table.heading(
                    col,
                    text=heading,
                    command=lambda c=col: self.sort_table(self.prizes_table, c, False)
                )
            
            # Bind eventi
            self.prizes_table.bind('<ButtonRelease-1>', self.handle_prize_action)
            self.prizes_table.tag_configure("center", anchor="center")
            
            self.translation_manager.log("debug", "log_prizes_table_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prizes_table", error=str(e))
            raise

    def setup_participants_tab(self):
        """Setup della tab partecipanti"""
        try:
            self.participants_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                self.participants_frame,
                text=self.translation_manager.get_text("participants")
            )
            
            # Frame input partecipanti
            self.create_participant_input_frame()
            
            # Tabella partecipanti
            self.create_participants_table()

            #tasto aggiungi
            self.participant_name_entry.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            self.participant_damage_entry.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            self.participant_text.bind('<KeyRelease>', lambda e: self.update_add_button_states())
            
            self.translation_manager.log("debug", "log_participants_tab_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_participants_tab", error=str(e))
            raise

    def create_participant_input_frame(self):
        """Creazione del frame di input partecipanti"""
        try:
            self.participant_input_frame = ttk.LabelFrame(self.participants_frame)
            self.participant_input_frame.pack(fill="x", padx=5, pady=5)
            
            # Modalità input
            self.create_participant_input_mode()
            
            # Container input
            self.participant_input_container = ttk.Frame(self.participant_input_frame)
            self.participant_input_container.pack(fill="x", padx=5, pady=5)
            
            # Frame input singolo e multiplo
            self.create_single_participant_frame()
            self.create_batch_participant_frame()
            
            # Frame pulsanti
            self.create_participant_buttons()
            
            # Bind modalità input
            self.participant_input_mode.trace_add("write", self.toggle_participant_mode)
            
            self.translation_manager.log("debug", "log_participant_input_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_participant_input_frame", error=str(e))
            raise

    def create_participant_input_mode(self):
        """Creazione dei controlli modalità input partecipanti"""
        try:
            self.p_mode_frame = ttk.Frame(self.participant_input_frame)
            self.p_mode_frame.pack(fill="x", padx=5, pady=5)
            
            self.participant_input_mode = tk.StringVar(value="single")
            
            # Radio input singolo
            self.single_participant_radio = ttk.Radiobutton(
                self.p_mode_frame,
                text=self.translation_manager.get_text("single_input"),
                variable=self.participant_input_mode,
                value="single"
            )
            self.single_participant_radio.pack(side="left", padx=5)
            
            # Radio input multiplo
            self.batch_participant_radio = ttk.Radiobutton(
                self.p_mode_frame,
                text=self.translation_manager.get_text("batch_input"),
                variable=self.participant_input_mode,
                value="batch"
            )
            self.batch_participant_radio.pack(side="left", padx=5)

            # Label informativa
            self.participant_delete_info = ttk.Label(
                self.p_mode_frame,
                text=self.translation_manager.get_text("delete_with_hash"),
                font=("TkDefaultFont", 9, "italic")
            )
            self.participant_delete_info.pack(side="left", padx=10)
            
            self.translation_manager.log("debug", "log_participant_input_mode_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_participant_input_mode", error=str(e))
            raise

    def create_single_participant_frame(self):
        """Creazione frame input partecipante singolo"""
        try:
            self.single_participant_frame = ttk.Frame(self.participant_input_container)
            
            # Nome partecipante
            self.participant_label = ttk.Label(
                self.single_participant_frame,
                text=self.translation_manager.get_text("participant")
            )
            self.participant_label.pack(side="left", padx=5)
            
            self.participant_name_entry = ttk.Entry(
            self.single_participant_frame,
            width=20,
            validate="key",
            validatecommand=(self.root.register(
                    lambda action, prev, new: self.validate_participant_name(action, prev, new)
                ), '%d', '%s', '%P')
            )
            self.participant_name_entry.pack(side="left", padx=5)
            
            # Danni
            self.damage_label = ttk.Label(
                self.single_participant_frame,
                text=self.translation_manager.get_text("damage")
            )
            self.damage_label.pack(side="left", padx=5)
            
            self.participant_damage_entry = ttk.Entry(
                self.single_participant_frame,
                width=10,
                validate="key",
                validatecommand=(self.root.register(
                    lambda action, prev, new: self.validate_damage(action, prev, new)
                ), '%d', '%s', '%P')
            )
            self.participant_damage_entry.pack(side="left", padx=5)
            
            # Abilitato
            self.enabled_var = tk.BooleanVar(value=True)
            self.enabled_check = ttk.Checkbutton(
                self.single_participant_frame,
                text=self.translation_manager.get_text("enabled"),
                variable=self.enabled_var
            )
            self.enabled_check.pack(side="left", padx=5)
            
            self.translation_manager.log("debug", "log_single_participant_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_single_participant_frame", error=str(e))
            raise

    def create_batch_participant_frame(self):
        """Creazione frame input partecipanti multipli"""
        try:
            self.batch_participant_frame = ttk.Frame(self.participant_input_container)
            
            # Area testo
            self.participant_text = tk.Text(self.batch_participant_frame, height=5)
            self.participant_text.pack(fill="x", padx=5, pady=5)
            
            # Frame formato
            self.participant_format_frame = ttk.Frame(self.batch_participant_frame)
            self.participant_format_frame.pack(fill="x", padx=5)
            
            # Etichette formato
            self.participant_format_label = ttk.Label(
                self.participant_format_frame,
                text=self.translation_manager.get_text("batch_participant_format"),
                wraplength=400
            )
            self.participant_format_label.pack(pady=2)
            
            self.participant_example_label = ttk.Label(
                self.participant_format_frame,
                text=self.translation_manager.get_text("batch_participant_example"),
                font=("TkDefaultFont", 9, "italic"),
                wraplength=400
            )
            self.participant_example_label.pack(pady=2)
            
            self.translation_manager.log("debug", "log_batch_participant_frame_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_batch_participant_frame", error=str(e))
            raise

    def create_participant_buttons(self):
        """Creazione pulsanti gestione partecipanti"""
        try:
            self.participant_button_frame = ttk.Frame(self.participant_input_frame)
            self.participant_button_frame.pack(fill="x", padx=5, pady=5)
            
            # Pulsante pulizia
            self.clear_participants_button = ttk.Button(
                self.participant_button_frame,
                text=self.translation_manager.get_text("clear"),
                command=self.clear_participants,
                state="disabled"
            )
            self.clear_participants_button.pack(side="left", padx=5)
            
            # Pulsante aggiungi
            self.add_participant_button = ttk.Button(
                self.participant_button_frame,
                text=self.translation_manager.get_text("add"),
                command=self.add_participants,
                state="disabled"
            )
            self.add_participant_button.pack(side="left", padx=5)
            
            self.translation_manager.log("debug", "log_participant_buttons_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_participant_buttons", error=str(e))
            raise

    def create_participants_table(self):
        """Creazione tabella partecipanti"""
        try:
            table_frame = ttk.Frame(self.participants_frame)
            table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Creazione tabella
            self.participants_table = ttk.Treeview(
                table_frame,
                columns=("id", "name", "damage", "percentage", "enabled", "edit", "delete", "toggle"),
                show="headings",
                height=10
            )
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=self.participants_table.yview
            )
            self.participants_table.configure(yscrollcommand=scrollbar.set)
            
            self.participants_table.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurazione colonne
            columns = [
                ("id", self.translation_manager.get_text("id"), 50, "center"),
                ("name", self.translation_manager.get_text("participant"), 200, "center"),
                ("damage", self.translation_manager.get_text("damage"), 100, "center"),
                ("percentage", self.translation_manager.get_text("percentage"), 100, "center"),
                ("enabled", self.translation_manager.get_text("enabled"), 100, "center"),
                ("edit", self.translation_manager.get_text("edit"), 50, "center"),
                ("delete", self.translation_manager.get_text("delete"), 50, "center"),
                ("toggle", self.translation_manager.get_text("toggle"), 50, "center")
            ]
            
            for col, heading, width, anchor in columns:
                self.participants_table.column(col, width=width, anchor=anchor)
                self.participants_table.heading(
                    col,
                    text=heading,
                    command=lambda c=col: self.sort_table(self.participants_table, c, False)
                )
            
            # Bind eventi
            self.participants_table.bind('<ButtonRelease-1>', self.handle_participant_action)
            self.participants_table.tag_configure("center", anchor="center")
            
            self.translation_manager.log("debug", "log_participants_table_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_participants_table", error=str(e))
            raise

    def handle_participant_action(self, event):
        """Gestione delle azioni sulla tabella partecipanti"""
        try:
            region = self.participants_table.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            row_id = self.participants_table.identify_row(event.y)
            col_id = self.participants_table.identify_column(event.x)
            
            if not row_id or not col_id:
                return
                
            values = self.participants_table.item(row_id)['values']
            if not values:
                return
                
            participant_id = values[0]
            
            if col_id == "#6":  # edit
                self.edit_participant(participant_id)
            elif col_id == "#7":  # delete
                self.delete_participant(participant_id)
            elif col_id == "#8":  # toggle
                self.toggle_participant(participant_id)
                
            self.translation_manager.log(
                "debug",
                "log_participant_action_handled",
                action=col_id,
                participant_id=participant_id
            )
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_participant_action",
                error=str(e)
            )
            raise

    def toggle_participant_mode(self, *args):
        """Toggle tra input singolo e multiplo per partecipanti"""
        try:
            for frame in [self.single_participant_frame, self.batch_participant_frame]:
                frame.pack_forget()
                
            if self.participant_input_mode.get() == "single":
                self.single_participant_frame.pack(fill="x", expand=True)
            else:
                self.batch_participant_frame.pack(fill="x", expand=True)
                
            self.translation_manager.log(
                "debug",
                "log_participant_mode_toggled",
                mode=self.participant_input_mode.get()
            )
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_participant_mode_toggle",
                error=str(e)
            )
            raise

    def setup_distribution_tab(self):
        """Setup della tab distribuzione"""
        try:
            self.distribution_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                self.distribution_frame,
                text=self.translation_manager.get_text("distribution")
            )
            
            # Controlli distribuzione
            self.create_distribution_controls()
            
            # Tabella distribuzione
            self.create_distribution_table()
            
            self.translation_manager.log("debug", "log_distribution_tab_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_distribution_tab", error=str(e))
            raise

    def create_distribution_controls(self):
        """Creazione controlli distribuzione"""
        try:
            self.distribution_controls = ttk.Frame(self.distribution_frame)
            self.distribution_controls.pack(fill="x", padx=5, pady=5)
            
            # Frame selettore premio
            self.prize_selector_frame = ttk.Frame(self.distribution_controls)
            self.select_prize_label = ttk.Label(
                self.prize_selector_frame,
                text=self.translation_manager.get_text("select_prize")
            )
            self.select_prize_label.pack(side="left", padx=5)
            
            # Combo selettore premio
            self.selected_prize = tk.StringVar()
            self.prize_selector = ttk.Combobox(
                self.prize_selector_frame,
                textvariable=self.selected_prize,
                state="readonly",
                width=30
            )
            self.prize_selector.pack(side="left", padx=5)
            
            # Bind aggiornamento distribuzione
            self.prize_selector.bind(
                '<<ComboboxSelected>>',
                lambda e: self.update_distribution()
            )
            
            # Checkbox numeri interi
            self.integer_only_check = ttk.Checkbutton(
                self.distribution_controls,
                text=self.translation_manager.get_text("integer_only"),
                variable=self.integer_only,
                command=self.update_distribution
            )
            self.integer_only_check.pack(side="right", padx=5)
            
            self.translation_manager.log("debug", "log_distribution_controls_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_distribution_controls", error=str(e))
            raise

    def create_distribution_table(self):
        """Creazione tabella distribuzione"""
        try:
            self.distribution_checks = []   # Array per mantenere lo stato dei check

            table_frame = ttk.Frame(self.distribution_frame)
            table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Creazione tabella
            self.distribution_table = ttk.Treeview(
                table_frame,
                columns=("id", "participant", "quantity", "check"),
                show="headings",
                height=15
            )
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=self.distribution_table.yview
            )
            self.distribution_table.configure(yscrollcommand=scrollbar.set)
            
            self.distribution_table.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Configurazione colonne
            columns = [
                ("id", self.translation_manager.get_text("id"), 50, "center"),
                ("participant", self.translation_manager.get_text("participant"), 300, "center"),
                ("quantity", self.translation_manager.get_text("quantity"), 150, "center"),
                ("check", self.translation_manager.get_text("received"), 50, "center")
            ]
            
            for col, heading, width, anchor in columns:
                self.distribution_table.column(col, width=width, anchor=anchor)
                self.distribution_table.heading(
                    col,
                    text=heading,
                    command=lambda c=col: self.sort_table(self.distribution_table, c, False)
                )

            self.distribution_table.bind('<ButtonRelease-1>', self.toggle_distribution_check)
            self.distribution_table.tag_configure("center", anchor="center")
            self.distribution_table.tag_configure("checked", foreground="green")
            
            self.distribution_table.tag_configure("center", anchor="center")
            
            self.translation_manager.log("debug", "log_distribution_table_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_distribution_table", error=str(e))
            raise

    def toggle_distribution_check(self, event):
        """Toggle dello stato check nella distribuzione"""
        try:
            region = self.distribution_table.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            row_id = self.distribution_table.identify_row(event.y)
            col_id = self.distribution_table.identify_column(event.x)
            
            if not row_id or col_id != "#4":  # #4 è la colonna check
                return
            
            values = self.distribution_table.item(row_id)['values']
            if values:
                participant_name = values[1]  # Ora il nome è nella seconda colonna
                prize_name = self.selected_prize.get().split(':')[1].strip()
                check_key = (prize_name, participant_name)

                current_check = values[3]
                if current_check == "☐":
                    new_check = "☑"
                    if check_key not in self.distribution_checks:
                        self.distribution_checks.append(check_key)
                else:
                    new_check = "☐"
                    if check_key in self.distribution_checks:
                        self.distribution_checks.remove(check_key)

                new_values = list(values[:3]) + [new_check]
                self.distribution_table.item(row_id, values=new_values)
                
                # Aggiorna tag per il colore
                if new_check == "☑":
                    self.distribution_table.item(row_id, tags=("center", "checked"))
                else:
                    self.distribution_table.item(row_id, tags=("center",))
                    
        except Exception as e:
            self.translation_manager.log("error", "log_error_toggle_check", error=str(e))

    def update_distribution(self):
        """Aggiornamento calcolo e visualizzazione distribuzione"""
        try:
            # Pulisci tabella
            for item in self.distribution_table.get_children():
                self.distribution_table.delete(item)

            # Se non ci sono elementi, pulisci l'array dei check
            if not any([p.enabled for p in self.participants]):
                self.distribution_checks = []

            # Verifica selezione premio
            selected = self.selected_prize.get()
            if not selected or not self.participants:
                return

            try:
                prize_id = int(selected.split(':')[0])
                selected_prize = selected.split(':')[1].strip()
                prize = next((p for p in self.prizes if p.id == prize_id), None)
                if not prize:
                    return

                # Log per debug
                self.translation_manager.log(
                    "debug",
                    "log_distribution_calculation",
                    prize_name=prize.name,
                    quantity=prize.quantity,
                    integer_only=self.integer_only.get()
                )

                # Calcola distribuzione
                distribution_data = self.calculate_distribution(prize)

                # Visualizza distribuzione
                for participant_id, name, quantity in distribution_data:
                    check_key = (selected_prize, name)
                    is_checked = check_key in self.distribution_checks

                    self.distribution_table.insert(
                        "",
                        "end",
                        values=(
                            participant_id,
                            name,
                            self.format_number(quantity, self.integer_only.get()),
                            "☑" if is_checked else "☐"
                        ),
                        tags=("center", "checked") if is_checked else ("center",)
                    )

            except ValueError:
                return

            self.translation_manager.log(
                "debug",
                "log_distribution_updated",
                prize_id=prize_id
            )
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_distribution_update",
                error=str(e)
            )

    def add_prizes(self):
        """Aggiunta di nuovi premi"""
        try:
            # Carichiamo prima gli elementi esistenti se c'è un evento selezionato
            event_name = self.event_var.get().strip()
            should_return = False

            if event_name:
                try:
                    date_range = self.validate_date_range()
                    if date_range:
                        # Cerca lo stato che corrisponde per nome e che è attivo nel periodo selezionato
                        existing_state = next((s for s in self.saved_states 
                                        if s.event == event_name and
                                        # Converte le date in oggetti date per confronto
                                        (date(s.date_range.start_year, 
                                             s.date_range.start_month, 
                                             s.date_range.start_day or 1) <= 
                                        # Controlla che la data di inizio dell'evento esistente
                                        # non sia dopo la data di fine del nuovo evento 
                                        date(date_range.end_year or date_range.start_year,
                                             date_range.end_month or date_range.start_month,
                                             date_range.end_day or monthrange(date_range.end_year or date_range.start_year,
                                                                            date_range.end_month or date_range.start_month)[1])
                                        and
                                        # Controlla che la data di inizio del nuovo evento
                                        # non sia dopo la data di fine dell'evento esistente
                                        date(date_range.start_year,
                                             date_range.start_month,
                                             date_range.start_day or 1) <=
                                        date(s.date_range.end_year or s.date_range.start_year,
                                             s.date_range.end_month or s.date_range.start_month,
                                             s.date_range.end_day or monthrange(s.date_range.end_year or s.date_range.start_year,
                                                                              s.date_range.end_month or s.date_range.start_month)[1]))), None)
                                        
                        if existing_state and not any(self.prizes) and not any(self.participants):
                            # Crea nuovi oggetti premio indipendenti
                            self.prizes = [Prize(
                                id=p.id,
                                name=p.name,
                                quantity=p.quantity,
                                is_special=p.is_special,
                                top_winners=p.top_winners
                            ) for p in existing_state.prizes]
                            
                            # Crea nuovi oggetti partecipante indipendenti
                            self.participants = [Participant(
                                id=p.id,
                                name=p.name,
                                damage=p.damage,
                                enabled=p.enabled
                            ) for p in existing_state.participants]
                            
                            # Aggiorna il next_prize_id
                            if self.prizes:
                                self.next_prize_id = max(p.id for p in self.prizes) + 1

                            # Aggiorna il next_participant_id
                            if self.participants:
                                self.next_participant_id = max(p.id for p in self.participants) + 1

                except Exception as e:
                    self.translation_manager.log("error", "log_error_date_validation", error=str(e))

            if self.prize_input_mode.get() == "single":
                name = self.prize_name_entry.get().strip()
                quantity_str = self.prize_quantity_entry.get().strip()
                
                # Validazione
                errors = []
                if not name:
                    errors.append(self.translation_manager.get_text("name_required"))
                elif len(name) < 3:  # Aggiunto controllo lunghezza minima
                    errors.append(self.translation_manager.get_text("prize_name_too_short"))
                if self.check_name_exists(name, True):
                    errors.append(self.translation_manager.get_text("name_exists_msg"))
                    should_return = True
                if not quantity_str:
                    errors.append(self.translation_manager.get_text("quantity_required"))
                
                if errors:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        "\n".join(errors)
                    )
                    should_return = True

                # Aggiorniamo l'interfaccia prima del return se necessario
                if should_return:
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    return
                
                try:
                    if quantity_str == '#':
                        quantity = quantity_str
                    else:
                        quantity = float(quantity_str)
                        if quantity <= 0:
                            raise ValueError(self.translation_manager.get_text("invalid_quantity"))
                            
                    prize = Prize(
                        id=self.next_prize_id,
                        name=name,
                        quantity=quantity,
                        is_special=self.is_special.get(),
                        top_winners=int(self.top_winners.get()) if self.is_special.get() else 1
                    )
                    self.prizes.append(prize)
                    self.next_prize_id += 1
                    
                    # Pulisci campi
                    self.prize_name_entry.delete(0, tk.END)
                    self.prize_quantity_entry.delete(0, tk.END)
                    
                    # Aggiorna interfaccia
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    
                except ValueError as e:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        str(e)
                    )
                    return
                    
            else:  # Batch mode
                text = self.prize_text.get("1.0", "end-1c")
                if not text.strip():
                    return
                    
                errors = []
                for line in text.strip().split('\n'):
                    if not line.strip():
                        continue
                        
                    try:
                        if ':' not in line:
                            raise ValueError(self.translation_manager.get_text("missing_separator"))
                            
                        name, quantity = line.split(':')[:2]  # prendiamo i primi due elementi
                        name = name.strip()
                        quantity = quantity.strip()
                        
                        if not name:
                            raise ValueError(self.translation_manager.get_text("name_required"))
                        if len(name) < 3:
                            raise ValueError(self.translation_manager.get_text("prize_name_too_short"))
                        if len(name) > 20:
                            raise ValueError(self.translation_manager.get_text("prize_name_too_long"))
                        if self.check_name_exists(name, True):
                            errors.append(f"{self.translation_manager.get_text('name_exists_msg')}: {name}")
                            continue
                        
                        # Gestione premio speciale
                        is_special = False
                        top_winners = 1
                        parts = line.split(':')
                        if len(parts) > 2:
                            special_part = parts[2].strip().lower()
                            if special_part == 's':
                                if len(parts) < 4:
                                    raise ValueError(self.translation_manager.get_text("missing_winners"))
                                try:
                                    top_winners = int(parts[3].strip())
                                    if top_winners < 1:
                                        raise ValueError
                                    is_special = True
                                except ValueError:
                                    raise ValueError(self.translation_manager.get_text("invalid_winners"))
                            elif special_part:
                                raise ValueError(self.translation_manager.get_text("invalid_special"))
                        
                        # Validazione quantità
                        if quantity == '#':
                            quantity_value = quantity
                        else:
                            try:
                                quantity_value = int(quantity)  # cambiato da float a int
                                if quantity_value <= 0:
                                    raise ValueError
                            except ValueError:
                                raise ValueError(self.translation_manager.get_text("quantity_must_be_integer"))
                        
                        prize = Prize(
                            id=self.next_prize_id,
                            name=name,
                            quantity=quantity_value,
                            is_special=is_special,
                            top_winners=top_winners
                        )
                        self.prizes.append(prize)
                        self.next_prize_id += 1
                            
                    except ValueError as e:
                        errors.append(f"{str(e)}: {line}")
                    
                if errors:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        "\n".join(errors)
                    )
                
                self.prize_text.delete("1.0", tk.END)
            
            # Aggiorna interfaccia
            self.update_tables()
            self.check_save_buttons_state()
            self.update_button_states()
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_adding_prizes", error=str(e))

            print(f"Error adding prizes: {str(e)}")
            print(traceback.format_exc())

    def add_participants(self):
        """Aggiunta di nuovi partecipanti"""
        try:
            # Carichiamo prima gli elementi esistenti se c'è un evento selezionato
            event_name = self.event_var.get().strip()
            should_return = False

            if event_name:
                try:
                    date_range = self.validate_date_range()
                    if date_range:
                        # Cerca lo stato che corrisponde per nome e che è attivo nel periodo selezionato
                        existing_state = next((s for s in self.saved_states 
                                        if s.event == event_name and
                                        # Converte le date in oggetti date per confronto
                                        (date(s.date_range.start_year, 
                                             s.date_range.start_month, 
                                             s.date_range.start_day or 1) <= 
                                        # Controlla che la data di inizio dell'evento esistente
                                        # non sia dopo la data di fine del nuovo evento 
                                        date(date_range.end_year or date_range.start_year,
                                             date_range.end_month or date_range.start_month,
                                             date_range.end_day or monthrange(date_range.end_year or date_range.start_year,
                                                                            date_range.end_month or date_range.start_month)[1])
                                        and
                                        # Controlla che la data di inizio del nuovo evento
                                        # non sia dopo la data di fine dell'evento esistente
                                        date(date_range.start_year,
                                             date_range.start_month,
                                             date_range.start_day or 1) <=
                                        date(s.date_range.end_year or s.date_range.start_year,
                                             s.date_range.end_month or s.date_range.start_month,
                                             s.date_range.end_day or monthrange(s.date_range.end_year or s.date_range.start_year,
                                                                              s.date_range.end_month or s.date_range.start_month)[1]))), None)

                        if existing_state and not any(self.participants) and not any(self.prizes):
                            # Crea nuovi oggetti partecipante indipendenti
                            self.participants = [Participant(
                                id=p.id,
                                name=p.name,
                                damage=p.damage,
                                enabled=p.enabled
                            ) for p in existing_state.participants]
                            
                            # Crea nuovi oggetti premio indipendenti
                            self.prizes = [Prize(
                                id=p.id,
                                name=p.name,
                                quantity=p.quantity,
                                is_special=p.is_special,
                                top_winners=p.top_winners
                            ) for p in existing_state.prizes]
                            
                            # Aggiorna il next_participant_id
                            if self.participants:
                                self.next_participant_id = max(p.id for p in self.participants) + 1

                            # Aggiorna il next_prize_id
                            if self.prizes:
                                self.next_prize_id = max(p.id for p in self.prizes) + 1
                            
                except Exception as e:
                    self.translation_manager.log("error", "log_error_date_validation", error=str(e))
                        
            if self.participant_input_mode.get() == "single":
                name = self.participant_name_entry.get().strip()
                damage_str = self.participant_damage_entry.get().strip()
                
                # Validazione
                errors = []
                if not name:
                    errors.append(self.translation_manager.get_text("name_required"))
                elif len(name) < 3:  # Aggiunto controllo lunghezza minima
                    errors.append(self.translation_manager.get_text("participant_name_too_short"))
                if self.check_name_exists(name, False):
                    errors.append(self.translation_manager.get_text("name_exists_msg"))
                    should_return = True
                if not damage_str:
                    errors.append(self.translation_manager.get_text("damage_required"))
                
                if errors:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        "\n".join(errors)
                    )
                    should_return = True

                    # Aggiorniamo l'interfaccia prima del return se necessario
                    if should_return:
                        self.update_tables()
                        self.check_save_buttons_state()
                        self.update_button_states()
                        return
                
                try:
                    if damage_str == '#':
                        damage = damage_str
                    else:
                        damage = float(damage_str)
                        if damage < 0:  # Allow 0 damage
                            raise ValueError(self.translation_manager.get_text("invalid_damage"))
                            
                    participant = Participant(
                        id=self.next_participant_id,
                        name=name,
                        damage=damage
                    )
                    self.participants.append(participant)
                    self.next_participant_id += 1
                    
                    # Pulisci campi
                    self.participant_name_entry.delete(0, tk.END)
                    self.participant_damage_entry.delete(0, tk.END)

                    # Aggiorna interfaccia
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    
                except ValueError as e:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        str(e)
                    )
            else:  # Batch mode
                text = self.participant_text.get("1.0", "end-1c")
                if not text.strip():
                    return
                    
                errors = []
                for line in text.strip().split('\n'):
                    if not line.strip():
                        continue
                        
                    try:
                        if ':' not in line:
                            raise ValueError(self.translation_manager.get_text("missing_separator"))
                            
                        name, damage = line.split(':')
                        name = name.strip()
                        damage = damage.strip()
                        
                        if not name:
                            raise ValueError(self.translation_manager.get_text("name_required"))
                        if len(name) < 3:
                            raise ValueError(self.translation_manager.get_text("participant_name_too_short"))
                        if len(name) > 20:
                            raise ValueError(self.translation_manager.get_text("participant_name_too_long"))
                        if self.check_name_exists(name, False):
                            errors.append(f"{self.translation_manager.get_text('name_exists_msg')}: {name}")
                            continue
                            
                        if damage == '#':
                            damage_value = damage
                        else:
                            try:
                                damage_value = int(damage)  # cambiato da float a int
                                if damage_value < 0:  # Allow 0 damage
                                    raise ValueError
                            except ValueError:
                                raise ValueError(self.translation_manager.get_text("damage_must_be_integer"))
                        
                        participant = Participant(
                            id=self.next_participant_id,
                            name=name,
                            damage=damage_value
                        )
                        self.participants.append(participant)
                        self.next_participant_id += 1
                            
                    except ValueError as e:
                        errors.append(f"{str(e)}: {line}")
                    
                if errors:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        "\n".join(errors)
                    )
                
                self.participant_text.delete("1.0", tk.END)

            # Aggiorna interfaccia
            self.update_tables()
            self.check_save_buttons_state()
            self.update_button_states()
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_adding_participants", error=str(e))

            print(f"Error adding participants: {str(e)}")
            print(traceback.format_exc())

    def parse_batch_prize_input(self, line: str) -> Tuple[str, float, bool, int]:
        """Parsing input batch premi"""
        try:
            parts = line.strip().split(':')
            if len(parts) < 2:
                raise ValueError(self.translation_manager.get_text("missing_separator"))
                
            name = parts[0].strip()
            if not name:
                raise ValueError(self.translation_manager.get_text("missing_name"))
            
            # Gestione del cancelletto
            quantity_str = parts[1].strip()
            if quantity_str == '#':
                quantity = quantity_str
            else:
                try:
                    quantity = float(quantity_str)
                    if quantity <= 0:
                        raise ValueError
                except ValueError:
                    raise ValueError(self.translation_manager.get_text("invalid_quantity"))
            
            is_special = False
            top_winners = 1
            
            if len(parts) > 2:
                special_part = parts[2].strip().lower()
                if special_part == 's':
                    if len(parts) < 4:
                        raise ValueError(self.translation_manager.get_text("missing_winners"))
                    try:
                        top_winners = int(parts[3].strip())
                        if top_winners < 1:
                            raise ValueError
                        is_special = True
                    except ValueError:
                        raise ValueError(self.translation_manager.get_text("invalid_winners"))
                elif special_part:
                    raise ValueError(self.translation_manager.get_text("invalid_special"))
            
            return name, quantity, is_special, top_winners
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_parsing_prize", error=str(e))
            raise

    def calculate_distribution(self, prize: Prize) -> List[Tuple[int, str, float]]:
        """Calcolo della distribuzione per un premio"""
        try:
            # Escludi partecipanti con cancelletto
            active_participants = [
                p for p in self.participants 
                if p.enabled and not (isinstance(p.damage, str) and p.damage.strip() == '#')
            ]
            if not active_participants:
                return []

            total_damage = sum(p.damage for p in active_participants)
            if total_damage == 0:
                return []

            distribution_data = []

            if prize.is_special:
                # Distribuzione premio speciale
                top_participants = sorted(
                    active_participants,
                    key=lambda p: p.id  # Ordina per ID
                )[:prize.top_winners]
                winner_total_damage = sum(p.damage for p in top_participants)

                if self.integer_only.get():
                    distribution_data = self.calculate_integer_distribution(top_participants, winner_total_damage, prize.quantity)
                else:
                    for p in top_participants:
                        ratio = p.damage / winner_total_damage
                        qty = prize.quantity * ratio
                        distribution_data.append((p.id, p.name, qty))
                        
            else:
                # Distribuzione premio normale
                if self.integer_only.get():
                    distribution_data = self.calculate_integer_distribution(active_participants, total_damage, prize.quantity)
                else:
                    # Ordina i partecipanti per ID prima di calcolare le quote
                    sorted_participants = sorted(active_participants, key=lambda p: p.id)
                    for p in sorted_participants:
                        ratio = p.damage / total_damage
                        qty = prize.quantity * ratio
                        distribution_data.append((p.id, p.name, qty))

            return distribution_data

        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_distribution_calculation",
                error=str(e)
            )
            return []

    def setup_history_tab(self):
        """Setup della tab cronologia"""
        try:
            self.history_frame = ttk.Frame(self.notebook)
            self.notebook.add(
                self.history_frame,
                text=self.translation_manager.get_text("history")
            )
            
            # Frame filtri
            self.create_history_filters()
            
            # Tabella cronologia
            self.create_history_table()
            
            self.translation_manager.log("debug", "log_history_tab_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_history_tab", error=str(e))
            raise

    def create_history_filters(self):
        """Creazione filtri cronologia"""
        try:
            self.filter_frame = ttk.LabelFrame(
                self.history_frame,
                text=self.translation_manager.get_text("filters")
            )
            self.filter_frame.pack(fill="x", padx=5, pady=5)
            
            # Filtro anno
            self.create_year_filter()
            
            # Filtro mese
            self.create_month_filter()
            
            # Filtro evento
            self.create_event_filter()
            
            self.translation_manager.log("debug", "log_history_filters_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_history_filters", error=str(e))
            raise

    def create_year_filter(self):
        """Creazione filtro anno"""
        try:
            self.history_year_frame = ttk.Frame(self.filter_frame)
            self.history_year_frame.pack(side="left", padx=5)
            
            self.history_year_label = ttk.Label(
                self.history_year_frame,
                text=self.translation_manager.get_text("year")
            )
            self.history_year_label.pack(side="left")
            
            self.history_year = ttk.Combobox(
                self.history_year_frame,
                values=[],
                width=6
            )
            self.history_year.pack(side="left", padx=5)

            current_year = str(datetime.now().year)
            self.history_year.set(current_year)
            
            self.history_year.bind(
                '<<ComboboxSelected>>',
                self.on_history_filter_change
            )
            
            self.translation_manager.log("debug", "log_year_filter_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_year_filter", error=str(e))
            raise

    def create_month_filter(self):
        """Creazione filtro mese"""
        try:
            self.history_month_frame = ttk.Frame(self.filter_frame)
            self.history_month_frame.pack(side="left", padx=5)
            
            self.history_month_label = ttk.Label(
                self.history_month_frame,
                text=self.translation_manager.get_text("month")
            )
            self.history_month_label.pack(side="left")
            
            self.history_month = ttk.Combobox(
                self.history_month_frame,
                values=[],
                width=10
            )
            self.history_month.pack(side="left", padx=5)
            
            self.history_month.bind(
                '<<ComboboxSelected>>',
                self.on_history_filter_change
            )
            
            self.translation_manager.log("debug", "log_month_filter_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_month_filter", error=str(e))
            raise

    def create_event_filter(self):
        """Creazione filtro evento"""
        try:
            self.event_filter_frame = ttk.Frame(self.filter_frame)
            self.event_filter_frame.pack(side="left", padx=5)
            
            self.history_event_label = ttk.Label(
                self.event_filter_frame,
                text=self.translation_manager.get_text("event")
            )
            self.history_event_label.pack(side="left")
            
            self.history_event = ttk.Combobox(
                self.event_filter_frame,
                values=[],
                width=20
            )
            self.history_event.pack(side="left", padx=5)
            
            self.history_event.bind(
                '<<ComboboxSelected>>',
                self.on_history_filter_change
            )
            
            self.translation_manager.log("debug", "log_event_filter_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_event_filter", error=str(e))
            raise

    def create_bottom_frame(self):
        """Creazione della barra inferiore"""
        try:
            self.save_frame = ttk.Frame(self.root)
            if not self.save_frame:
                raise ValueError("Failed to create save frame")
                
            self.save_frame.pack(fill="x", padx=5, pady=5)
            
            # Pulsante salvataggio stato
            self.save_state_button = ttk.Button(
                self.save_frame,
                text=self.translation_manager.get_text("save_state"),
                command=self.save_current_state,
                state="disabled"
            )
            if not self.save_state_button:
                raise ValueError("Failed to create save state button")
                
            self.save_state_button.pack(side="right", padx=5)
            
            # Pulsante aggiornamento stato
            self.update_state_button = ttk.Button(
                self.save_frame,
                text=self.translation_manager.get_text("update_state"),
                command=self.update_current_state,
                state="disabled"
            )
            if not self.update_state_button:
                raise ValueError("Failed to create update state button")
                
            self.update_state_button.pack(side="right", padx=5)
            
            self.translation_manager.log("debug", "log_bottom_frame_created")
            
        except Exception as e:
            self.translation_manager.log(
                "error", 
                "log_error_bottom_frame", 
                error=f"Detailed error: {str(e)}"
            )
            raise  # Rilanciamo l'eccezione per vedere l'errore nel terminale

    def create_history_table(self):
        """Creazione tabella cronologia"""
        try:
            self.history_table_frame = ttk.Frame(self.history_frame)
            self.history_table_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            self.history_table = ttk.Treeview(
                self.history_table_frame,
                show="headings",
                height=15
            )
            
            # Scrollbars
            self.history_y_scrollbar = ttk.Scrollbar(
                self.history_table_frame,
                orient="vertical",
                command=self.history_table.yview
            )
            self.history_x_scrollbar = ttk.Scrollbar(
                self.history_table_frame,
                orient="horizontal",
                command=self.history_table.xview
            )
            
            self.history_table.configure(
                yscrollcommand=self.history_y_scrollbar.set,
                xscrollcommand=self.history_x_scrollbar.set
            )
            
            # Layout
            self.history_table.grid(row=0, column=0, sticky="nsew")
            self.history_y_scrollbar.grid(row=0, column=1, sticky="ns")
            self.history_x_scrollbar.grid(row=1, column=0, sticky="ew")
            
            self.history_table_frame.grid_rowconfigure(0, weight=1)
            self.history_table_frame.grid_columnconfigure(0, weight=1)
            
            # Configurazione colonne
            columns = [
                ("date", self.translation_manager.get_text("date"), 120, "center"),
                ("event", self.translation_manager.get_text("event"), 150, "center"),
                ("participants", self.translation_manager.get_text("participants"), 180, "w"),
                ("damages", f"{self.translation_manager.get_text('damage')} ({self.translation_manager.get_text('total_damage')})", 180, "w"),
                ("prizes", self.translation_manager.get_text("prizes"), 180, "w"),
                ("distributions", self.translation_manager.get_text("distributions"), 220, "w")
            ]
            
            self.history_table["columns"] = [col[0] for col in columns]
            
            for col, heading, width, anchor in columns:
                self.history_table.column(
                    col,
                    width=width,
                    minwidth=width,
                    anchor=anchor
                )
                self.history_table.heading(
                    col,
                    text=heading,
                    command=lambda c=col: self.sort_table(self.history_table, c, False)
                )
            
            self.history_table.tag_configure("center", anchor="center")
            
            self.translation_manager.log("debug", "log_history_table_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_history_table", error=str(e))
            raise

    def on_history_filter_change(self, event=None):
        """Gestione cambio filtri cronologia"""
        try:
            # Ottieni selezioni correnti
            year = self.history_year.get()
            month = self.history_month.get()
            
            # Reset dipendenti quando cambia l'anno
            if isinstance(event, tk.Event) and event.widget == self.history_year:
                self.history_month.set('')
                self.history_event.set('')
            # Reset eventi quando cambia il mese
            elif isinstance(event, tk.Event) and event.widget == self.history_month:
                self.history_event.set('')
                
            # Aggiorna filtri e tabella
            self.update_history_filters()
            self.update_history_table()
            
            self.translation_manager.log(
                "debug",
                "log_history_filters_changed",
                year=year,
                month=month
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_history_filter_change", error=str(e))
            raise

    def get_filtered_states(self) -> List[SavedState]:
        """Ottieni stati filtrati in base alle selezioni"""
        try:
            filtered_states = []
            month = self.history_month.get()
            event = self.history_event.get()
            
            if year := self.history_year.get():
                year = int(year)
                # Filtra per anno, includendo:
                # - eventi che iniziano in questo anno
                # - eventi che finiscono in questo anno se iniziano nell'anno precedente
                filtered_states = [
                    s for s in self.saved_states 
                    if (s.date_range.start_year == year or  # Eventi che iniziano in questo anno
                        (s.date_range.start_year == year - 1 and  # Eventi che iniziano l'anno precedente
                        s.date_range.end_year == year and  # e finiscono in questo anno
                        s.date_range.end_month is not None))
                ]
                
                # Filtra per mese se selezionato
                if month:
                    month = int(month)
                    filtered_states = [
                        s for s in filtered_states 
                        if ((s.date_range.start_year == year and  # Eventi nello stesso anno
                            s.date_range.start_month == month) or  # che iniziano nel mese selezionato
                            (s.date_range.start_year == year and  # Eventi nello stesso anno
                            s.date_range.end_month is not None and  # che attraversano più mesi
                            s.date_range.start_month < month and  # iniziati prima
                            s.date_range.end_month >= month) or  # e che includono il mese selezionato
                            (s.date_range.start_year == year - 1 and  # Eventi che attraversano l'anno
                            s.date_range.end_year == year and  
                            s.date_range.end_month == month))  # e finiscono nel mese selezionato
                    ]
                
                # Filtra per evento se selezionato
                if event:
                    filtered_states = [
                        s for s in filtered_states 
                        if s.event == event
                    ]
            else:
                # Se non c'è anno selezionato
                filtered_states = self.saved_states[:]
                
                # Filtra per mese se selezionato
                if month:
                    month = int(month)
                    filtered_states = [
                        s for s in filtered_states 
                        if (s.date_range.start_month == month or  # Eventi che iniziano in questo mese
                            (s.date_range.end_month is not None and  # Eventi multi-mese
                            s.date_range.start_month < month and  # che iniziano prima
                            s.date_range.end_month >= month) or  # e includono questo mese
                            (s.date_range.end_month == month and  # Eventi che finiscono in questo mese
                            s.date_range.start_month > month))  # ma sono iniziati dopo (attraversamento anno)
                    ]
                
                # Filtra per evento se selezionato
                if event:
                    filtered_states = [
                        s for s in filtered_states 
                        if s.event == event
                    ]
            
            self.translation_manager.log(
                "debug",
                "log_states_filtered",
                count=len(filtered_states)
            )
            
            return filtered_states
        except Exception as e:
            self.translation_manager.log("error", "log_error_filtering_states", error=str(e))
            raise

    def update_history_filters(self):
        """Aggiornamento dei valori dei filtri"""
        try:
            if not all([self.history_year, self.history_month, self.history_event]):
                return
                    
            # Ottieni anni unici da tutti gli stati
            years = sorted(set(
                year for state in self.saved_states
                for year in range(
                    state.date_range.start_year,
                    (state.date_range.end_year or state.date_range.start_year) + 1
                )
            ))
            self.history_year['values'] = [''] + [str(y) for y in years]
            
            selected_year = self.history_year.get()
            selected_month = self.history_month.get()
            
            months = set()
            events = set()

            # Se non c'è anno selezionato, mostra tutti i mesi ed eventi
            if not selected_year:
                for state in self.saved_states:
                    # Raccogli tutti i mesi sia di inizio che di fine
                    months.add(state.date_range.start_month)
                    if state.date_range.end_month is not None:
                        months.add(state.date_range.end_month)

                    # Se c'è un mese selezionato
                    if selected_month:
                        month = int(selected_month)
                        if (state.date_range.start_month == month or  # Eventi che iniziano in questo mese
                            (state.date_range.end_month is not None and  # Eventi multi-mese
                            state.date_range.start_month < month and 
                            state.date_range.end_month >= month) or
                            (state.date_range.end_month == month and  # Eventi che attraversano l'anno
                            state.date_range.start_month > month)):
                            events.add(state.event)
                    else:
                        # Se non c'è mese selezionato, mostra tutti gli eventi
                        events.add(state.event)
            else:
                year = int(selected_year)
                # Raccogli i mesi per l'anno selezionato
                for state in self.saved_states:
                    if state.date_range.start_year == year:
                        months.add(state.date_range.start_month)
                        if state.date_range.end_month is not None:
                            months.add(state.date_range.end_month)
                    elif (state.date_range.start_year == year - 1 and 
                        state.date_range.end_year == year and 
                        state.date_range.end_month is not None):
                        months.add(state.date_range.end_month)

                # Filtra gli eventi
                if selected_month:
                    month = int(selected_month)
                    for state in self.saved_states:
                        if ((state.date_range.start_year == year and 
                            state.date_range.start_month == month) or
                            (state.date_range.start_year == year and
                            state.date_range.end_month is not None and
                            state.date_range.start_month < month and
                            state.date_range.end_month >= month) or
                            (state.date_range.start_year == year - 1 and
                            state.date_range.end_year == year and
                            state.date_range.end_month == month)):
                            events.add(state.event)
                else:
                    # Se non c'è mese selezionato, mostra tutti gli eventi dell'anno
                    for state in self.saved_states:
                        if (state.date_range.start_year == year or
                            (state.date_range.start_year == year - 1 and
                            state.date_range.end_year == year)):
                            events.add(state.event)

            # Aggiorna i valori delle combo
            self.history_month['values'] = [''] + [f"{m:02d}" for m in sorted(months)]
            self.history_event['values'] = [''] + sorted(events)
            
            # Se il valore corrente non è più valido, resettalo
            if self.history_month.get() and self.history_month.get() not in self.history_month['values']:
                self.history_month.set('')
            if self.history_event.get() and self.history_event.get() not in self.history_event['values']:
                self.history_event.set('')
            
            self.translation_manager.log("debug", "log_history_filters_updated")
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_filters", error=str(e))
            raise

    def toggle_top_winners(self):
        """Toggle della visibilità del campo numero vincitori"""
        try:
            if self.is_special.get():
                self.top_winners_label.pack(side="left", padx=5)
                self.top_winners.pack(side="left", padx=5)
            else:
                self.top_winners_label.pack_forget()
                self.top_winners.pack_forget()
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_toggle_winners", error=str(e))

    def handle_prize_action(self, event):
        """Gestione azioni sulla tabella premi"""
        try:
            table = self.prizes_table
            region = table.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            row_id = table.identify_row(event.y)
            col_id = table.identify_column(event.x)
            
            if not row_id or not col_id:
                return
                
            values = table.item(row_id)['values']
            if not values:
                return
                
            prize_id = values[0]
            
            if col_id == "#6":  # edit column
                self.edit_prize(prize_id)
            elif col_id == "#7":  # delete column
                self.delete_prize(prize_id)
                
            self.translation_manager.log(
                "debug",
                "log_prize_action_handled",
                action="edit" if col_id == "#6" else "delete",
                prize_id=prize_id
            )
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_action", error=str(e))

    def update_history_table(self):
        """Aggiornamento della tabella cronologia"""
        try:
            # Pulisci tabella
            for item in self.history_table.get_children():
                self.history_table.delete(item)
                
            filtered_states = self.get_filtered_states()
            filtered_states.sort(key=lambda s: (
                s.date_range.start_year,
                s.date_range.start_month, 
                s.date_range.start_day if s.date_range.start_day else 0
            ))
            
            for state in filtered_states:
                # Formatta dati partecipanti
                participants_lines = [
                    f"{p.name} ({'✓' if p.enabled else '✗'})"
                    for p in state.participants
                ]
                
                # Formatta dati danni
                damages_lines = self.format_damage_lines(state)
                
                # Formatta dati premi
                prizes_lines = self.format_prize_lines(state)
                
                # Formatta distribuzioni
                distributions_lines = self.format_distribution_lines(state)
                
                # Prima riga con intestazioni
                event_row = self.history_table.insert(
                    "",
                    "end",
                    values=(
                        str(state.date_range),
                        state.event,
                        self.translation_manager.get_text("participants"),
                        self.translation_manager.get_text("damages"),
                        self.translation_manager.get_text("prizes"),
                        self.translation_manager.get_text("distributions")
                    ),
                    tags=("center",)
                )
                
                # Righe dati
                max_rows = max(
                    len(participants_lines),
                    len(damages_lines),
                    len(prizes_lines),
                    len(distributions_lines)
                )
                
                # Estendi liste alla stessa lunghezza
                participants_lines.extend([""] * (max_rows - len(participants_lines)))
                damages_lines.extend([""] * (max_rows - len(damages_lines)))
                prizes_lines.extend([""] * (max_rows - len(prizes_lines)))
                distributions_lines.extend([""] * (max_rows - len(distributions_lines)))
                
                # Inserisci righe dati
                for i in range(max_rows):
                    self.history_table.insert(
                        "",
                        "end",
                        values=(
                            "",
                            "",
                            participants_lines[i],
                            damages_lines[i],
                            prizes_lines[i],
                            distributions_lines[i]
                        ),
                        tags=("center",)
                    )
            
            self.translation_manager.log(
                "debug",
                "log_history_table_updated",
                states=len(filtered_states)
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_history", error=str(e))
            raise

    def update_history_table_headers(self):
        """Aggiornamento intestazioni tabella cronologia"""
        try:
            columns = [
                ("date", self.translation_manager.get_text("date")),
                ("event", self.translation_manager.get_text("event")),
                ("participants", self.translation_manager.get_text("participants")),
                ("damages", f"{self.translation_manager.get_text('damage')} ({self.translation_manager.get_text('total_damage')})"),
                ("prizes", self.translation_manager.get_text("prizes")),
                ("distributions", self.translation_manager.get_text("distributions"))
            ]
            
            for col, text in columns:
                self.history_table.heading(
                    col,
                    text=text if isinstance(text, str) else text()
                )
                
            self.translation_manager.log("debug", "log_history_headers_updated")
            
        except Exception as e:
            self.translation_manager.log(
                "error", 
                "log_error_history_headers",
                error=str(e)
            )

    def format_damage_lines(self, state: SavedState) -> List[str]:
        """Formattazione linee danni per la cronologia"""
        try:
            damages_lines = []
            total_damage = state.total_damage
            
            # Mostra danni e percentuali di tutti i partecipanti
            for p in state.participants:
                percentage = (p.damage / total_damage * 100) if total_damage > 0 else 0
                status = self.translation_manager.get_text("disabled") if not p.enabled else ""
                
                line = (
                    f"{p.name}: {self.format_number(p.damage)} "
                    f"({percentage:.1f}%) {status}"
                ).strip()
                damages_lines.append(line)
            
            # Aggiungi totale
            damages_lines.append(
                f"{self.translation_manager.get_text('total')}: "
                f"{self.format_number(total_damage)}"
            )
            
            return damages_lines
        except Exception as e:
            self.translation_manager.log("error", "log_error_formatting_damages", error=str(e))
            raise

    def format_prize_lines(self, state: SavedState) -> List[str]:
        """Formattazione linee premi per la cronologia"""
        try:
            prizes_lines = []
            for p in state.prizes:
                prize_text = f"{p.name}: {self.format_number(p.quantity)}"
                if p.is_special:
                    prize_text += f" ({self.translation_manager.get_text('special_prize')})"
                    if p.top_winners > 1:
                        prize_text += f" {p.top_winners} {self.translation_manager.get_text('winners')}"
                prizes_lines.append(prize_text)
            return prizes_lines
        except Exception as e:
            self.translation_manager.log("error", "log_error_formatting_prizes", error=str(e))
            raise

    def format_distribution_lines(self, state: SavedState) -> List[str]:
        """Formattazione linee distribuzioni per la cronologia"""
        try:
            distributions_lines = []
            for prize_id, dist_list in state.distributions.items():
                prize = next((p for p in state.prizes if p.id == prize_id), None)
                if prize:
                    distributions_lines.append(f"• {prize.name}:")
                    for dist_entry in dist_list:
                        if isinstance(dist_entry, (list, tuple)):
                            name = dist_entry[0] if len(dist_entry) > 0 else ""
                            qty = dist_entry[1] if len(dist_entry) > 1 else 0
                        else:
                            name = ""
                            qty = 0
                            
                        participant = next(
                            (p for p in state.participants if p.name == name),
                            None
                        )
                        if participant:
                            status = (
                                self.translation_manager.get_text("disabled")
                                if not participant.enabled else ""
                            )
                            distributions_lines.append(
                                f"  - {name}: {self.format_number(qty)} {status}".strip()
                            )

            return distributions_lines
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_formatting_distributions", error=str(e))
            return []  # Ritorna una lista vuota in caso di errore

    def calculate_integer_distribution(
            self,
            participants: List[Participant],
            total_damage: float,
            quantity: float
        ) -> List[Tuple[int, str, float]]:
            """Calcolo distribuzione con numeri interi"""
            try:
                if not participants or total_damage == 0:
                    return []

                total_to_distribute = int(quantity)
                
                # Calcolo quote esatte e ordina per danno
                shares = []
                for participant in sorted(participants, key=lambda p: p.damage, reverse=True):
                    ratio = participant.damage / total_damage
                    exact_share = quantity * ratio
                    shares.append([participant, exact_share, exact_share])  # salviamo anche la quota esatta originale

                # Prima assegnazione basata sull'arrotondamento matematico standard
                total_assigned = 0
                for share in shares:
                    rounded = round(share[1])  # .5 o più va all'intero superiore
                    share[1] = rounded
                    total_assigned += rounded

                # Correggi il totale se necessario
                diff = total_assigned - total_to_distribute
                if diff != 0:
                    # Manteniamo l'ordine per danno per le correzioni
                    if diff > 0:  # Se abbiamo assegnato troppo
                        for i in range(abs(diff)):
                            # Cerchiamo la quota più bassa che possiamo decrementare
                            min_loss = float('inf')
                            min_idx = -1
                            for j, share in enumerate(shares):
                                if share[1] > 0:  # se possiamo ancora decrementare
                                    loss = abs((share[1] - 1) - share[2])  # distanza dalla quota esatta
                                    if loss < min_loss:
                                        min_loss = loss
                                        min_idx = j
                            if min_idx >= 0:
                                shares[min_idx][1] -= 1
                    else:  # Se abbiamo assegnato troppo poco
                        for i in range(abs(diff)):
                            # Cerchiamo la quota più alta che possiamo incrementare
                            min_gain = float('inf')
                            min_idx = -1
                            for j, share in enumerate(shares):
                                gain = abs((share[1] + 1) - share[2])  # distanza dalla quota esatta
                                if gain < min_gain:
                                    min_gain = gain
                                    min_idx = j
                            if min_idx >= 0:
                                shares[min_idx][1] += 1

                # Ordina il risultato finale per ID
                result = [(p.id, p.name, qty) for p, qty, _ in shares]
                result.sort(key=lambda x: x[0])

                return result

            except Exception as e:
                self.translation_manager.log("error", "log_error_integer_distribution", error=str(e))
                return []

    def format_number(self, value: float, force_integer: bool = False) -> str:
        """Formattazione numero rimuovendo decimali non necessari"""
        try:
            if force_integer:
                return str(int(round(value)))
                
            if isinstance(value, float):
                s = f"{value:.10f}".rstrip('0').rstrip('.')
                return s if '.' in s else str(int(value))
                
            return str(value)
        except Exception as e:
            self.translation_manager.log("error", "log_error_number_format", error=str(e))
            raise

    def check_name_exists(self, name: str, is_prize: bool) -> bool:
        """Verifica se il nome esiste già nei premi o partecipanti"""
        try:
            if is_prize:
                return any(p.name.lower() == name.lower() for p in self.prizes)
            else:
                return any(p.name.lower() == name.lower() for p in self.participants)
                
        except Exception as e:
            self.translation_manager.log(
                "error", 
                "log_error_checking_name", 
                error=str(e)
            )
            return False
        
    def validate_date_range(self) -> Optional[DateRange]:
        """Validazione date"""
        try:
            year = int(self.year_var.get())
            start_month = None
            end_month = None
            
            if self.start_month.get():
                start_month = int(self.start_month.get().split()[0])
            else:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("start_month_required")
                )
                return None
                
            if self.use_date_range.get() and self.end_month.get():
                end_month = int(self.end_month.get().split()[0])
                
            # Crea oggetto DateRange
            date_range = DateRange(
                start_year=year,
                start_month=start_month,
                start_day=int(self.start_day.get()) if self.start_day.get() else None,
                end_year=year if end_month else None,
                end_month=end_month,
                end_day=int(self.end_day.get()) if self.end_day.get() else None
            )
            
            if not date_range.is_valid():
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("invalid_date_range")
                )
                return None
                
            return date_range
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_date_validation", error=str(e))
            messagebox.showerror(
                self.translation_manager.get_text("error"),
                str(e)
            )
            return None

    def validate_prize_name(self, action, text_before, text_after) -> bool:
        """Validazione nome premio"""
        if not text_after or len(text_after) <= 20:  # lunghezza massima 20 caratteri
            return True
        messagebox.showerror(
            self.translation_manager.get_text("error"),
            self.translation_manager.get_text("prize_name_too_long")
        )
        return False

    def validate_quantity(self, action, text_before, text_after) -> bool:
        """Validazione quantità premio"""
        try:
            if not text_after:
                return True

            if text_after == '#':  # Permetti il cancelletto
                return True
                    
            try:
                quantity = float(text_after)
                if quantity <= 0:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("quantity_must_be_positive")
                    )
                    return False
                        
                if self.integer_only.get() and not quantity.is_integer():
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("quantity_must_be_integer")
                    )
                    return False
                        
                return True
            except ValueError:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("quantity_must_be_number")
                )
                return False
        except Exception as e:
            self.translation_manager.log("error", "log_error_quantity_validation", error=str(e))
            return False

    def validate_winners(self, value: str) -> bool:
        """Validazione numero vincitori"""
        try:
            if not value.strip():
                return True
                
            try:
                winners = int(value)
                if winners < 1:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("winners_must_be_positive")
                    )
                    return False
                    
                # Controlliamo il numero di vincitori solo se ci sono partecipanti
                if self.participants:
                    if winners > len(self.participants):
                        messagebox.showerror(
                            self.translation_manager.get_text("error"),
                            self.translation_manager.get_text("winners_exceed_participants")
                        )
                        return False
                        
                return True
            except ValueError:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("winners_must_be_integer")
                )
                return False
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_validating_winners", error=str(e))
            return False

    def validate_participant_name(self, action, text_before, text_after) -> bool:
        """Validazione nome partecipante (solo lunghezza massima)"""
        if not text_after or len(text_after) <= 20:  # lunghezza massima 20 caratteri
            return True
        messagebox.showerror(
            self.translation_manager.get_text("error"),
            self.translation_manager.get_text("participant_name_too_long")
        )
        return False

    def validate_damage(self, action, text_before, text_after) -> bool:
        """Validazione danni partecipante"""
        try:
            if not text_after:
                return True

            if text_after == '#':  # Permetti il cancelletto
                return True
                    
            try:
                damage = float(text_after)
                if damage < 0:  # Allow 0 damage
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("damage_must_be_non_negative")
                    )
                    return False
                        
                return True
            except ValueError:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("damage_must_be_number")
                )
                return False
        except Exception as e:
            self.translation_manager.log("error", "log_error_damage_validation", error=str(e))
            return False

    def on_tab_changed(self, event):
        """Gestione cambio tab"""
        try:
            current_tab = self.notebook.select()
            tab_id = self.notebook.index(current_tab)
            
            # Se selezionata tab distribuzione
            if tab_id == 2:  # Distribution tab
                # Auto-seleziona primo premio se ci sono partecipanti e premi
                if self.participants and self.prizes:
                    self.prize_selector_frame.pack(side="left", fill="x", expand=True)
                    # Aggiorna valori selettore premio
                    self.prize_selector['values'] = [f"{p.id}: {p.name}" for p in self.prizes]
                    # Seleziona primo premio se nessuno selezionato
                    if not self.selected_prize.get() and self.prizes:
                        self.prize_selector.set(self.prize_selector['values'][0])
                        self.update_distribution()
                else:
                    # Nasconde selettore premio se non ci sono partecipanti o premi
                    self.prize_selector_frame.pack_forget()
                    self.selected_prize.set('')
                    
        except Exception as e:
            self.translation_manager.log("error", "log_error_tab_changed", error=str(e))

    def update_ui_text(self):
        """Aggiornamento testi interfaccia"""
        try:
            # Titolo finestra
            self.root.title(self.translation_manager.get_text("title"))

            # Settings button
            self.settings_button.configure(text=self.translation_manager.get_text("settings"))
            
            # Titoli tab
            self.notebook.tab(0, text=self.translation_manager.get_text("prizes"))
            self.notebook.tab(1, text=self.translation_manager.get_text("participants"))
            self.notebook.tab(2, text=self.translation_manager.get_text("distribution"))
            self.notebook.tab(3, text=self.translation_manager.get_text("history"))
            
            # Frame stato corrente
            self.current_state_frame.configure(
                text=self.translation_manager.get_text("current_state")
            )
            
            # Frame template
            self.template_frame.configure(
                text=self.translation_manager.get_text("load_template")
            )
            
            # Aggiorna etichette date
            self.year_label.configure(text=self.translation_manager.get_text("year"))
            self.start_date_label.configure(text=self.translation_manager.get_text("start_date"))
            self.end_date_label.configure(text=self.translation_manager.get_text("end_date"))
            self.use_date_range_check.configure(text=self.translation_manager.get_text("use_date_range"))

            # Aggiorna bottoni
            self.clear_prizes_button.configure(text=self.translation_manager.get_text("clear"))
            self.clear_participants_button.configure(text=self.translation_manager.get_text("clear"))
            self.add_prizes_button.configure(text=self.translation_manager.get_text("add"))
            self.add_participant_button.configure(text=self.translation_manager.get_text("add"))
            self.save_state_button.configure(text=self.translation_manager.get_text("save_state"))
            self.update_state_button.configure(text=self.translation_manager.get_text("update_state"))

            # Template frame buttons
            self.load_prizes_button.configure(text=self.translation_manager.get_text("load_prizes"))
            self.load_participants_button.configure(text=self.translation_manager.get_text("load_participants"))
            
            # Event label
            self.event_label.configure(text=self.translation_manager.get_text("event"))
            
            # Prizes tab
            self.single_input_radio.configure(text=self.translation_manager.get_text("single_input"))
            self.batch_input_radio.configure(text=self.translation_manager.get_text("batch_input"))
            self.batch_format_label.configure(text=self.translation_manager.get_text("batch_prize_format"))
            self.batch_example_label.configure(text=self.translation_manager.get_text("batch_prize_example"))
            self.prize_delete_info.configure(text=self.translation_manager.get_text("delete_with_hash"))
            self.prize_name_label.configure(text=self.translation_manager.get_text("prize_name"))
            self.quantity_label.configure(text=self.translation_manager.get_text("quantity"))
            self.special_prize_check.configure(text=self.translation_manager.get_text("special_prize"))
            self.top_winners_label.configure(text=self.translation_manager.get_text("top_winners"))
            
            # Participants tab
            self.single_participant_radio.configure(text=self.translation_manager.get_text("single_input"))
            self.batch_participant_radio.configure(text=self.translation_manager.get_text("batch_input"))
            self.participant_format_label.configure(text=self.translation_manager.get_text("batch_participant_format"))
            self.participant_example_label.configure(text=self.translation_manager.get_text("batch_participant_example"))
            self.participant_delete_info.configure(text=self.translation_manager.get_text("delete_with_hash"))
            self.participant_label.configure(text=self.translation_manager.get_text("participant"))
            self.damage_label.configure(text=self.translation_manager.get_text("damage"))
            self.enabled_check.configure(text=self.translation_manager.get_text("enabled"))
            
            # History tab filters
            self.filter_frame.configure(text=self.translation_manager.get_text("filters"))
            self.history_year_label.configure(text=self.translation_manager.get_text("year"))
            self.history_month_label.configure(text=self.translation_manager.get_text("month"))
            self.history_event_label.configure(text=self.translation_manager.get_text("event"))
            
            # Aggiorna combo mesi
            self.update_month_values()
            
            # Aggiorna tabelle
            self.update_tables()
            
            self.translation_manager.log("debug", "log_ui_text_updated")
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_ui_text", error=str(e))
            raise

    def update_tables(self):
        """Aggiornamento di tutte le tabelle dell'interfaccia"""
        try:
            # Pulisce le tabelle
            for table in [self.prizes_table, self.participants_table, self.distribution_table]:
                if table:  # Verifica che la tabella esista
                    for item in table.get_children():
                        table.delete(item)
            
            # Aggiorna tabella premi
            for prize in self.prizes:
                self.prizes_table.insert("", "end", values=(
                    prize.id,
                    prize.name,
                    self.format_number(prize.quantity),
                    "✓" if prize.is_special else "",
                    prize.top_winners if prize.is_special else "",
                    "✎",  # edit
                    "✖"   # delete
                ), tags=("center",))
            
            # Aggiorna tabella partecipanti
            active_participants = [p for p in self.participants if p.enabled and 
                            not (isinstance(p.damage, str) and p.damage.strip() == '#')]
            total_damage = sum(p.damage for p in active_participants) if active_participants else 0
            
            for participant in self.participants:
                if isinstance(participant.damage, str) and participant.damage.strip() == '#':
                    percentage = 0
                    damage_display = '#'
                elif participant.enabled and total_damage > 0:
                    percentage = (participant.damage / total_damage * 100)
                    damage_display = self.format_number(participant.damage)
                else:
                    percentage = 0
                    damage_display = self.format_number(participant.damage)
                    
                self.participants_table.insert("", "end", values=(
                    participant.id,
                    participant.name,
                    damage_display,
                    f"{percentage:.2f}%",
                    "✓" if participant.enabled else "✗",
                    "✎",  # edit
                    "✖",  # delete
                    "☐" if participant.enabled else "☑"  # toggle
                ), tags=("center",))

            # Aggiorna label danni totali
            if hasattr(self, 'total_damage_label') and self.total_damage_label:
                self.total_damage_label.configure(
                    text=f"{self.translation_manager.get_text('total_damage')}: {self.format_number(total_damage)}"
                )
            
            # Aggiorna pulsanti salva e aggiorna
            self.check_save_buttons_state()

        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_tables", error=str(e))
            print(f"Error updating tables: {str(e)}")
            print(traceback.format_exc())

    def update_button_states(self):
        """Aggiorna lo stato dei pulsanti in base al contenuto delle liste"""
        try:
            # Per i premi
            if hasattr(self, 'clear_prizes_button'):
                self.clear_prizes_button["state"] = "normal" if self.prizes else "disabled"
            
            # Per i partecipanti
            if hasattr(self, 'clear_participants_button'):
                self.clear_participants_button["state"] = "normal" if self.participants else "disabled"
                
            self.translation_manager.log("debug", "log_button_states_updated",
                prizes_count=len(self.prizes),
                participants_count=len(self.participants))
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_button_states", error=str(e))

    def update_add_button_states(self):
        """Aggiorna lo stato dei pulsanti aggiungi in base al contenuto dei campi"""
        try:
            # Per i premi
            if self.prize_input_mode.get() == "single":
                # Controlla se c'è del testo in almeno uno dei campi
                has_content = bool(self.prize_name_entry.get().strip() or 
                                self.prize_quantity_entry.get().strip())
                self.add_prizes_button["state"] = "normal" if has_content else "disabled"
            else:
                # Modalità batch
                has_content = bool(self.prize_text.get("1.0", "end-1c").strip())
                self.add_prizes_button["state"] = "normal" if has_content else "disabled"

            # Per i partecipanti
            if self.participant_input_mode.get() == "single":
                # Controlla se c'è del testo in almeno uno dei campi
                has_content = bool(self.participant_name_entry.get().strip() or 
                                self.participant_damage_entry.get().strip())
                self.add_participant_button["state"] = "normal" if has_content else "disabled"
            else:
                # Modalità batch
                has_content = bool(self.participant_text.get("1.0", "end-1c").strip())
                self.add_participant_button["state"] = "normal" if has_content else "disabled"

        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_add_button_states", error=str(e))
    
    def update_current_state(self):
        """Aggiornamento dello stato corrente con validazioni complete"""
        try:
            event_name = self.event_var.get().strip()
            # Verifica che il nome evento sia presente
            if not event_name:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("event_required")
                )
                return

            # Validazione iniziale
            try:
                date_range = self.validate_date_range()
                if not date_range:
                    return
                    
                # Verifica esistenza evento con queste date specifiche
                existing_state = next((s for s in self.saved_states
                                if s.event == event_name and
                                s.date_range.start_year == date_range.start_year and
                                s.date_range.start_month == date_range.start_month and
                                s.date_range.start_day == date_range.start_day and
                                s.date_range.end_year == date_range.end_year and
                                s.date_range.end_month == date_range.end_month and
                                s.date_range.end_day == date_range.end_day), None)
                                
                if not existing_state:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("state_not_found_with_dates")
                    )
                    return

                # Ottieni i nomi degli elementi esistenti
                existing_participant_names = {p.name for p in self.participants}
                existing_prize_names = {p.name for p in self.prizes}

                # Verifica se ci sono elementi mancanti
                missing_participants = {p.name for p in existing_state.participants} - existing_participant_names
                missing_prizes = {p.name for p in existing_state.prizes} - existing_prize_names

                # Se ci sono elementi mancanti, mostra il messaggio
                if missing_participants or missing_prizes:
                    if not messagebox.askyesno(
                        self.translation_manager.get_text("info"),
                        self.translation_manager.get_text("state_incomplete_load")
                    ):
                        return

                    state_compared = False

                    # Verifica e aggiornamento premi esistenti
                    for prize in self.prizes:
                        existing_prize = next(
                            (p for p in existing_state.prizes if p.name == prize.name), 
                            None
                        )
                        if existing_prize:
                            existing_prize.quantity = prize.quantity
                            existing_prize.is_special = prize.is_special
                            existing_prize.top_winners = prize.top_winners
                        else:
                            max_id = max(p.id for p in existing_state.prizes)
                            prize.id = max_id + 1

                    # Aggiungi premi mancanti dallo stato
                    for p in existing_state.prizes:
                        if p.name not in existing_prize_names:
                            prize = Prize(
                                id=self.next_prize_id,
                                name=p.name,
                                quantity=p.quantity,
                                is_special=p.is_special,
                                top_winners=p.top_winners
                            )
                            self.prizes.append(prize)
                            self.next_prize_id += 1

                    # Verifica e aggiornamento partecipanti esistenti
                    for participant in self.participants:
                        existing_participant = next(
                            (p for p in existing_state.participants if p.name == participant.name), 
                            None
                        )
                        if existing_participant:
                            existing_participant.damage = participant.damage
                            existing_participant.enabled = participant.enabled
                        else:
                            max_id = max(p.id for p in existing_state.participants)
                            participant.id = max_id + 1

                    # Aggiungi partecipanti mancanti dallo stato
                    for p in existing_state.participants:
                        if p.name not in existing_participant_names:
                            participant = Participant(
                                id=self.next_participant_id,
                                name=p.name,
                                damage=p.damage,
                                enabled=p.enabled
                            )
                            self.participants.append(participant)
                            self.next_participant_id += 1

                    # Aggiorna interfaccia
                    self.update_tables()
                    self.update_button_states()
                    self.check_save_buttons_state()
                    state_compared = True
                    return

            except Exception as e:
                self.translation_manager.log("error", "log_error_date_validation", error=str(e))
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    str(e)
                )
                return

            # Lista degli elementi da eliminare
            prizes_to_remove = []
            participants_to_remove = []

            # Verifica e aggiorna gli elementi
            has_changes = False

            if self.prizes:
                updated_prizes = existing_state.prizes.copy()
                for new_prize in self.prizes:
                    if isinstance(new_prize.quantity, str) and new_prize.quantity.strip() == '#':
                        # Marca il premio per la rimozione
                        prizes_to_remove.append(new_prize.name)
                        has_changes = True
                    else:
                        # Gestione normale aggiornamento/aggiunta
                        existing_prize = next((p for p in updated_prizes if p.name == new_prize.name), None)
                        if existing_prize:
                            existing_prize.quantity = new_prize.quantity
                            existing_prize.is_special = new_prize.is_special
                            existing_prize.top_winners = new_prize.top_winners
                            has_changes = True
                        else:
                            updated_prizes.append(new_prize)
                            has_changes = True

                # Rimuovi i premi marcati per l'eliminazione
                updated_prizes = [p for p in updated_prizes if p.name not in prizes_to_remove]

                # Verifica se è l'ultimo premio
                if len(updated_prizes) == 0 and len(prizes_to_remove) > 0:
                    if messagebox.askyesno(
                        self.translation_manager.get_text("confirm"),
                        self.translation_manager.get_text("confirm_delete_last_prize")
                    ):
                        # Elimina l'intero stato
                        self.saved_states.remove(existing_state)
                        # Rimuovi il file
                        filename = f"{existing_state.date_range}__{existing_state.event}.json"
                        filepath = os.path.join(self.data_folder, filename)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        return
                    else:
                        return

            if self.participants:
                updated_participants = existing_state.participants.copy()
                for new_participant in self.participants:
                    if isinstance(new_participant.damage, str) and new_participant.damage.strip() == '#':
                        # Marca il partecipante per la rimozione
                        participants_to_remove.append(new_participant.name)
                        has_changes = True
                    else:
                        # Gestione normale aggiornamento/aggiunta
                        existing_participant = next((p for p in updated_participants if p.name == new_participant.name), None)
                        if existing_participant:
                            existing_participant.damage = new_participant.damage
                            existing_participant.enabled = new_participant.enabled
                            has_changes = True
                        else:
                            updated_participants.append(new_participant)
                            has_changes = True

                # Rimuovi i partecipanti marcati per l'eliminazione
                updated_participants = [p for p in updated_participants if p.name not in participants_to_remove]

                # Verifica se è l'ultimo partecipante
                if len(updated_participants) == 0 and len(participants_to_remove) > 0:
                    if messagebox.askyesno(
                        self.translation_manager.get_text("confirm"),
                        self.translation_manager.get_text("confirm_delete_last_participant")
                    ):
                        # Elimina l'intero stato
                        self.saved_states.remove(existing_state)
                        # Rimuovi il file
                        filename = f"{existing_state.date_range}__{existing_state.event}.json"
                        filepath = os.path.join(self.data_folder, filename)
                        if os.path.exists(filepath):
                            os.remove(filepath)
                        return
                    else:
                        return

            if not has_changes:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("no_elements_to_update")
                )
                return

            if messagebox.askyesno(
                self.translation_manager.get_text("confirm"),
                self.translation_manager.get_text("confirm_update")
            ):
                try:
                    # Calcola distribuzioni per gli elementi presenti
                    all_distributions = {}
                    
                    # Se ci sono premi, calcola le loro distribuzioni
                    if self.prizes:
                        # Seleziona i partecipanti attivi escludendo quelli con cancelletto
                        active_participants = [p for p in self.participants if p.enabled and 
                                            not (isinstance(p.damage, str) and p.damage.strip() == '#')] if self.participants else \
                                            [p for p in existing_state.participants if p.enabled and 
                                            not (isinstance(p.damage, str) and p.damage.strip() == '#')]
                                            
                        # Calcola il danno totale solo per i partecipanti validi
                        total_damage = sum(p.damage for p in active_participants)
                        
                        for prize in self.prizes:
                            if active_participants and total_damage > 0:
                                distributions = []
                                if prize.is_special:
                                    # Logica per premi speciali
                                    top_participants = sorted(active_participants,
                                                        key=lambda p: p.damage, 
                                                        reverse=True)[:prize.top_winners]
                                    winner_total_damage = sum(p.damage for p in top_participants)
                                    
                                    for participant in top_participants:
                                        ratio = participant.damage / winner_total_damage
                                        quantity = (prize.quantity * ratio) if not self.integer_only.get() \
                                                else max(1, round(prize.quantity * ratio))
                                        distributions.append((participant.name, quantity))
                                else:
                                    # Logica per premi normali
                                    for participant in active_participants:
                                        ratio = participant.damage / total_damage
                                        quantity = (prize.quantity * ratio) if not self.integer_only.get() \
                                                else max(1, round(prize.quantity * ratio))
                                        distributions.append((participant.name, quantity))
                                
                                all_distributions[prize.id] = distributions
                    else:
                        # Mantieni le distribuzioni esistenti per i premi non modificati
                        all_distributions = existing_state.distributions

                    # Chiedi se aggiornare le opzioni di immissione
                    if messagebox.askyesno(
                        self.translation_manager.get_text("confirm"),
                        self.translation_manager.get_text("update_input_options")
                    ):
                        # Crea dialog per modifica opzioni
                        dialog = tk.Toplevel(self.root)
                        dialog.title(self.translation_manager.get_text("update_options"))
                        dialog.geometry("400x500")
                        self.center_dialog(dialog)
                        dialog.grab_set()

                        # Frame principale
                        main_frame = ttk.Frame(dialog, padding=20)
                        main_frame.pack(fill="both", expand=True)

                        # Anno
                        year_frame = ttk.Frame(main_frame)
                        year_frame.pack(fill="x", pady=5)
                        ttk.Label(year_frame, text=self.translation_manager.get_text("year")).pack(side="left")
                        year_var = tk.StringVar(value=str(existing_state.date_range.start_year))
                        year_combo = ttk.Combobox(
                            year_frame,
                            textvariable=year_var,
                            values=[str(y) for y in range(2020, datetime.now().year + 2)],
                            state="readonly",
                            width=6
                        )
                        year_combo.pack(side="left", padx=5)

                        # Date range
                        date_range_var = tk.BooleanVar(value=True if existing_state.date_range.end_month else False)
                        ttk.Checkbutton(
                            main_frame,
                            text=self.translation_manager.get_text("use_date_range"),
                            variable=date_range_var,
                            command=lambda: toggle_date_range()
                        ).pack(pady=5)

                        # Date frames
                        start_frame = ttk.LabelFrame(main_frame, text=self.translation_manager.get_text("start_date"))
                        start_frame.pack(fill="x", pady=5)
                        
                        end_frame = ttk.LabelFrame(main_frame, text=self.translation_manager.get_text("end_date"))

                        # Start date
                        start_month_var = tk.StringVar(value=f"{existing_state.date_range.start_month:02d}")
                        start_month_combo = ttk.Combobox(
                            start_frame,
                            textvariable=start_month_var,
                            values=[f"{i:02d}" for i in range(1, 13)],
                            state="readonly",
                            width=5
                        )
                        start_month_combo.pack(side="left", padx=5)

                        start_day_var = tk.StringVar(value=str(existing_state.date_range.start_day or ""))
                        start_day_combo = ttk.Combobox(
                            start_frame,
                            textvariable=start_day_var,
                            state="readonly",
                            width=5
                        )
                        start_day_combo.pack(side="left", padx=5)

                        # End date
                        end_month_var = tk.StringVar(value=f"{existing_state.date_range.end_month:02d}" if existing_state.date_range.end_month else "")
                        end_month_combo = ttk.Combobox(
                            end_frame,
                            textvariable=end_month_var,
                            values=[f"{i:02d}" for i in range(1, 13)],
                            state="readonly",
                            width=5
                        )
                        end_month_combo.pack(side="left", padx=5)

                        end_day_var = tk.StringVar(value=str(existing_state.date_range.end_day or ""))
                        end_day_combo = ttk.Combobox(
                            end_frame,
                            textvariable=end_day_var,
                            state="readonly",
                            width=5
                        )
                        end_day_combo.pack(side="left", padx=5)

                        # Event name
                        name_frame = ttk.LabelFrame(main_frame, text=self.translation_manager.get_text("event"))
                        name_frame.pack(fill="x", pady=5)
                        name_var = tk.StringVar(value=existing_state.event)
                        ttk.Entry(name_frame, textvariable=name_var).pack(fill="x", padx=5, pady=5)

                        def toggle_date_range():
                            if date_range_var.get():
                                end_frame.pack(fill="x", pady=5, before=name_frame)
                            else:
                                end_frame.pack_forget()
                                end_month_var.set("")
                                end_day_var.set("")

                        def update_days(*args):
                            # Update start days
                            if start_month_var.get():
                                month = int(start_month_var.get())
                                year = int(year_var.get())
                                _, last_day = monthrange(year, month)
                                start_day_combo['values'] = [f"{d:02d}" for d in range(1, last_day + 1)]
                            
                            # Update end days
                            if end_month_var.get():
                                month = int(end_month_var.get())
                                year = int(year_var.get())
                                _, last_day = monthrange(year, month)
                                end_day_combo['values'] = [f"{d:02d}" for d in range(1, last_day + 1)]

                        # Bind updates
                        start_month_combo.bind('<<ComboboxSelected>>', update_days)
                        end_month_combo.bind('<<ComboboxSelected>>', update_days)
                        year_combo.bind('<<ComboboxSelected>>', update_days)

                        # Initial toggle
                        toggle_date_range()
                        update_days()

                        def validate_and_update():
                            try:
                                # Validate dates
                                start_month = int(start_month_var.get())
                                start_day = int(start_day_var.get()) if start_day_var.get() else None
                                year = int(year_var.get())
                                
                                end_month = None
                                end_day = None
                                if date_range_var.get():
                                    if end_month_var.get():
                                        end_month = int(end_month_var.get())
                                        if end_day_var.get():
                                            end_day = int(end_day_var.get())

                                # Create date range
                                new_date_range = DateRange(
                                    start_year=year,
                                    start_month=start_month,
                                    start_day=start_day,
                                    end_year=year if end_month else None,
                                    end_month=end_month,
                                    end_day=end_day
                                )

                                # Validate date range
                                if not new_date_range.is_valid():
                                    messagebox.showerror(
                                        self.translation_manager.get_text("error"),
                                        self.translation_manager.get_text("invalid_date_range")
                                    )
                                    return False

                                # Validate event name
                                new_name = name_var.get().strip()
                                if len(new_name) < 3:
                                    messagebox.showerror(
                                        self.translation_manager.get_text("error"),
                                        self.translation_manager.get_text("event_name_too_short")
                                    )
                                    return False

                                # Check for conflicts
                                if new_name != existing_state.event:
                                    for state in self.saved_states:
                                        if state != existing_state and state.event == new_name:
                                            if new_date_range.overlaps(state.date_range):
                                                messagebox.showerror(
                                                    self.translation_manager.get_text("error"),
                                                    self.translation_manager.get_text("date_collision")
                                                )
                                                return False

                                return new_date_range, new_name
                            except ValueError:
                                messagebox.showerror(
                                    self.translation_manager.get_text("error"),
                                    self.translation_manager.get_text("invalid_input")
                                )
                                return False

                        def on_confirm():
                            if messagebox.askyesno(
                                self.translation_manager.get_text("confirm"),
                                self.translation_manager.get_text("confirm_update_options"), # "Confermi l'aggiornamento delle opzioni di immissione?"
                                parent=dialog 
                            ):

                                result = validate_and_update()
                                if result:
                                    new_date_range, new_name = result
                                    dialog.result = ("confirm", new_date_range, new_name)
                                    dialog.destroy()

                        def on_ignore():
                            if messagebox.askyesno(
                                self.translation_manager.get_text("confirm"),
                                self.translation_manager.get_text("confirm_update_options"),
                                parent=dialog 
                            ):
                                if messagebox.askyesno(
                                    self.translation_manager.get_text("confirm"),
                                    self.translation_manager.get_text("ignore_update_options")  # "Vuoi ignorare le modifiche alle opzioni di immissione? Le modifiche ai dati verranno comunque salvate"
                                ):
                                    dialog.result = ("ignore", None, None)
                                    dialog.destroy()

                        def on_cancel():
                            if messagebox.askyesno(
                                self.translation_manager.get_text("confirm"),
                                self.translation_manager.get_text("confirm_update_options"),
                                parent=dialog 
                            ):
                                if messagebox.askyesno(
                                    self.translation_manager.get_text("confirm"),
                                    self.translation_manager.get_text("cancel_all_updates")  # "Vuoi annullare tutte le modifiche? Nessuna modifica verrà salvata"
                                ):
                                    dialog.result = ("cancel", None, None)
                                    dialog.destroy()

                        # Buttons
                        button_frame = ttk.Frame(main_frame)
                        button_frame.pack(fill="x", pady=10)
                        
                        ttk.Button(button_frame, text=self.translation_manager.get_text("confirm"), command=on_confirm).pack(side="left", padx=5)
                        ttk.Button(button_frame, text=self.translation_manager.get_text("ignore"), command=on_ignore).pack(side="left", padx=5)
                        ttk.Button(button_frame, text=self.translation_manager.get_text("cancel"), command=on_cancel).pack(side="right", padx=5)

                        # Wait for dialog result
                        dialog.wait_window()
                        
                        if hasattr(dialog, 'result'):
                            action, new_date_range, new_name = dialog.result
                            
                            if action == "cancel":
                                return
                            elif action == "confirm":
                                # Update date range and name
                                date_range = new_date_range
                                event_name = new_name
                            # If ignore, keep original values
                            else:
                                date_range = existing_state.date_range
                        else:
                            return
                    else:
                        # Keep original date range and name
                        date_range = existing_state.date_range

                    # Create updated state
                    state = SavedState(
                        date_range=date_range,
                        event=event_name,
                        prizes=self.prizes if self.prizes else existing_state.prizes,
                        participants=self.participants if self.participants else existing_state.participants,
                        distributions=all_distributions,
                        saved_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                        total_damage=sum(p.damage for p in (self.participants if self.participants else existing_state.participants))
                    )

                    # Update file
                    filename = f"{date_range}__{event_name}.json"
                    filepath = os.path.join(self.data_folder, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(state.to_dict(), f, indent=2)

                    # Delete old file if name changed
                    if event_name != existing_state.event:
                        old_filename = f"{existing_state.date_range}__{existing_state.event}.json"
                        old_filepath = os.path.join(self.data_folder, old_filename)
                        if os.path.exists(old_filepath):
                            os.remove(old_filepath)

                    # Update state in memory
                    idx = self.saved_states.index(existing_state)
                    self.saved_states[idx] = state
                    
                    messagebox.showinfo(
                        self.translation_manager.get_text("info"),
                        self.translation_manager.get_text("state_updated")
                    )
                    
                    self.update_history_table()
                    self.update_history_filters()

                    # Pulisci i dati correnti
                    self.prizes = []
                    self.participants = []

                    # Reset degli ID
                    self.next_prize_id = 1
                    self.next_participant_id = 1

                    # Aggiorna le tabelle per mostrare che sono vuote
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    

                except Exception as e:
                    self.translation_manager.log("error", "log_error_update_state", error=str(e))
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("save_error")
                    )

        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_state", error=str(e))

    def clear_prizes(self):
        """Pulizia lista premi"""
        try:
            if self.prizes and messagebox.askyesno(
                self.translation_manager.get_text("confirm"),
                self.translation_manager.get_text("confirm_clear_prizes")
            ):
                self.prizes = []
                self.next_prize_id = 1
                self.update_tables()
                self.check_save_buttons_state()
                self.update_button_states()
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_clear_prizes", error=str(e))

    def clear_participants(self):
        """Pulizia lista partecipanti"""
        try:
            if self.participants and messagebox.askyesno(
                self.translation_manager.get_text("confirm"),
                self.translation_manager.get_text("confirm_clear_participants")
            ):
                self.participants = []
                self.next_participant_id = 1
                self.update_tables()
                self.check_save_buttons_state()
                self.update_button_states()
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_clear_participants", error=str(e))

    def update_month_values(self):
        """Aggiornamento valori mesi nelle combo"""
        try:
            months = [(f"{i:02d}", nome) for i, nome in
                     enumerate(self.translation_manager.get_text("months").split(","), 1)]
            month_values = [''] + [f"{m[0]} - {m[1]}" for m in months]
            
            # Salva selezioni correnti
            start_val = self.start_month.get()
            end_val = self.end_month.get()
            
            # Aggiorna valori
            for combo in [self.start_month, self.end_month]:
                current = combo.get()
                combo['values'] = month_values
                
                # Ripristina selezione se possibile
                if current and ' - ' in current:
                    month_num = current.split(' - ')[0]
                    for val in month_values:
                        if val.startswith(month_num):
                            combo.set(val)
                            break
                else:
                    combo.set('')
            
            self.translation_manager.log("debug", "log_month_values_updated")
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_months", error=str(e))
            raise

    def sort_table(self, table, col, reverse):
        """Sort treeview table by column"""
        try:
            col_idx = table["columns"].index(col)

            # Gestione speciale per la tabella storico
            if table == self.history_table:
                # Mantieni la logica esistente per la tabella storico
                events_data = []
                current_event = []
                
                for item in table.get_children(''):
                    values = [table.set(item, c) for c in table["columns"]]
                    if values[0] and values[1]:  # Se data e evento non sono vuoti
                        if current_event:
                            events_data.append(current_event)
                        current_event = [values]
                    else:
                        current_event.append(values)
                
                if current_event:
                    events_data.append(current_event)

                if len(events_data) == 1 and col not in ["date", "event"]:
                    return
                
                if col in ["date", "event"]:
                    events_data.sort(key=lambda x: x[0][col_idx], reverse=reverse)
                else:
                    return  # Non ordiniamo altre colonne
                
                for item in table.get_children(''):
                    table.delete(item)
                
                for event in events_data:
                    for row in event:
                        table.insert("", "end", values=row, tags=("center",))
            
            # Gestione per le altre tabelle (premi, partecipanti, distribuzione)
            else:
                l = [(table.set(k, col), k) for k in table.get_children('')]
                
                # Gestione specifica per colonne numeriche
                if table in [self.prizes_table, self.participants_table, self.distribution_table]:
                    numeric_columns = {
                        self.prizes_table: ["quantity", "top_winners"],
                        self.participants_table: ["damage"],
                        self.distribution_table: ["quantity"]
                    }
                    
                    if table in numeric_columns and col in numeric_columns[table]:
                        # Converte stringhe numeriche in float per il sorting
                        l = [(float(table.set(k, col).replace('%', '')) if table.set(k, col) and table.set(k, col) != '#' else -1, k) for k in table.get_children('')]
                    else:
                        # Sorting standard per colonne non numeriche
                        l = [(table.set(k, col), k) for k in table.get_children('')]
                
                # Ordina la lista
                l.sort(reverse=reverse)
                
                # Riordina gli elementi
                for index, (_, k) in enumerate(l):
                    table.move(k, '', index)

            # Imposta il comando per il prossimo click
            table.heading(col, command=lambda: self.sort_table(table, col, not reverse))

        except Exception as e:
            self.translation_manager.log("error", "log_error_sorting_table", error=str(e))

    def update_tables(self):
        """Aggiornamento di tutte le tabelle"""
        try:
            # Aggiorna intestazioni tabella premi
            self.update_prizes_table_headers()
            
            # Aggiorna intestazioni tabella partecipanti
            self.update_participants_table_headers()
            
            # Aggiorna intestazioni tabella distribuzione
            self.update_distribution_table_headers()
            
            # Aggiorna intestazioni tabella cronologia
            self.update_history_table_headers()
            
            # Aggiorna contenuto tabelle
            self.refresh_tables_content()
            
            self.translation_manager.log("debug", "log_tables_updated")
        except Exception as e:
            self.translation_manager.log("error", "log_error_updating_tables", error=str(e))
            raise

    def update_prizes_table_headers(self):
        """Aggiornamento intestazioni tabella premi"""
        try:
            headers = [
                ("id", "id", 50),
                ("name", "prize_name", 200),
                ("quantity", "quantity", 100),
                ("special", "special_prize", 100),
                ("winners", "winners", 100),
                ("edit", "edit", 50),
                ("delete", "delete", 50)
            ]
            
            for col, text_key, width in headers:
                self.prizes_table.heading(
                    col,
                    text=self.translation_manager.get_text(text_key)
                )
                
            self.translation_manager.log("debug", "log_prize_headers_updated")
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_headers", error=str(e))
            raise

    def handle_table_action(self, event, table_type: str):
        """Gestione azioni sulle tabelle"""
        try:
            if table_type not in ["prizes", "participants"]:
                raise ValueError("Invalid table type")
                
            table = (self.prizes_table if table_type == "prizes" 
                    else self.participants_table)
                    
            region = table.identify_region(event.x, event.y)
            if region != "cell":
                return
                
            row_id = table.identify_row(event.y)
            col_id = table.identify_column(event.x)
            
            if not row_id or not col_id:
                return
                
            values = table.item(row_id)['values']
            if not values:
                return
                
            item_id = values[0]
            
            # Gestione azioni in base al tipo di tabella
            if table_type == "prizes":
                self.handle_prize_table_action(col_id, item_id)
            else:
                self.handle_participant_table_action(col_id, item_id)
                
            self.translation_manager.log(
                "debug",
                "log_table_action_handled",
                table=table_type,
                action=col_id,
                item_id=item_id
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_table_action", error=str(e))
            raise

    def handle_prize_table_action(self, col_id: str, prize_id: int):
        """Gestione azioni tabella premi"""
        try:
            if col_id == "#6":  # edit
                self.edit_prize(prize_id)
            elif col_id == "#7":  # delete
                self.delete_prize(prize_id)
                
            self.translation_manager.log(
                "debug",
                "log_prize_action_handled",
                action="edit" if col_id == "#6" else "delete",
                prize_id=prize_id
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_prize_action", error=str(e))
            raise

    def edit_prize(self, prize_id: int):
        """Dialog modifica premio"""
        try:
            prize = next((p for p in self.prizes if p.id == prize_id), None)
            if not prize:
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("edit_prize"))
            dialog.geometry("400x350")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            content = ttk.Frame(dialog, padding=20)
            content.pack(fill="both", expand=True)
            
            # Nome
            name_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("prize_name")
            )
            name_frame.pack(fill="x", pady=5)
            
            name_entry = ttk.Entry(name_frame)
            name_entry.insert(0, prize.name)
            name_entry.pack(padx=5, pady=5)
            
            # Quantità
            quantity_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("quantity")
            )
            quantity_frame.pack(fill="x", pady=5)
            
            quantity_entry = ttk.Entry(quantity_frame)
            quantity_entry.insert(0, self.format_number(prize.quantity))
            quantity_entry.pack(padx=5, pady=5)
            
            # Premio speciale
            special_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("special_prize")
            )
            special_frame.pack(fill="x", pady=5)
            
            is_special_var = tk.BooleanVar(value=prize.is_special)
            special_check = ttk.Checkbutton(
                special_frame,
                text=self.translation_manager.get_text("special_prize"),
                variable=is_special_var
            )
            special_check.pack(padx=5, pady=5)
            
            # Vincitori
            winners_frame = ttk.Frame(special_frame)
            winners_label = ttk.Label(
                winners_frame,
                text=self.translation_manager.get_text("winners")
            )
            winners_label.pack(side="left", padx=5)
            
            winners_entry = ttk.Entry(winners_frame, width=5)
            winners_entry.insert(0, str(prize.top_winners))
            winners_entry.pack(side="left", padx=5)
            
            if prize.is_special:
                winners_frame.pack(pady=5)
            
            def toggle_winners(*args):
                if is_special_var.get():
                    winners_frame.pack(pady=5)
                else:
                    winners_frame.pack_forget()
                    
            is_special_var.trace_add("write", toggle_winners)
            
            # Pulsanti
            button_frame = ttk.Frame(content)
            button_frame.pack(fill="x", pady=20)
            
            def save_changes():
                try:
                    new_name = name_entry.get().strip()
                    if new_name != prize.name and self.check_name_exists(new_name, True):
                        self.show_validation_error("prize_name_exists")
                        return
                    
                    quantity_str = quantity_entry.get().strip()
                    try:
                        if quantity_str == '#':
                            quantity = quantity_str
                        else:
                            quantity = float(quantity_str)
                            if quantity <= 0:
                                self.show_validation_error("quantity_must_be_positive")
                                return
                    except ValueError:
                        self.show_validation_error("quantity_must_be_number")
                        return
                    
                    is_special = is_special_var.get()
                    if is_special:
                        try:
                            winners = int(winners_entry.get())
                            if winners < 1:
                                self.show_validation_error("winners_must_be_positive")
                                return
                        except ValueError:
                            self.show_validation_error("winners_must_be_integer")
                            return
                    
                    # Aggiorna premio
                    prize.name = new_name
                    prize.quantity = quantity
                    prize.is_special = is_special
                    prize.top_winners = int(winners_entry.get()) if is_special else 1
                    
                    self.update_tables()
                    dialog.destroy()
                    
                    self.translation_manager.log(
                        "info",
                        "log_prize_edited",
                        prize_id=prize.id,
                        name=prize.name
                    )
                except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_saving_prize",
                        error=str(e)
                    )
                    self.show_validation_error("save_error")
            
            save_button = ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("save"),
                command=save_changes
            )
            save_button.pack(side="left", padx=5)
            
            cancel_button = ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            )
            cancel_button.pack(side="right", padx=5)
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_edit_prize", error=str(e))
            raise

    def delete_prize(self, prize_id: int):
        """Eliminazione premio"""
        try:
            if messagebox.askyesno(
                self.translation_manager.get_text("confirm"),
                self.translation_manager.get_text("confirm_delete_prize")
            ):
                prize = next((p for p in self.prizes if p.id == prize_id), None)
                if prize:
                    self.prizes = [p for p in self.prizes if p.id != prize_id]
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    
                    self.translation_manager.log(
                        "info",
                        "log_prize_deleted",
                        prize_id=prize_id,
                        name=prize.name
                    )
        except Exception as e:
            self.translation_manager.log("error", "log_error_delete_prize", error=str(e))
            raise

    def update_participants_table_headers(self):
        """Aggiornamento intestazioni tabella partecipanti"""
        try:
            columns = [
                ("id", "id"),
                ("name", "participant"),
                ("damage", "damage"),
                ("percentage", "percentage"),
                ("enabled", "enabled"),
                ("edit", "edit"),
                ("delete", "delete"),
                ("toggle", "toggle")
            ]
            
            for col, text_key in columns:
                self.participants_table.heading(
                    col,
                    text=self.translation_manager.get_text(text_key)
                )
                
            self.translation_manager.log("debug", "log_participant_headers_updated")
            
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_participant_headers",
                error=str(e)
            )

    def handle_participant_table_action(self, col_id: str, participant_id: int):
        """Gestione azioni tabella partecipanti"""
        try:
            if col_id == "#6":  # edit
                self.edit_participant(participant_id)
            elif col_id == "#7":  # delete
                self.delete_participant(participant_id)
            elif col_id == "#8":  # toggle
                self.toggle_participant(participant_id)
                
            self.translation_manager.log(
                "debug",
                "log_participant_action_handled",
                action=col_id,
                participant_id=participant_id
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_participant_action", error=str(e))
            raise

    def edit_participant(self, participant_id: int):
        """Dialog modifica partecipante"""
        try:
            participant = next((p for p in self.participants if p.id == participant_id), None)
            if not participant:
                return
            
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("edit_participant"))
            dialog.geometry("400x300")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            content = ttk.Frame(dialog, padding=20)
            content.pack(fill="both", expand=True)
            
            # Nome
            name_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("participant_name")
            )
            name_frame.pack(fill="x", pady=5)
            
            name_entry = ttk.Entry(name_frame)
            name_entry.insert(0, participant.name)
            name_entry.pack(padx=5, pady=5)
            
            # Danni
            damage_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("damage")
            )
            damage_frame.pack(fill="x", pady=5)
            
            damage_entry = ttk.Entry(damage_frame)
            damage_entry.insert(0, self.format_number(participant.damage))
            damage_entry.pack(padx=5, pady=5)
            
            # Abilitato
            enabled_frame = ttk.LabelFrame(
                content,
                text=self.translation_manager.get_text("enabled")
            )
            enabled_frame.pack(fill="x", pady=5)
            
            enabled_var = tk.BooleanVar(value=participant.enabled)
            enabled_check = ttk.Checkbutton(
                enabled_frame,
                text=self.translation_manager.get_text("enabled"),
                variable=enabled_var
            )
            enabled_check.pack(padx=5, pady=5)
            
            # Pulsanti
            button_frame = ttk.Frame(content)
            button_frame.pack(fill="x", pady=20)
            
            def save_changes():
                try:
                    new_name = name_entry.get().strip()
                    if new_name != participant.name and self.check_name_exists(new_name, False):
                        self.show_validation_error("participant_name_exists")
                        return
                    
                    damage_str = damage_entry.get().strip()
                    try:
                        if damage_str == '#':
                            damage = damage_str
                        else:
                            damage = float(damage_str)
                            if damage < 0:  # Allow 0 damage
                                self.show_validation_error("damage_must_be_non_negative")
                                return
                    except ValueError:
                        self.show_validation_error("damage_must_be_number")
                        return
                    
                    # Aggiorna partecipante
                    participant.name = new_name
                    participant.damage = damage
                    participant.enabled = enabled_var.get()
                    
                    self.update_tables()
                    dialog.destroy()
                    
                    self.translation_manager.log(
                        "info",
                        "log_participant_edited",
                        participant_id=participant.id,
                        name=participant.name
                    )
                except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_saving_participant",
                        error=str(e)
                    )
                    self.show_validation_error("save_error")
            
            save_button = ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("save"),
                command=save_changes
            )
            save_button.pack(side="left", padx=5)
            
            cancel_button = ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            )
            cancel_button.pack(side="right", padx=5)
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_edit_participant", error=str(e))
            raise

    def delete_participant(self, participant_id: int):
        """Eliminazione partecipante"""
        try:
            if messagebox.askyesno(
                self.translation_manager.get_text("confirm"),
                self.translation_manager.get_text("confirm_delete_participant")
            ):
                participant = next((p for p in self.participants if p.id == participant_id), None)
                if participant:
                    self.participants = [p for p in self.participants if p.id != participant_id]
                    self.update_tables()
                    self.check_save_buttons_state()
                    self.update_button_states()
                    
                    self.translation_manager.log(
                        "info",
                        "log_participant_deleted",
                        participant_id=participant_id,
                        name=participant.name
                    )
        except Exception as e:
            self.translation_manager.log("error", "log_error_delete_participant", error=str(e))
            raise

    def toggle_participant(self, participant_id: int):
        """Toggle stato abilitato partecipante"""
        try:
            participant = next((p for p in self.participants if p.id == participant_id), None)
            if participant:
                participant.enabled = not participant.enabled
                self.update_tables()
                
                self.translation_manager.log(
                    "debug",
                    "log_participant_toggled",
                    participant_id=participant_id,
                    name=participant.name,
                    enabled=participant.enabled
                )
        except Exception as e:
            self.translation_manager.log("error", "log_error_toggle_participant", error=str(e))
            raise

    def refresh_tables_content(self):
        """Aggiornamento del contenuto di tutte le tabelle"""
        try:
            # Aggiorna tabella premi
            for item in self.prizes_table.get_children():
                self.prizes_table.delete(item)
                
            for prize in self.prizes:
                self.prizes_table.insert("", "end", values=(
                    prize.id,
                    prize.name,
                    self.format_number(prize.quantity),
                    "✓" if prize.is_special else "",
                    prize.top_winners if prize.is_special else "",
                    "✎",  # edit
                    "✖"   # delete
                ), tags=("center",))
                
            # Aggiorna tabella partecipanti
            for item in self.participants_table.get_children():
                self.participants_table.delete(item)

            active_participants = [p for p in self.participants if p.enabled and 
                                not (isinstance(p.damage, str) and p.damage.strip() == '#')]
            total_damage = sum(p.damage for p in active_participants) if active_participants else 0

            for participant in self.participants:
                if isinstance(participant.damage, str) and participant.damage.strip() == '#':
                    percentage = 0
                    damage_display = '#'
                elif participant.enabled and total_damage > 0:
                    percentage = (participant.damage / total_damage * 100)
                    damage_display = self.format_number(participant.damage)
                else:
                    percentage = 0
                    damage_display = self.format_number(participant.damage)
                    
                self.participants_table.insert("", "end", values=(
                    participant.id,
                    participant.name,
                    damage_display,
                    f"{percentage:.2f}%",
                    "✓" if participant.enabled else "✗",
                    "✎",  # edit
                    "✖",  # delete
                    "☐" if participant.enabled else "☑"  # toggle
                ), tags=("center",))
                
            # Aggiorna distribuzione se necessario
            if self.selected_prize.get():
                self.update_distribution()
                
            self.translation_manager.log("debug", "log_tables_content_refreshed")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_refreshing_tables", error=str(e))

    def update_distribution_table_headers(self):
        """Aggiornamento intestazioni tabella distribuzione"""
        try:
            columns = [
                ("id", "id", 50),
                ("participant", "participant", 300),
                ("quantity", "quantity", 150),
                ("check", "received", 50)
            ]
            
            for col, text_key, width in columns:
                self.distribution_table.heading(
                    col,
                    text=self.translation_manager.get_text(text_key)
                )
                
            self.translation_manager.log("debug", "log_distribution_headers_updated")
            
        except Exception as e:
            self.translation_manager.log(
                "error",
                "log_error_distribution_headers",
                error=str(e)
            )

    def save_current_state(self):
        """Salvataggio dello stato corrente con validazioni complete"""
        try:
            event_name = self.event_var.get().strip()
            
            # Validazioni
            if len(event_name) < 3:
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("event_name_too_short")
                )
                return

            if not self.start_month.get():
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("start_month_required")
                )
                return

            if not (self.prizes and self.participants):
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("prizes_and_participants_required")
                )
                return

            try:
                date_range = self.validate_date_range()
                if not date_range:
                    return

                # Verifica evento esistente
                existing_state = any(
                    state.event == event_name 
                    for state in self.saved_states
                )
                
                if existing_state:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("event_exists")
                    )
                    return

                # Calcola distribuzioni
                all_distributions = {}
                for prize in self.prizes:
                    distributions = self.calculate_distribution(prize)
                    all_distributions[prize.id] = [(name, qty) for name, qty in distributions]

                # Crea nuovo stato
                state = SavedState(
                    date_range=date_range,
                    event=event_name,
                    prizes=self.prizes.copy(),
                    participants=self.participants.copy(),
                    distributions=all_distributions,
                    saved_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    total_damage=sum(p.damage for p in self.participants)
                )

                # Salva su file
                filename = f"{date_range}__{event_name}.json"
                filepath = os.path.join(self.data_folder, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(state.to_dict(), f, indent=2)

                self.saved_states.append(state)

                messagebox.showinfo(
                    self.translation_manager.get_text("info"),
                    self.translation_manager.get_text("state_saved")
                )

                self.update_history_filters()
                self.update_history_table()
                self.prizes = []
                self.participants = []
                self.update_tables()

            except Exception as e:
                self.translation_manager.log("error", "log_error_saving_state", error=str(e))
                messagebox.showerror(
                    self.translation_manager.get_text("error"),
                    self.translation_manager.get_text("save_error")
                )

        except Exception as e:
            self.translation_manager.log("error", "log_error_save_current_state", error=str(e))
            raise

    def save_state_to_file(self, state: SavedState):
        """Salvataggio stato su file"""
        try:
            filename = f"{state.date_range}__{state.event}.json"
            filepath = os.path.join(self.data_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
                
            self.translation_manager.log(
                "debug",
                "log_state_file_saved",
                filename=filename
            )
        except Exception as e:
            self.translation_manager.log("error", "log_error_saving_file", error=str(e))
            raise

    def load_saved_states(self):
        """Caricamento degli stati salvati"""
        try:
            self.saved_states.clear()
            if not os.path.exists(self.data_folder):
                return
            
            for filename in os.listdir(self.data_folder):
                # Ignora i file che non sono JSON
                if not filename.endswith('.json'):
                    continue

                filepath = os.path.join(self.data_folder, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Verifica che sia un file di stato valido e non un tag XML
                    if not isinstance(data, dict) or data.get("userStyle", None):
                        continue
                        
                    if "event" not in data:
                        raise ValueError(f"Campo 'event' mancante nel file: {filename}")
                        
                    state = SavedState.from_dict(data)
                    self.saved_states.append(state)
                    
                    self.translation_manager.log(
                        "debug",
                        "log_state_loaded",
                        filename=filename
                    )
                        
                except json.JSONDecodeError:
                    # Ignora file JSON non validi
                    continue
                except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_loading_state",
                        error=str(e)
                    )
            
            self.update_history_filters()
            self.update_history_table()
            
            self.translation_manager.log(
                "info",
                "log_states_loaded",
                count=len(self.saved_states)
            )
        except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_loading_state",
                        error=f"{str(e)} - File: {filename} - Content: {data if 'data' in locals() else 'No data loaded'}"
                    )

    def center_dialog(self, dialog):
        """Centra una finestra di dialogo"""
        try:
            dialog.update_idletasks()
            
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            
            screen_width = dialog.winfo_screenwidth()
            screen_height = dialog.winfo_screenheight()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_centering_dialog", error=str(e))

    def new_state(self):
        """Crea nuovo stato"""
        try:
            if self.prizes or self.participants:
                if not messagebox.askyesno(
                    self.translation_manager.get_text("confirm"),
                    self.translation_manager.get_text("confirm_new_state")
                ):
                    return
            
            # Reset dati
            self.prizes = []
            self.participants = []
            self.next_prize_id = 1
            self.next_participant_id = 1
            
            # Reset campi
            self.event_var.set("")
            self.year_var.set(str(datetime.now().year))
            self.start_month.set("")
            self.end_month.set("")
            self.start_day.set("")
            self.end_day.set("")
            
            # Aggiorna interfaccia
            self.update_tables()
            self.check_save_buttons_state()
            
            self.translation_manager.log("info", "log_new_state_created")
        except Exception as e:
            self.translation_manager.log("error", "log_error_creating_new_state", error=str(e))
            raise

    def save_preferences(self, dialog):
        """Salvataggio preferenze"""
        try:
            preferences = {
                # Preferenze generali
                "default_language": self.translation_manager.current_language,
                "data_folder": self.data_folder,
                "auto_save": self.get_preference("auto_save", False),
                
                # Preferenze visualizzazione
                "theme": self.get_preference("theme", "system"),
                "font_size": self.get_preference("font_size", 10),
                "row_height": self.get_preference("row_height", 30),
                
                # Preferenze backup
                "auto_backup": self.get_preference("auto_backup", True),
                "backup_interval": self.get_preference("backup_interval", 30),
                "backup_folder": self.get_preference("backup_folder", "backups"),
                "backup_retention": self.get_preference("backup_retention", 10)
            }
            
            # Salva su file
            with open("preferences.json", "w", encoding="utf-8") as f:
                json.dump(preferences, f, indent=4)
            
            # Applica preferenze
            self.apply_preferences(preferences)
            
            dialog.destroy()
            
            self.translation_manager.log("info", "log_preferences_saved")
            self.set_status_message("preferences_saved")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_saving_preferences", error=str(e))
            self.show_validation_error("preferences_save_error")
            raise

    def load_preferences(self):
        """Caricamento preferenze"""
        try:
            if os.path.exists("preferences.json"):
                with open("preferences.json", "r", encoding="utf-8") as f:
                    preferences = json.load(f)
                self.apply_preferences(preferences)
                
                self.translation_manager.log("info", "log_preferences_loaded")
            else:
                # Carica preferenze di default
                self.apply_preferences({})
                
                self.translation_manager.log("info", "log_default_preferences_loaded")
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_loading_preferences", error=str(e))
            # Continua con preferenze di default
            self.apply_preferences({})

    def apply_preferences(self, preferences: dict):
        """Applicazione preferenze"""
        try:
            # Applica lingua
            if language := preferences.get("default_language"):
                self.translation_manager.current_language = language
            
            # Applica tema
            if theme := preferences.get("theme"):
                self.apply_theme(theme)
            
            # Applica font size
            if font_size := preferences.get("font_size"):
                self.apply_font_size(font_size)
            
            # Applica altezza righe
            if row_height := preferences.get("row_height"):
                style = ttk.Style()
                style.configure("Treeview", rowheight=row_height)
            
            # Setup backup automatico
            if preferences.get("auto_backup", True):
                self.setup_auto_backup(
                    preferences.get("backup_interval", 30),
                    preferences.get("backup_retention", 10)
                )
            
            self.translation_manager.log("debug", "log_preferences_applied")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_applying_preferences", error=str(e))
            raise

    def apply_theme(self, theme_name: str):
        """Applicazione tema con pulsanti ottimizzati"""
        try:
            style = ttk.Style()

            if theme_name == "system":
                # Usa il tema di sistema
                import sys
                if sys.platform.startswith("win"):
                    style.theme_use("vista")
                elif sys.platform.startswith("darwin"):
                    style.theme_use("aqua")
                else:
                    style.theme_use("clam")
            else:
                # Applica tema chiaro/scuro con migliori contrasti
                themes = {
                    "light": {
                        "background": "#ffffff",      # Sfondo generale
                        "foreground": "#000000",      # Testo generale
                        "input_bg": "#ffffff",        # Sfondo input
                        "input_fg": "#000000",        # Testo input
                        "button_bg": "#e0e0e0",       # Sfondo pulsante
                        "button_fg": "#000000",       # Testo pulsante
                        "button_hover_bg": "#c8c8c8", # Hover pulsante sfondo
                        "button_hover_fg": "#000000", # Hover pulsante testo
                        "selected": "#0078d7",        # Selezione (es. Treeview)
                        "selected_fg": "#ffffff"      # Testo selezionato
                    },
                    "dark": {
                        "background": "#1e1e1e",      # Sfondo generale
                        "foreground": "#dcdcdc",      # Testo generale
                        "input_bg": "#3c3c3c",        # Sfondo input
                        "input_fg": "#ffffff",        # Testo input
                        "button_bg": "#404040",       # Sfondo pulsante (più scuro)
                        "button_fg": "#ffffff",       # Testo pulsante
                        "button_hover_bg": "#505050", # Hover pulsante sfondo (più chiaro per contrasto)
                        "button_hover_fg": "#ffffff", # Hover pulsante testo
                        "selected": "#0078d7",        # Selezione (es. Treeview)
                        "selected_fg": "#ffffff"      # Testo selezionato
                    }
                }

                theme = themes.get(theme_name, themes["light"])

                # Configurazione di base
                style.configure(".",
                                background=theme["background"],
                                foreground=theme["foreground"])
                style.configure("TLabel",
                                background=theme["background"],
                                foreground=theme["foreground"])
                style.configure("TFrame",
                                background=theme["background"])
                
                # Configura campi di input
                style.configure("TEntry",
                                fieldbackground=theme["input_bg"],
                                foreground=theme["input_fg"])
                
                # Configura pulsanti con hover
                style.configure("TButton",
                    background=theme["button_bg"],
                    foreground=theme["button_fg"])

                # Mappa gli stati del pulsante
                style.map("TButton",
                    background=[
                        ("pressed", theme["button_hover_bg"]),
                        ("active", theme["button_hover_bg"])
                    ],
                    foreground=[
                        ("pressed", theme["button_hover_fg"]),
                        ("active", theme["button_hover_fg"])
                    ])

                # Treeview per tabella
                style.configure("Treeview",
                                background=theme["background"],
                                fieldbackground=theme["background"],
                                foreground=theme["foreground"])
                style.map("Treeview",
                        background=[("selected", theme["selected"])],
                        foreground=[("selected", theme["selected_fg"])])

            # Aggiorna il tema attivo
            self.root.update_idletasks()

        except Exception as e:
            self.translation_manager.log("error", "log_error_applying_theme", error=str(e))
            raise

    def apply_font_size(self, size: int):
        """Applicazione dimensione font"""
        try:
            # Font predefinito
            default_font = ("TkDefaultFont", size)
            
            # Applica a tutti gli stili
            style = ttk.Style()
            style.configure(".", font=default_font)
            style.configure("Treeview", font=default_font)
            style.configure("Treeview.Heading", font=(default_font[0], default_font[1], "bold"))
            
            # Aggiorna font esistenti
            for widget in self.root.winfo_children():
                try:
                    widget.configure(font=default_font)
                except:
                    pass
                    
            self.translation_manager.log(
                "debug",
                "log_font_size_applied",
                size=size
            )
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_applying_font", error=str(e))
            raise

    def setup_auto_backup(self, interval: int, retention: int):
        """Setup backup automatico"""
        try:
            # Crea cartella backup se non esiste
            backup_folder = self.get_preference("backup_folder", "backups")
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
            
            def perform_backup():
                try:
                    # Crea backup
                    self.create_backup()
                    
                    # Mantieni solo gli ultimi N backup
                    self.cleanup_old_backups(retention)
                    
                    # Schedula prossimo backup
                    self.root.after(interval * 60 * 1000, perform_backup)
                    
                except Exception as e:
                    self.translation_manager.log("error", "log_error_auto_backup", error=str(e))
            
            # Avvia primo backup
            self.root.after(interval * 60 * 1000, perform_backup)
            
            self.translation_manager.log(
                "info",
                "log_auto_backup_setup",
                interval=interval,
                retention=retention
            )
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_backup_setup", error=str(e))
            raise

    def create_backup(self):
        """Creazione backup"""
        try:
            # Prepara dati da salvare - salviamo lo stato corrente
            if not (self.prizes or self.participants):  # Skip se non ci sono dati
                return

            backup_data = {
                "current_state": {
                    "prizes": [prize.to_dict() for prize in self.prizes] if self.prizes else [],
                    "participants": [participant.to_dict() for participant in self.participants] if self.participants else []
                }
            }
                
            # Nome file con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = self.get_preference("backup_folder", "backups")
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
                
            filename = os.path.join(backup_folder, f"backup_{timestamp}.json")
            
            # Salva backup
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(backup_data, f, indent=4, ensure_ascii=False)
            
            self.translation_manager.log(
                "info",
                "log_backup_created",
                filename=filename
            )
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_creating_backup", error=str(e))

    def cleanup_old_backups(self, retention: int):
        """Pulizia vecchi backup"""
        try:
            backup_folder = self.get_preference("backup_folder", "backups")
            
            # Lista file di backup ordinati per data
            backup_files = []
            for f in os.listdir(backup_folder):
                if f.startswith("backup_") and f.endswith(".json"):
                    path = os.path.join(backup_folder, f)
                    backup_files.append((path, os.path.getmtime(path)))
                    
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Elimina backup più vecchi
            for path, _ in backup_files[retention:]:
                os.remove(path)
                self.translation_manager.log(
                    "debug",
                    "log_old_backup_removed",
                    file=os.path.basename(path)
                )
                
        except Exception as e:
            self.translation_manager.log("error", "log_error_cleanup_backups", error=str(e))
            raise

    def restore_backup(self):
        """Ripristino da backup"""
        try:
            # Prima verifichiamo se la cartella backup esiste
            backup_folder = self.get_preference("backup_folder", "backups")
            if not os.path.exists(backup_folder):
                self.show_validation_error("no_backups_available")
                return

            # Poi verifichiamo se ci sono file di backup
            backup_files = [
                f for f in os.listdir(backup_folder)
                if f.startswith("backup_") and f.endswith(".json")
            ]
            
            if not backup_files:
                self.show_validation_error("no_backups_available")
                return
                
            # Da qui proseguiamo con la creazione del dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("restore_backup"))
            dialog.geometry("500x600")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            # Lista backup
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill="both", expand=True)
            
            ttk.Label(
                frame,
                text=self.translation_manager.get_text("select_backup")
            ).pack(pady=5)
            
            # Treeview per backup
            backup_tree = ttk.Treeview(
                frame,
                columns=("date", "size", "prizes", "participants"),
                show="headings",
                height=10
            )
            
            # Configura colonne
            backup_tree.column("date", width=150)
            backup_tree.column("size", width=100)
            backup_tree.column("prizes", width=100)
            backup_tree.column("participants", width=100)
            
            backup_tree.heading("date", text=self.translation_manager.get_text("date"))
            backup_tree.heading("size", text=self.translation_manager.get_text("size"))
            backup_tree.heading("prizes", text=self.translation_manager.get_text("prizes"))
            backup_tree.heading("participants", text=self.translation_manager.get_text("participants"))
            
            # Popola lista
            for filename in sorted(backup_files, reverse=True):
                path = os.path.join(backup_folder, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                    current_state = data.get("current_state", {})
                    prizes = current_state.get("prizes", [])
                    participants = current_state.get("participants", [])
                    
                    # Estrai data da nome file
                    date_str = filename[7:-5]  # Rimuove "backup_" e ".json"
                    date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                    
                    size = os.path.getsize(path) / 1024  # KB

                    backup_tree.insert("", "end", values=(
                        date.strftime("%Y-%m-%d %H:%M:%S"),
                        f"{size:.1f} KB",
                        str(len(prizes)),
                        str(len(participants))
                    ))
                except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_reading_backup",
                        filename=filename,
                        error=str(e)
                    )
            
            backup_tree.pack(fill="both", expand=True, pady=10)
            
            def do_restore():
                selection = backup_tree.selection()
                if not selection:
                    self.show_validation_error("no_backup_selected")
                    return
                    
                item = backup_tree.item(selection[0])
                date_str = item["values"][0]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                filename = f"backup_{date.strftime('%Y%m%d_%H%M%S')}.json"
                
                if messagebox.askyesno(
                    self.translation_manager.get_text("confirm"),
                    self.translation_manager.get_text("confirm_restore")
                ):
                    self.perform_restore(os.path.join(backup_folder, filename))
                    dialog.destroy()
            
            # Pulsanti
            button_frame = ttk.Frame(frame)
            button_frame.pack(fill="x", pady=10)
            
            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("restore"),
                command=do_restore
            ).pack(side="left", padx=5)
            
            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            ).pack(side="right", padx=5)
            
            # Preview
            preview_frame = ttk.LabelFrame(
                frame,
                text=self.translation_manager.get_text("preview"),
                padding=10
            )
            preview_frame.pack(fill="x", pady=5)
            
            preview_text = tk.Text(preview_frame, height=5, wrap="word")
            preview_text.pack(fill="x")
            
            def show_preview(event):
                selection = backup_tree.selection()
                if not selection:
                    return
                    
                item = backup_tree.item(selection[0])
                date_str = item["values"][0]
                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                filename = f"backup_{date.strftime('%Y%m%d_%H%M%S')}.json"
                
                try:
                    with open(os.path.join(backup_folder, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    current_state = data.get("current_state", {})
                    prizes = current_state.get("prizes", [])
                    participants = current_state.get("participants", [])
                    
                    preview = (
                        f"{self.translation_manager.get_text('prizes')}: {len(prizes)}\n"
                        f"{self.translation_manager.get_text('participants')}: {len(participants)}\n"
                    )

                    if prizes:
                        # Aggiungi i primi 3 premi come esempio
                        preview += f"\n{self.translation_manager.get_text('prizes')} ({min(3, len(prizes))}):\n"
                        for prize in prizes[:3]:
                            preview += f"- {prize['name']}: {prize['quantity']}\n"

                    if participants:
                        # Aggiungi i primi 3 partecipanti come esempio
                        preview += f"\n{self.translation_manager.get_text('participants')} ({min(3, len(participants))}):\n"
                        for participant in participants[:3]:
                            preview += f"- {participant['name']}: {participant['damage']}\n"

                    preview_text.delete("1.0", tk.END)
                    preview_text.insert("1.0", preview)
                    
                except Exception as e:
                    self.translation_manager.log(
                        "error",
                        "log_error_preview",
                        filename=filename,
                        error=str(e)
                    )

                # Aggiungi qui il binding!
            backup_tree.bind("<<TreeviewSelect>>", show_preview)

        except Exception as e:
            self.translation_manager.log("error", "log_error_restore_dialog", error=str(e))

    def perform_restore(self, backup_file: str):
        """Esecuzione ripristino da backup"""
        try:
            # Leggi backup
            with open(backup_file, "r", encoding='utf-8') as f:
                data = json.load(f)
            
            # Ripristina lo stato corrente
            if "current_state" in data:
                current_state = data["current_state"]
                
                # Ripristina premi
                if "prizes" in current_state:
                    self.prizes = [Prize.from_dict(p) for p in current_state["prizes"]]
                    if self.prizes:
                        self.next_prize_id = max(p.id for p in self.prizes) + 1
                    else:
                        self.next_prize_id = 1
                        
                # Ripristina partecipanti
                if "participants" in current_state:
                    self.participants = [Participant.from_dict(p) for p in current_state["participants"]]
                    if self.participants:
                        self.next_participant_id = max(p.id for p in self.participants) + 1
                    else:
                        self.next_participant_id = 1
            
            # Ripristina impostazioni
            settings = data.get("settings", {})
            if theme := settings.get("theme"):
                self.apply_theme(theme)
                
            # Aggiorna interfaccia
            self.update_tables()
            self.check_save_buttons_state()
            
            self.translation_manager.log(
                "info",
                "log_restore_completed",
                filename=os.path.basename(backup_file)
            )
            self.set_status_message("restore_completed")
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_restore", error=str(e))
            self.show_validation_error("restore_error")

    def show_credits(self):
        """Mostra finestra crediti"""
        try:
            credits_dialog = tk.Toplevel(self.root)
            credits_dialog.title(self.translation_manager.get_text("credits"))
            credits_dialog.geometry("400x350")
            
            self.center_dialog(credits_dialog)
            credits_dialog.transient(self.root)
            credits_dialog.grab_set()
            
            # Frame principale
            content_frame = ttk.Frame(credits_dialog, padding=20)
            content_frame.pack(fill="both", expand=True)
            
            # Developer info
            ttk.Label(
            content_frame, 
            text=self.translation_manager.get_text("developer"),
            font=("Helvetica", 14, "bold")
            ).pack(pady=10)

            # Frame per nome e github
            dev_frame = ttk.Frame(content_frame)
            dev_frame.pack(pady=10)

            ttk.Label(
            dev_frame,
            text="Luke0094",
            font=("Helvetica", 10)
            ).pack(side="left", padx=5)

            ttk.Button(
            dev_frame,
            text="GitHub",
            command=lambda: webbrowser.open("https://github.com/Luke0094")
            ).pack(side="left", padx=5)

            # Separatore
            ttk.Separator(content_frame, orient="horizontal").pack(fill="x", pady=20)

            # Donations
            ttk.Label(
                content_frame,
                text=self.translation_manager.get_text("donations"),
                font=("Helvetica", 12, "bold")
            ).pack(pady=10)
            
            # Wallet frame
            wallet_frame = ttk.Frame(content_frame)
            wallet_frame.pack(pady=10)
            
            # Bitcoin wallet
            btc_frame = ttk.Frame(content_frame)
            btc_frame.pack(pady=5)
            ttk.Label(btc_frame, text="Bitcoin:", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
            btc_entry = ttk.Entry(btc_frame, width=40)
            btc_entry.insert(0, "3G3MDNUh51g6iK7ZRSQPX4EeBXEb3UyAtw")
            btc_entry.configure(state="readonly")
            btc_entry.pack(side="left")
            
            # Litecoin wallet
            ltc_frame = ttk.Frame(content_frame)
            ltc_frame.pack(pady=5)
            ttk.Label(ltc_frame, text="Litecoin:", font=("Helvetica", 10, "bold")).pack(side="left", padx=5)
            ltc_entry = ttk.Entry(ltc_frame, width=40)
            ltc_entry.insert(0, "MEmeHh7A3Cfp9KvcqurviaJXpYL9HXuVJV")
            ltc_entry.configure(state="readonly")
            ltc_entry.pack(side="left")
            
            # Close button
            ttk.Button(
                content_frame,
                text=self.translation_manager.get_text("close"),
                command=credits_dialog.destroy
            ).pack(side="bottom", pady=10)
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_credits", error=str(e))

    def show_settings(self):
        """Mostra finestra impostazioni"""
        try:
            dialog = tk.Toplevel(self.root)
            dialog.title(self.translation_manager.get_text("settings"))
            dialog.geometry("500x400")
            self.center_dialog(dialog)
            dialog.grab_set()
            
            content_frame = ttk.Frame(dialog, padding=20)
            content_frame.pack(fill="both", expand=True)
            
            notebook = ttk.Notebook(content_frame)
            notebook.pack(fill="both", expand=True, padx=5, pady=5)

            # Tab Generale
            general_frame = ttk.Frame(notebook)
            notebook.add(general_frame, text=self.translation_manager.get_text("general"))

            # Import Impostazioni
            import_frame = ttk.LabelFrame(general_frame, text=self.translation_manager.get_text("import_settings"))
            import_frame.pack(fill="x", padx=5, pady=5)
            ttk.Button(
                import_frame,
                text=self.translation_manager.get_text("import_settings_file"),
                command=self.import_settings
            ).pack(fill="x", padx=5, pady=5)

            # Selettore lingua
            lang_frame = ttk.LabelFrame(general_frame, text=self.translation_manager.get_text("default_language"))
            lang_frame.pack(fill="x", padx=5, pady=5)
            lang_var = tk.StringVar(value=self.translation_manager.current_language)
            ttk.Combobox(
                lang_frame,
                textvariable=lang_var,
                values=[f"{self.language_flags[lang]} {lang.upper()}" for lang in self.language_flags.keys()],
                state="readonly"
            ).pack(pady=5)

            # Tab Tema
            theme_frame = ttk.Frame(notebook)
            notebook.add(theme_frame, text=self.translation_manager.get_text("theme"))

            # Selettore tema
            theme_var = tk.StringVar(value=self.get_preference("theme", "system"))
            ttk.Label(theme_frame, text=self.translation_manager.get_text("theme")).pack(pady=5)
            ttk.Combobox(
                theme_frame,
                textvariable=theme_var,
                values=["system", "light", "dark"],
                state="readonly"
            ).pack(pady=5)

            # Font size con preview
            font_frame = ttk.LabelFrame(theme_frame, text=self.translation_manager.get_text("font_size"))
            font_frame.pack(fill="x", padx=5, pady=5)

            preview_label = ttk.Label(font_frame, text="Sample Text")
            preview_label.pack(pady=5)

            font_scale = ttk.Scale(
                font_frame,
                from_=8,
                to=16,
                orient="horizontal"
            )
            font_scale.set(self.get_preference("font_size", 10))
            font_scale.pack(fill="x", padx=5, pady=5)

            current_size_label = ttk.Label(font_frame, text=str(int(font_scale.get())))
            current_size_label.pack(pady=2)

            def update_preview(event):
                size = int(font_scale.get())
                preview_label.configure(font=("TkDefaultFont", size))
                current_size_label.configure(text=str(size))
                
            font_scale.bind("<Motion>", update_preview)

            def reset_font():
                font_scale.set(10)
                update_preview(None)
                
            ttk.Button(
                font_frame,
                text=self.translation_manager.get_text("reset"),
                command=reset_font
            ).pack(pady=5)

            # Tab Backup
            backup_frame = ttk.Frame(notebook)
            notebook.add(backup_frame, text=self.translation_manager.get_text("backup"))

            # Import Backup
            import_backup_frame = ttk.LabelFrame(backup_frame, text=self.translation_manager.get_text("import_backup"))
            import_backup_frame.pack(fill="x", padx=5, pady=5)
            ttk.Button(
                import_backup_frame,
                text=self.translation_manager.get_text("import_backup_file"),
                command=self.restore_backup
            ).pack(fill="x", padx=5, pady=5)

            # Auto backup
            auto_frame = ttk.LabelFrame(backup_frame, text=self.translation_manager.get_text("auto_backup"))
            auto_frame.pack(fill="x", padx=5, pady=5)

            auto_backup = tk.BooleanVar(value=self.get_preference("auto_backup", True))
            
            # Frame per l'intervallo (inizialmente nascosto)
            interval_frame = ttk.Frame(auto_frame)
            
            def toggle_interval_frame(*args):
                if auto_backup.get():
                    interval_frame.pack(fill="x", padx=5)
                else:
                    interval_frame.pack_forget()
            
            ttk.Checkbutton(
                auto_frame,
                text=self.translation_manager.get_text("enable_auto_backup"),
                variable=auto_backup,
                command=toggle_interval_frame
            ).pack(padx=5, pady=5)

            # Intervallo backup
            ttk.Label(interval_frame, text=self.translation_manager.get_text("backup_interval")).pack(side="left")
            interval_var = tk.StringVar(value="3")  # Default a 3 minuti
            ttk.Entry(interval_frame, textvariable=interval_var, width=5).pack(side="left", padx=5)
            ttk.Label(interval_frame, text=self.translation_manager.get_text("minutes")).pack(side="left")

            # Imposta stato iniziale del frame intervallo
            if auto_backup.get():
                interval_frame.pack(fill="x", padx=5)

            # Frame pulsanti principali
            button_frame = ttk.Frame(content_frame)
            button_frame.pack(fill="x", pady=10)

            # Reset preferences button a sinistra
            def reset_all_preferences():
                if messagebox.askyesno(
                    self.translation_manager.get_text("confirm"),
                    self.translation_manager.get_text("confirm_reset_preferences")
                ):
                    if os.path.exists('preferences.json'):
                        os.remove('preferences.json')
                    self._preferences = {}
                    dialog.destroy()
                    messagebox.showinfo(
                        self.translation_manager.get_text("info"),
                        self.translation_manager.get_text("preferences_reset")
                    )
                    # Riapplica le impostazioni di default
                    self.load_preferences()

            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("reset"),
                command=reset_all_preferences
            ).pack(side="left", padx=5)

            def save_settings():
                try:
                    prefs = {}  # Dizionario temporaneo per raccogliere tutte le preferenze

                    # Raccogli tutte le preferenze
                    prefs["theme"] = theme_var.get()
                    prefs["font_size"] = int(font_scale.get())
                    prefs["language"] = lang_var.get().split()[-1].lower()
                    prefs["auto_backup"] = auto_backup.get()
                    prefs["backup_interval"] = int(interval_var.get())

                    # Salva ogni preferenza individualmente
                    for key, value in prefs.items():
                        self.save_preference(key, value)
                    
                    # Applica le modifiche
                    self.apply_theme(prefs["theme"])
                    self.apply_font_size(prefs["font_size"])
                    self.change_language(prefs["language"])
                    
                    # Setup backup se abilitato
                    if prefs["auto_backup"]:
                        self.setup_auto_backup(prefs["backup_interval"], 10)  # 10 è il retention default
                    
                    dialog.destroy()
                    self.translation_manager.log("info", "log_settings_saved")
                    self.set_status_message("preferences_saved")
                except Exception as e:
                    self.translation_manager.log("error", "log_error_saving_settings", error=str(e))
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("save_error")
                    )

            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("save"),
                command=save_settings
            ).pack(side="right", padx=5)

            ttk.Button(
                button_frame,
                text=self.translation_manager.get_text("cancel"),
                command=dialog.destroy
            ).pack(side="right", padx=5)
            
        except Exception as e:
            self.translation_manager.log("error", "log_error_showing_settings", error=str(e))

    def import_settings(self):
        """Importa le impostazioni"""
        try:
            filename = filedialog.askopenfilename(
                title=self.translation_manager.get_text("select_settings_file"),
                filetypes=[("JSON files", "*.json")],
                initialdir=os.getcwd()
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        settings = json.load(f)
                    
                    # Backup impostazioni attuali
                    current_settings = self._preferences.copy() if hasattr(self, '_preferences') else {}
                    
                    try:
                        # Applica le nuove impostazioni
                        self.apply_preferences(settings)
                        self._preferences = settings
                        
                        messagebox.showinfo(
                            self.translation_manager.get_text("info"),
                            self.translation_manager.get_text("settings_imported")
                        )
                        
                    except Exception as e:
                        # Ripristina impostazioni precedenti in caso di errore
                        self._preferences = current_settings
                        self.apply_preferences(current_settings)
                        raise e
                        
                except json.JSONDecodeError:
                    messagebox.showerror(
                        self.translation_manager.get_text("error"),
                        self.translation_manager.get_text("invalid_settings_file")
                    )
                    
        except Exception as e:
            self.translation_manager.log("error", "log_error_importing_settings", error=str(e))
            messagebox.showerror(
                self.translation_manager.get_text("error"),
                self.translation_manager.get_text("settings_import_error")
            )

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Ottiene una preferenza"""
        try:
            if not hasattr(self, '_preferences'):
                self._preferences = {}
                if os.path.exists('preferences.json'):
                    with open('preferences.json', 'r', encoding='utf-8') as f:
                        self._preferences = json.load(f)
            return self._preferences.get(key, default)
        except Exception as e:
            self.translation_manager.log("error", "log_error_getting_preference", error=str(e))
            return default

    def save_preference(self, key: str, value: Any):
        """Salva una preferenza"""
        try:
            if not hasattr(self, '_preferences'):
                self._preferences = {}
            self._preferences[key] = value
            with open('preferences.json', 'w', encoding='utf-8') as f:
                json.dump(self._preferences, f, indent=4)
            self.translation_manager.log("debug", "log_preference_saved", pref_key=key)
        except Exception as e:
            self.translation_manager.log("error", "log_error_saving_preference", error=str(e))
    
    def show_validation_error(self, error_key: str):
        """Mostra un messaggio di errore di validazione"""
        messagebox.showerror(
            self.translation_manager.get_text("error"),
            self.translation_manager.get_text(error_key)
        )

    def set_status_message(self, message_key: str):
        """Mostra un messaggio di stato"""
        messagebox.showinfo(
            self.translation_manager.get_text("info"),
            self.translation_manager.get_text(message_key)
        )


    def run(self):
        """Start the application"""
        # Apply initial translations
        self.update_ui_text()
       
        # Start main loop
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = PrizeDistributionApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")