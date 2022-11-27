def interactive_confirm(s):
    answer = ""
    while answer not in ["y", "n"]:
        answer = input(s).lower()
    return answer == "y"


def strict_confirm(_):
    return False


def relaxed_confirm(_):
    return True


confirm = interactive_confirm
