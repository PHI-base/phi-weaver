# Database Configuration for PHI-Canto MySQL Integration
# Copy this file to config_local.py and customize your settings

# MySQL Database Settings
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # or 'phi_curator' if you created a dedicated user
    'password': '',  # Add your MySQL password here
    'database': 'phi_canto_tracking'
}

# Curator Settings
DEFAULT_CURATOR = 'martin.urban'  # Your name for session logging

# Obsidian Vault Settings
VAULT_ROOT = '/mnt/z/OBS-PHI-Canto'
SESSION_LOGS_DIR = '11-CLAUDE-AI/SESSION-LOGS'
LITERATURE_DIR = '04-Literature'
PROJECTS_DIR = '02-Projects'

# File Path Helpers
def get_session_log_path(filename):
    """Get full path to session log file"""
    return f"{SESSION_LOGS_DIR}/{filename}"

def get_literature_note_path(filename):
    """Get full path to literature note"""
    return f"{LITERATURE_DIR}/{filename}"

def get_project_note_path(project, filename):
    """Get full path to project note"""
    return f"{PROJECTS_DIR}/{project}/{filename}"

# Example usage:
# from config import DB_CONFIG, DEFAULT_CURATOR
# from phi_canto_db import PHICantoDB
#
# db = PHICantoDB(**DB_CONFIG)
# db.connect()
# db.log_session(date.today(), DEFAULT_CURATOR, proteins_curated=2)