from app import GlobalConfig
from ..assets.error_handling import *


class CommonResoures():

    def get_complaince_status(self, blocking_conditions, seen_with):
        try:
            response = dict()
            response['complaince_status'] = "Non compliant" if any(blocking_conditions[key] for key in blocking_conditions) else "Compliant (Active)" if seen_with else "Compliant (Inactive)"
            if response['complaince_status'] == "Non compliant":
                response['inactivity_reasons'] = [key for key in blocking_conditions if blocking_conditions[key]]
                response['link_to_help'] = GlobalConfig['HelpUrl']
                response['block_date'] = GlobalConfig['BlockDate']
            return response
        except Exception as e:
            app.logger.info("Error occurred while evaluating compliance status.")
            app.logger.exception(e)
            return internal_error()
