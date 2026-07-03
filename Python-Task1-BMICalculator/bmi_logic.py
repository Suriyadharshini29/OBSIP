def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI = weight (kg) / height (m)^2"""
    return round(weight / (height ** 2), 2)


def classify_bmi(bmi: float) -> tuple[str, str]:
    """
    Returns (category, hex_color) based on BMI value.
    Color scheme: blue=underweight, green=normal, orange=overweight, red=obese
    """
    if bmi < 18.5:
        return "Underweight", "#3498DB"
    elif bmi < 25:
        return "Normal", "#27AE60"
    elif bmi < 30:
        return "Overweight", "#E67E22"
    else:
        return "Obese", "#E74C3C"


def validate_inputs(weight_str: str, height_str: str) -> tuple[float, float]:
    """
    Validate and parse weight/height strings.
    Returns (weight, height) floats or raises ValueError with a descriptive message.
    """
    try:
        weight = float(weight_str)
    except ValueError:
        raise ValueError("Weight must be a numeric value (e.g. 70.5).")

    try:
        height = float(height_str)
    except ValueError:
        raise ValueError("Height must be a numeric value (e.g. 1.75).")

    if weight <= 0:
        raise ValueError("Weight must be a positive number.")
    if height <= 0:
        raise ValueError("Height must be a positive number.")
    if weight > 500:
        raise ValueError("Weight seems unrealistic. Please enter a value under 500 kg.")
    if height > 3.0 or height < 0.5:
        raise ValueError("Height must be between 0.5 m and 3.0 m.")

    return weight, height
