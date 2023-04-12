import logging

def setup_logger():
    logger = logging.getLogger(__name__) 
    logger.setLevel(logging.INFO)

    # Create a formatter for log messages
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 

    # Create a stream handler for displaying log messages in the console
    console_handler = logging.StreamHandler() 
    console_handler.setFormatter(formatter)

    # Create a file handler for saving log messages to a file
    file_handler = logging.FileHandler('jira_app.log') 
    file_handler.setLevel(logging.INFO) 
    file_handler.setFormatter(formatter) 

    # Add both handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger 
