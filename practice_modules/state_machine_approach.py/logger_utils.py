import datetime
import os

# You can change the path to a specific log directory if needed
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "state_machine_logs.txt")

def log_state_transition(state_machine_name, from_node, to_node, details=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_node_name(node):
        if node is None:
            return "None"
        if hasattr(node, "pretty_print"):
            return node.pretty_print()
        # Fallback to class name
        return node.__class__.__name__

    from_name = get_node_name(from_node)
    to_name = get_node_name(to_node)
    
    log_entry = f"[{timestamp}] {state_machine_name}: {from_name} -> {to_name}"
    if details:
        log_entry += f" | {details}"
    log_entry += "\n"
    
    # Ensure the log file is in the workspace root or a consistent location
    # For now, just use the current directory or a relative path
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def log_action(class_name, action_desc):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] ACTION - {class_name}: {action_desc}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
