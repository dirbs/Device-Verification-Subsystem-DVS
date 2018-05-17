from app import config

link_to_help = config.get("Development", "link_to_help")
block_date = config.get("Development", "block_date")

class CommonResoures():

    def get_complaince_status(self, blocking_conditions):
        try:
            response = {}
            response['complaince_status'] = "inactive" if any(blocking_conditions[key]==True for key in blocking_conditions) else "active"
            if response['complaince_status'] == "inactive":
                response['inactivity_reasons'] = [key for key in blocking_conditions if blocking_conditions[key]]
                response['link_to_help'] = link_to_help
                response['block_date'] = block_date
            return response
        except Exception as e:
            print(e)