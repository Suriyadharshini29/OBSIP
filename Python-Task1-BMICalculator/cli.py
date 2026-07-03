"""Beginner-tier command-line BMI calculator (standalone, no DB)."""
from bmi_logic import calculate_bmi, classify_bmi, validate_inputs


def get_input(prompt: str) -> str:
    return input(prompt).strip()


def main():
    print("\n===== BMI Calculator =====\n")

    while True:
        weight_str = get_input("Enter your weight in kg: ")
        height_str = get_input("Enter your height in metres (e.g. 1.75): ")

        try:
            weight, height = validate_inputs(weight_str, height_str)
            break
        except ValueError as e:
            print(f"\n⚠  {e}  Try again.\n")

    bmi = calculate_bmi(weight, height)
    category, _ = classify_bmi(bmi)

    print(f"\n  BMI      : {bmi:.2f}")
    print(f"  Category : {category}")

    tips = {
        "Underweight": "Consider consulting a nutritionist for a healthy weight-gain plan.",
        "Normal":      "Great work — keep up your healthy lifestyle!",
        "Overweight":  "Regular exercise and a balanced diet can help.",
        "Obese":       "Please consider speaking with a healthcare professional.",
    }
    print(f"  Tip      : {tips[category]}\n")


if __name__ == "__main__":
    main()
