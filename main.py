import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Récupération des données historiques
# On prend un laps de temps intéressant, par exemple les 3 dernières années
start_date = "2021-01-01"
end_date = "2024-01-01"

tickers = ["KO", "PEP"]
data_full = yf.download(tickers, start=start_date, end=end_date)

# Gestion des colonnes 
if 'Adj Close' in data_full.columns:
    data = data_full['Adj Close'].copy()
else:
    data = data_full['Close'].copy()

# Vérification que les données sont bien là
if data.empty:
    print("Aucune donnée récupérée. Vérifiez votre connexion internet.")
else:
    # 2. Calcul du Beta (Hedge Ratio) dynamique

    slope, intercept = np.polyfit(data['KO'], data['PEP'], 1)
    Beta = slope
    print(f"Beta calculé sur la période : {Beta:.4f}")

    # 3. Calcul du Spread
    # Spread = Prix_PEP - (Beta * Prix_KO)
    data['Spread'] = data['PEP'] - (Beta * data['KO'])

    # 4. Calcul du Z-Score (Indicateur normalisé)
    # Z-Score = (Spread - Moyenne) / Ecart-Type
    spread_mean = data['Spread'].mean()
    spread_std = data['Spread'].std()
    data['Z-Score'] = (data['Spread'] - spread_mean) / spread_std

    # 5. Génération des Signaux
    entry_threshold = 2.0
    
    data['Signal'] = 0
    # Si Z-Score > 2, le spread est "cher" -> On VEND le spread (Short PEP, Long KO)
    data.loc[data['Z-Score'] > entry_threshold, 'Signal'] = -1 
    # Si Z-Score < -2, le spread est "pas cher" -> On ACHETE le spread (Long PEP, Short KO)
    data.loc[data['Z-Score'] < -entry_threshold, 'Signal'] = 1

    # Affichage d'un aperçu
    print("\nAperçu des données avec Z-Score et Signaux :")
    print(data[['KO', 'PEP', 'Spread', 'Z-Score', 'Signal']].tail(10))

    # 6. Visualisation (
    try:
        plt.figure(figsize=(12, 6))
        data['Z-Score'].plot(label='Z-Score')
        plt.axhline(entry_threshold, color='red', linestyle='--', label='Seuil Vente')
        plt.axhline(-entry_threshold, color='green', linestyle='--', label='Seuil Achat')
        plt.axhline(0, color='black', linewidth=1)
        plt.title(f"Pairs Trading: Z-Score du Spread (PEP vs {Beta:.2f}*KO)")
        plt.legend()
        plt.show()
    except Exception as e:
        print("Impossible d'afficher le graphique (matplotlib peut manquer).")
