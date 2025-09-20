# utils/config.py
import yaml
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Config:
    _config_loaded = False
    _config_data = {}

    def __init__(self):
        if not Config._config_loaded:
            config_path = None
            current_dir = os.getcwd() # Start from the current working directory

            # Look for config.yaml in current or parent directories
            for i in range(5): # Check up to 5 levels up
                potential_path = os.path.join(current_dir, 'config.yaml')
                if os.path.exists(potential_path):
                    config_path = potential_path
                    break
                current_dir = os.path.dirname(current_dir) # Move up one directory
                if current_dir == os.path.dirname(current_dir): # Reached root
                    break

            if not config_path:
                logging.error("config.yaml not found in current or parent directories.")
                Config._config_data = {} # Ensure it's empty if not found
            else:
                try:
                    with open(config_path, 'r', encoding='utf-8') as file:
                        Config._config_data = yaml.safe_load(file)
                    Config._config_loaded = True
                    logging.info(f"Configuration loaded successfully from: {config_path}")
                except yaml.YAMLError as e:
                    logging.error(f"Error parsing config.yaml: {e}")
                    Config._config_data = {}
                except FileNotFoundError:
                    logging.error(f"config.yaml not found at expected path: {config_path}")
                    Config._config_data = {}
                except Exception as e:
                    logging.error(f"An unexpected error occurred while loading config: {e}")
                    Config._config_data = {}

    @classmethod
    def get_disease_tags(cls):
        """
        Returns the 'DISEASE_TAGS' dictionary from the configuration.
        Returns an empty dictionary if 'DISEASE_TAGS' is not found or if config failed to load.
        """
        # This method is designed to be called on the class itself (Config.get_disease_tags())
        # and should return the dictionary directly.
        return cls._config_data.get('DISEASE_TAGS', {})

    @classmethod
    def get_recipe_db(cls):
        """
        Returns the 'RECIPE_DB' list from the configuration.
        Returns an empty list if 'RECIPE_DB' is not found or if config failed to load.
        """
        return cls._config_data.get('RECIPE_DB', [])

# Instantiate Config on import to load the data immediately when the module is imported.
# This ensures the configuration is available when other modules use the Config class.
Config()