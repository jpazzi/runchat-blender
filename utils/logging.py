# utils/logging.py

import bpy


def log(message, level='INFO', operator=None):
    """
    Centralized logging function for runchat addon
    
    Args:
        message: The message to log
        level: Log level ('INFO', 'WARNING', 'ERROR')
        operator: Optional operator instance for UI reporting
    """
    # Print to console (always visible)
    print(f"[runchat] {message}")
    
    # Report to UI if operator is available
    if operator and hasattr(operator, 'report'):
        try:
            report_type = {'INFO': 'INFO', 'WARNING': 'WARNING', 'ERROR': 'ERROR'}.get(level, 'INFO')
            operator.report({report_type}, f"runchat: {message}")
        except Exception:
            # Fallback to print if reporting fails
            pass


def log_info(message, operator=None):
    """Log info message"""
    log(message, 'INFO', operator)


def log_warning(message, operator=None):
    """Log warning message"""
    log(message, 'WARNING', operator)


def log_error(message, operator=None):
    """Log error message"""
    log(message, 'ERROR', operator) 