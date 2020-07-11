import os


class Config:
    APP_NAME ="sarjom"
    SECRET_KEY = "SuperWieRdTOpSecRETKeY"  # This needs to be changed to a proper secret key


class DevConfig(Config):
    DEBUG = True
    DB_URI = "mongodb://localhost:27017/test"  # This is the local test database
    DB_NAME = "greendubs"
    GOOGLEMAPS_KEY = os.environ.get('GOOGLEMAPS_KEY')


class ProdConfig(Config):
    DEBUG = False


config = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig
}