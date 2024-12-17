import logging
import logging.config
import yaml


def setup_logging(default_path='logging.yml', log_level=logging.INFO):
    """Setup logging configuration."""
    with open(default_path, 'r') as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)


def get_logger(name):
    return logging.getLogger(name)


setup_logging()
