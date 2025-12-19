import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 1. Récupération des données historiques
# On prend un laps de temps intéressant, par exemple les 3 dernières années
start_date = "2021-01-01"
end_date = "2024-01-01"

print("--- Pairs Trading Analysis ---")
t1 = input("Enter first ticker (e.g. KO): ").upper()
t2 = input("Enter second ticker (e.g. PEP): ").upper()
tickers = [t1, t2]

print(f"Downloading data for {t1} and {t2}...")
data_full = yf.download(tickers, start=start_date, end=end_date)

# Gestion des colonnes selon la version de yfinance
if 'Adj Close' in data_full.columns:
    data = data_full['Adj Close'].copy()
else:
    data = data_full['Close'].copy()

# Vérification que les données sont bien là
if data.empty:
    print("Aucune donnée récupérée. Vérifiez votre connexion internet.")
else:
    # 2. Calcul du Beta (Hedge Ratio) dynamique
    # On cherche la relation : T2 = Beta * T1 + Alpha
    slope, intercept = np.polyfit(data[t1], data[t2], 1)
    Beta = slope
    print(f"Beta calculé sur la période : {Beta:.4f}")

    # 3. Calcul du Spread
    # Spread = Prix_T2 - (Beta * Prix_T1)
    data['Spread'] = data[t2] - (Beta * data[t1])

    # 4. Calcul du Z-Score (Indicateur normalisé)
    # Z-Score = (Spread - Moyenne) / Ecart-Type
    spread_mean = data['Spread'].mean()
    spread_std = data['Spread'].std()
    data['Z-Score'] = (data['Spread'] - spread_mean) / spread_std

    # 5. Génération des Signaux (Stratégie avec retour à la moyenne)
    entry_threshold = 2.0
    exit_threshold = 0.0
    
    positions = []
    current_position = 0 # 0: Neutre, 1: Long Spread, -1: Short Spread
    
    for z in data['Z-Score']:
        if z > entry_threshold:
            current_position = -1 # Vente du spread (Trop cher)
        elif z < -entry_threshold:
            current_position = 1 # Achat du spread (Pas cher)
        elif current_position == -1 and z < exit_threshold:
            current_position = 0 # Retour à la normale -> On sort
        elif current_position == 1 and z > exit_threshold:
            current_position = 0 # Retour à la normale -> On sort
        
        positions.append(current_position)
        
    data['Position'] = positions

    # 6. Backtest du Portefeuille
    initial_capital = 10000
    cash = initial_capital
    shares_t1 = 0 # Nombre d'actions Ticker 1
    shares_t2 = 0 # Nombre d'actions Ticker 2
    portfolio_values = []
    
    print(f"\n--- Démarrage du Backtest avec {initial_capital}$ ---")
    
    for i in range(len(data)):
        price1 = data[t1].iloc[i]
        price2 = data[t2].iloc[i]
        pos = data['Position'].iloc[i]
        
        # Valeur actuelle du portefeuille (Cash + Actions)
        current_val = cash + (shares_t1 * price1) + (shares_t2 * price2)
        portfolio_values.append(current_val)
        
        # Vérification si on doit changer de position
        # On simplifie : si la position cible est différente de la position actuelle (déduite des actions)
        # On ferme tout et on réouvre
        
        current_holding_type = 0
        if shares_t2 > 0: current_holding_type = 1
        elif shares_t2 < 0: current_holding_type = -1
        
        if pos != current_holding_type:
            # 1. On ferme la position existante (si y'en a une)
            cash += (shares_t1 * price1) + (shares_t2 * price2)
            shares_t1 = 0
            shares_t2 = 0
            
            # 2. On ouvre la nouvelle position
            if pos != 0:
                # On calcule combien on peut acheter
                # Spread = 1*T2 - Beta*T1
                # On veut investir le capital équitablement ou maximiser l'exposition ?
                # Approche simple : On utilise tout le cash pour acheter des "unités" de spread
                # Coût d'une unité (en valeur absolue) = Prix_T2 + (Beta * Prix_T1)
                unit_cost = price2 + (Beta * price1)
                
                if unit_cost > 0:
                    # Nombre d'unités qu'on peut "payer"
                    num_units = cash // unit_cost
                    
                    if pos == 1: # Long Spread (Achat T2, Vente T1)
                        shares_t2 = num_units
                        shares_t1 = -num_units * Beta
                        # On paie T2, on reçoit cash de T1
                        cash -= (shares_t2 * price2) + (shares_t1 * price1)
                        
                    elif pos == -1: # Short Spread (Vente T2, Achat T1)
                        shares_t2 = -num_units
                        shares_t1 = num_units * Beta
                        # On reçoit cash de T2, on paie T1
                        cash -= (shares_t2 * price2) + (shares_t1 * price1)

    data['Portfolio Value'] = portfolio_values
    
    final_value = portfolio_values[-1]
    perf = ((final_value - initial_capital) / initial_capital) * 100
    
    print(f"Capital Initial : {initial_capital}$")
    print(f"Capital Final   : {final_value:.2f}$")
    print(f"Performance     : {perf:.2f}%")

    # 7. Visualisation
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Graphique 1 : Z-Score
        data['Z-Score'].plot(ax=ax1, label='Z-Score')
        ax1.axhline(entry_threshold, color='red', linestyle='--', label='Seuil Vente')
        ax1.axhline(-entry_threshold, color='green', linestyle='--', label='Seuil Achat')
        ax1.axhline(0, color='black', linewidth=1)
        ax1.set_title(f"Z-Score du Spread ({t2} vs {Beta:.2f}*{t1})")
        ax1.legend()
        
        # Graphique 2 : Portefeuille
        data['Portfolio Value'].plot(ax=ax2, color='purple', label='Valeur Portefeuille')
        ax2.set_title("Evolution du Portefeuille ($)")
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Erreur graphique : {e}")

