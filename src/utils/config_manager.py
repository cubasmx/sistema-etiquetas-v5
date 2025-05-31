import os
import json
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / '.odoo_bom_exporter'
        self.config_file = self.config_dir / 'config.json'
        self.ensure_config_dir()
        
    def ensure_config_dir(self):
        """Asegura que el directorio de configuración existe"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def get_config(self):
        """Obtiene la configuración actual"""
        if not self.config_file.exists():
            return {
                'url': '',
                'db': '',
                'username': '',
                'password': '',
                'port': ''
            }
            
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'url': '',
                'db': '',
                'username': '',
                'password': '',
                'port': ''
            }
            
    def save_config(self, config):
        """Guarda la configuración"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4) 