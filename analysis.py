from main import main
import pandas as pd
from itertools import product

mean_list = [mean for mean in range(0, 1)]
std_list = [std for std in range(1, 7)]
noise_times_list = [noise_times for noise_times in range(5, 6)]

resultados = []

if __name__ == "__main__":
    for mean, std, noise_times in product(mean_list, std_list, noise_times_list):
        
        main(mean, std, noise_times)
        
        df = pd.read_csv("data/trilateration_results_table.csv", delimiter=";", encoding='utf-8-sig')
        media = df['Erro (metros)'].mean()
        
        resultados.append({
            'mean': mean,
            'std': std,
            'noise_times': noise_times,
            'media_erro (metros)': media
        })

    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv("data/error_analysis.csv", index=False, sep=';')
