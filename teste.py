#import random
#import statistics

#from data.generator import noise

#noise_list = []
#for _ in range(1000000):
#    x = noise(2, 2, 1)
##    if x < 0:
#        noise_list.append(x)

#print(noise_list)
#print("Mean:", sum(noise_list)/len(noise_list))

#print("Median:", statistics.mean(noise_list))
#print("Standard Deviation:", statistics.stdev(noise_list))

import pandas as pd

def generate_case_summary(results_path):
    df = pd.read_csv(results_path)

    summary = (
        df.groupby("case", as_index=False)
          .agg(
              average_error=("error", "mean"),
              samples=("error", "count")
          )
          .sort_values("case")
    )

    overall_average = (
        (summary["average_error"] * summary["samples"]).sum()
        / summary["samples"].sum()
    )

    summary.loc[len(summary)] = {
        "case": "Overall",
        "average_error": overall_average,
        "samples": summary["samples"].sum()
    }

    output_path = results_path.replace("results_", "summary_")
    summary.to_csv(output_path, index=False)

    print(summary)
    print(f"\nMédia ponderada: {overall_average:.4f}")

    return summary
def calculate_solution_average(file_path, solution):
    df = pd.read_csv(file_path, sep=";")

    solution_data = df[df["Solution"] == solution]

    if solution_data.empty:
        raise ValueError(f"Solution {solution} not found.")

    weighted_sum = (
        solution_data["Average Error"] * solution_data["Samples"]
    ).sum()

    total_samples = solution_data["Samples"].sum()

    return weighted_sum / total_samples

#means = []

#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_0_2.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_2_2.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_4_4.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_6_6.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_8_8.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_10_10.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_12_12.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_14_14.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_16_16.txt", 9))
#means.append(calculate_solution_average("data/dados/dados_20260731_23_29_20_260474_18_18.txt", 9))


#print("mean 0, std -2:", means[0])
#print("mean 0, std -4:", means[1])
#print("mean 0, std -6:", means[2])
#print("mean 0, std -8:", means[3])
#print("mean 0, std -10:", means[4])
#print("mean 0, std 2:", means[5])
#print("mean 0, std 4:", means[6])
#print("mean 0, std 6:", means[7])
#print("mean 0, std 8:", means[8])
#print("mean 0, std 10:", means[9])

generate_case_summary("data/ga/results_20260801_00_08_35_998282_0_2_1_100_mut0_5.csv")
generate_case_summary("data/ga/results_20260801_00_08_35_998282_0_4_1_100_mut0_5.csv")
generate_case_summary("data/ga/results_20260801_00_08_35_998282_0_6_1_100_mut0_5.csv")
generate_case_summary("data/ga/results_20260801_00_08_35_998282_0_8_1_100_mut0_5.csv")
generate_case_summary("data/ga/results_20260801_00_08_35_998282_0_10_1_100_mut0_5.csv")