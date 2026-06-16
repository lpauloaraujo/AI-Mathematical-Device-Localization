import csv
from main import main

def generate_comparison_table():

    trilateration_methods = [0, 1]

    choice_methods = [
        0,
        1,
        2,
        3,
        4
    ]

    with open(
        "data/method_comparison.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.writer(
            file,
            delimiter=";"
        )

        writer.writerow([
            "Trilateration",
            "Choice",
            "Case",
            "Average Error",
            "Samples"
        ])

        for tril_method in trilateration_methods:

            for choice_method in choice_methods:

                print(
                    f"Testing T={tril_method}, "
                    f"C={choice_method}"
                )

                case_errors = main(
                    0,
                    6,
                    5,
                    tril_method,
                    choice_method
                )

                for case in sorted(
                    case_errors.keys(),
                    key=int
                ):

                    errors = case_errors[case]

                    avg_error = (
                        sum(errors) /
                        len(errors)
                    )

                    writer.writerow([
                        tril_method,
                        choice_method,
                        case,
                        round(avg_error, 2),
                        len(errors)
                    ])

if __name__ == "__main__":
    generate_comparison_table()