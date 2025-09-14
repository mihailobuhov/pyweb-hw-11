import configparser


class Config:
    config = configparser.ConfigParser()
    config.read('config.ini')
    DB_URL = config['database']['DB_URL']


config = Config()