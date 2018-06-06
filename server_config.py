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
    Global = dict(
    MinImeiLength = 14,
    MaxImeiLength = 16,
    MinImeiRange = "000000",
    MaxImeiRange = "100",
    HelpUrl = "not confirmed",
    BlocDate = "to be decided",
    MinFileContent = 1,
    MaxFileContent = 1000000
    )


