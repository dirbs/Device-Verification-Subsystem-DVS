###################################################
#                                                 #
# Copyright (c) 2018 Qualcomm Technologies, Inc.  #
#                                                 #
# All rights reserved.                            #
#                                                 #
###################################################

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
