from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec
from app import BaseUrl


class ApiDocs:
    """Class for Flask-Apispec Autodocs"""

    def __init__(self, app, version):
        """Constructor"""
        self.app = app
        self.title = 'Device Verification Subsystem'
        self.version = version
        self.plugins = [MarshmallowPlugin()]
        self.swagger_json_url = '/apidocs-json/'
        self.swagger_url = BaseUrl+'/apidocs/'

    def init_doc(self):
        """Config and init auto-docs for api version"""
        self.app.config.update({
            'APISPEC_SPEC': APISpec(
                title=self.title,
                version=self.version,
                info={'description': self.spec_description()},
                plugins=self.plugins,
            ),
            'APISPEC_SWAGGER_URL': self.swagger_json_url,
            'APISPEC_SWAGGER_UI_URL': self.swagger_url,
        })

        return FlaskApiSpec(self.app)

    def spec_description(self):
        """Generate text for api docs description"""
        description = 'The document lists the APIs exposed by device verification subsystem. '
        return description
