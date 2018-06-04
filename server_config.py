class BaseConfig(object):  # base config class for server
    """Base configuration class"""
    SECRET_KEY = 'SecretKey'
    DEBUG = True
    TESTING = False


class ProductionConfig(BaseConfig):
    """Production Specific Configurations"""
    DEBUG = False
    SECRET_KEY = 'ProductionSecretKey'


class StagingConfig(BaseConfig):
    """Staging Specific Configuration"""
    DEBUG = True


class DevelopmentConfig(BaseConfig):
    """Development Specific Configurations"""
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'DevSecretKey'
    ALLOWED_EXT = ['tsv']
    UPLOAD_FOLDER = 'api/v1/assets'
    BASE_URL = '/api/v1'
    HOST = '127.0.0.1'
    PORT = 5000
    DIRBSCORE = 'http://dirbs.pta.gov.pk'


class GlobalConfig(BaseConfig):
    """Global Configurations"""
    MIN_IMEI_LENGTH = 14
    MAX_IMEI_LENGTH = 16
    MIN_IMEI_RANGE = "000000"
    MAX_IMEI_RANGE = "100"
    HELP_URL = "not confirmed"
    BLOCK_DATE = "to be decided"
    MIN_FILE_CONTENT = 1
    MAX_FILE_CONTENT = 1000000


