SILENT_LOG = False

def log(string):
    if not SILENT_LOG:
        print("[LOG] -- " + string)

def log_warn(string):
    print("[WARNING] -- " + string)

def log_error(string):
    print("[ERROR] -- " + string)
