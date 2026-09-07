import csv
from collections import defaultdict
from data.generator import apply_noise, generate_experiment
from main import main
import copy

from run_experiment import run_experiment


TIMES = 1

NOISE_CONFIGS = [
    (0, 2),
    (0, 4),
    (0, 6),
    (0, 8),
    (0, 10),
    (2, 2),
    (2, 4),
    (2, 6),
    (2, 8),
    (2, 10),
    (4, 2),
    (4, 4),
    (4, 6),
    (4, 8),
    (4, 10),
    (6, 2),
    (6, 4),
    (6, 6),
    (6, 8),
    (6, 10),
    (8, 2),
    (8, 4),
    (8, 6),
    (8, 8),
    (8, 10),
    (10, 2),
    (10, 4),
    (10, 6),
    (10, 8),
    (10, 10)
]

SOLUTIONS = [1, 2, 3, 4]


def generate_comparison_table():

    timestamp = generate_experiment(
        num_scenarios=30,
        num_users=500,
    )

    distribution_filename = (
        f"data/dados/cases_distribution_{timestamp}.csv"
    )

    combined_filename = (
        f"data/dados/dados_completo_{timestamp}.csv"
    )

    with open(
        distribution_filename,
        "w",
        newline=""
    ) as distribution_file, \
         open(
             combined_filename,
             "w",
             newline=""
         ) as combined_file:

        distribution_writer = csv.writer(
            distribution_file,
            delimiter=";"
        )

        combined_writer = csv.writer(
            combined_file,
            delimiter=";"
        )

        distribution_writer.writerow([
            "Mean",
            "Stddev",
            "Solution",
            "Case",
            "Samples",
            "Percentage"
        ])

        combined_writer.writerow([
            "Mean",
            "Stddev",
            "Solution",
            "Case",
            "Average Error",
            "Samples"
        ])

        for mean, stddev in NOISE_CONFIGS:

            filename = (
                f"data/dados/"
                f"dados_{timestamp}_{mean}_{stddev}.txt"
            )

            print(f"\n{'=' * 70}")
            print(f"MEAN = {mean} | STDDEV = {stddev}")
            print(f"{'=' * 70}")

            with open(
                filename,
                "w",
                newline=""
            ) as results_file:

                writer = csv.writer(
                    results_file,
                    delimiter=";"
                )

                writer.writerow([
                    "Solution",
                    "Case",
                    "Average Error",
                    "Samples"
                ])

                all_solution_errors = {
                    solution: defaultdict(list)
                    for solution in SOLUTIONS
                }

                for scenario, base_stations, users in run_experiment(timestamp):

                    print(
                        f"\nScenario {scenario} "
                        f"| mean={mean}, stddev={stddev}"
                    )

                    users_with_noise = apply_noise(
                        copy.deepcopy(users),
                        mean,
                        stddev,
                        TIMES,
                        fixed_value=False,
                        same_for_all_bs=False
                    )

                    for solution in SOLUTIONS:

                        print(
                            f"    Testing solution={solution}"
                        )

                        solution_users = copy.deepcopy(
                            users_with_noise
                        )

                        case_errors = main(
                            base_stations,
                            solution_users,
                            mean,
                            stddev,
                            TIMES,
                            solution,
                            timestamp
                        )

                        for case, errors in case_errors.items():

                            all_solution_errors[
                                solution
                            ][case].extend(errors)

                for solution in SOLUTIONS:

                    print(
                        f"\n{'-' * 60}"
                    )

                    print(
                        f"RESULTADOS DA SOLUÇÃO {solution}"
                    )

                    print(
                        f"{'-' * 60}"
                    )

                    solution_results = (
                        all_solution_errors[solution]
                    )

                    total_samples = sum(
                        len(errors)
                        for errors
                        in solution_results.values()
                    )

                    print(
                        f"Total samples: {total_samples}"
                    )

                    for case in sorted(
                        solution_results.keys(),
                        key=int
                    ):

                        errors = solution_results[case]

                        if not errors:
                            continue

                        samples = len(errors)

                        avg_error = (
                            sum(errors) / samples
                        )

                        writer.writerow([
                            solution,
                            case,
                            round(avg_error, 2),
                            samples
                        ])

                        combined_writer.writerow([
                            mean,
                            stddev,
                            solution,
                            case,
                            round(avg_error, 2),
                            samples
                        ])

                        percentage = (
                            samples / total_samples * 100
                            if total_samples > 0
                            else 0
                        )

                        distribution_writer.writerow([
                            mean,
                            stddev,
                            solution,
                            case,
                            samples,
                            round(percentage, 2)
                        ])

                        print(
                            f"Case {case}: "
                            f"samples={samples}, "
                            f"avg_error={avg_error:.2f}"
                        )


if __name__ == "__main__":
    generate_comparison_table()