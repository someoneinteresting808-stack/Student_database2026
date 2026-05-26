def calculate_percentage(scores):
    if not scores:
        return 0.0
    total = sum(float(s) for s in scores)
    count = len(scores)
    return (total / (count * 100.0)) * 100.0

def map_gpa(percentage):
    if percentage >= 90.0:
        return 4.00
    elif percentage >= 80.0:
        return 3.00
    elif percentage >= 70.0:
        return 2.00
    elif percentage >= 60.0:
        return 1.00
    else:
        return 0.00
