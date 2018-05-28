from app import GlobalConfig

class CommonResoures():

    def get_complaince_status(self, blocking_conditions):
        try:
            response = {}
            response['complaince_status'] = "inactive" if any(blocking_conditions[key] for key in blocking_conditions) else "active"
            if response['complaince_status'] == "inactive":
                response['inactivity_reasons'] = [key for key in blocking_conditions if blocking_conditions[key]]
                response['link_to_help'] = GlobalConfig['HelpUrl']
                response['block_date'] = GlobalConfig['BlockDate']
            return response
        except Exception as e:
            print(e)