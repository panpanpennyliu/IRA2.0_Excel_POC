from utils.logger_setup_data_extraction import logger

class ContextManager:

    def __init__(self):
        self.context = []

    def get_context(self):
        return self.context

    def add_context(self, value):
        self.context.append(value)
        print(f"Add '{value}' into the context.")

    def remove_context(self, value):
        if value in self.context:
            self.context.remove(value)
            print(f"Remove '{value}' from the context.")
        else:
            print(f"Value '{value}' not found in context.")

    def context_to_str(self):
        contextStr = "<context>\n"
        for value in self.context:
            contextStr += f"\n{value}\n"
        contextStr += "</context>"
        return contextStr

    def print_context(self):
        logger.info(f"Here is the context:")
        logger.info(self.context_to_str())