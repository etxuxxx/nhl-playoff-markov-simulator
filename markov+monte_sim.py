import pandas as pd
import math
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

filepath = r'C:\Users\etxux\Downloads\teams.csv'
df = pd.read_csv(filepath)

# Ratings for each team calculated

playoff_teams = [
    "BUF",  # Buffalo Sabres
    "TBL",  # Tampa Bay Lightning
    "MTL",  # Montreal Canadiens
    "CAR",  # Carolina Hurricanes
    "PIT",  # Pittsburgh Penguins
    "PHI",  # Philadelphia Flyers
    "BOS",  # Boston Bruins
    "OTT",  # Ottawa Senators
    "COL",  # Colorado Avalanche
    "DAL",  # Dallas Stars
    "MIN",  # Minnesota Wild
    "VGK",  # Vegas Golden Knights
    "EDM",  # Edmonton Oilers
    "ANA",  # Anaheim Ducks
    "UTA",  # Utah Mammoth
    "LAK"   # Los Angeles Kings
]


playoff_df = df[df['team'].isin(playoff_teams)]


playoff_df1 = playoff_df[[
    "team",
    "situation",
    "xGoalsPercentage",
    "xGoalsFor",
    "xGoalsAgainst",
    "highDangerxGoalsFor",
    "highDangerxGoalsAgainst",
    "goalsFor",
    "goalsAgainst",
    "corsiPercentage"
]]


fiveonfive = playoff_df1[playoff_df1['situation'] == '5on5']
powerplay = playoff_df1[playoff_df1['situation'] == '5on4']
penaltykill = playoff_df1[playoff_df1['situation'] == '4on5']
all_sit = playoff_df1[playoff_df1['situation'] == 'all']

fiveonfive_stats = fiveonfive[["team",
    "xGoalsPercentage",
    "xGoalsFor",
    "xGoalsAgainst",
    "highDangerxGoalsFor",
    "highDangerxGoalsAgainst",
    "corsiPercentage"]].copy()

powerplay_stat = powerplay[[
    'team',
    'xGoalsFor'
]].copy()

penalty_stat = penaltykill[[
    "team",
    "xGoalsAgainst"
]].copy()

all_sit_stats = all_sit[[
    "team",
    "goalsFor",
    "goalsAgainst"
]].copy()

playoff_df2 = fiveonfive_stats.merge(powerplay_stat, on = 'team').merge(penalty_stat, on = 'team').merge(all_sit_stats, on = 'team')

playoff_df2['allgoals diff'] = playoff_df2['goalsFor'] - playoff_df2['goalsAgainst']

list_of_columns = playoff_df2.columns.tolist()
list_of_columns.remove('team')
playoff_df2 = playoff_df2.reset_index(drop=True)

for i in list_of_columns:
    playoff_df2[f'{i} mean'] = playoff_df2[i].mean()
    playoff_df2[f'{i} std'] = playoff_df2[i].std()
    playoff_df2[f'{i} total'] = 0.0
    for index in range(len(playoff_teams)):
        mean = playoff_df2.loc[index, f'{i} mean'] 
        std = playoff_df2.loc[index, f'{i} std'] 
        value = playoff_df2.loc[index, i] 
        playoff_df2.loc[index, f'{i} total'] = (value - mean)/(std)

# list_of_columns = playoff_df2.columns.tolist()
# print(list_of_columns)

bad_stats = [
    'xGoalsAgainst_x total',
    'highDangerxGoalsAgainst total',
    'xGoalsAgainst_y total',
    'goalsAgainst total'
]

for i in bad_stats:
    playoff_df2[i] = -1*playoff_df2[i]

playoff_df2['rating'] = 0.0

for i in range(len(playoff_df2)):
    goalp_total = playoff_df2.loc[i, 'xGoalsPercentage total']

    goalfor_total = playoff_df2.loc[i, 'xGoalsFor_x total']
    goalagainst_total = playoff_df2.loc[i, 'xGoalsAgainst_x total']

    highdangerfor_total = playoff_df2.loc[i, 'highDangerxGoalsFor total']
    highdangeragainst_total = playoff_df2.loc[i, 'highDangerxGoalsAgainst total']

    ppgoalsfor_total = playoff_df2.loc[i, 'xGoalsFor_y total']
    pkgoalsagainst_total = playoff_df2.loc[i, 'xGoalsAgainst_y total']

    allgoaldiff_total = playoff_df2.loc[i, 'allgoals diff total']

    corsi_total = playoff_df2.loc[i, 'corsiPercentage total']

    playoff_df2.loc[i, 'rating'] = (
        0.30 * goalp_total
        + 0.12 * goalfor_total
        + 0.12 * goalagainst_total
        + 0.10 * highdangerfor_total
        + 0.10 * highdangeragainst_total
        + 0.08 * ppgoalsfor_total
        + 0.08 * pkgoalsagainst_total
        + 0.06 * allgoaldiff_total
        + 0.04 * corsi_total
    )

list_of_teams = [i for i in playoff_df2['team']]
team_rating = [i for i in playoff_df2['rating']]

rating_final = pd.DataFrame({
    "team": list_of_teams,
    "team_rating": team_rating
})

rating_final = rating_final.sort_values("team_rating", ascending=False).reset_index(drop=True)
print(rating_final)

# Playoff logistic equation

def rating_percentage(team_1_rating, team_2_rating):
    t = team_1_rating - team_2_rating
    k = 0.50
    win_percentage = 1 / (1+math.exp(-k * t))
    return win_percentage

team_rating_dct = rating_final.set_index('team')['team_rating'].to_dict()
# print(rating_percentage(team_rating_dct['CAR'], team_rating_dct['VGK']))




# Markov chain playoff bracket

round1 = [
    ["BUF", "BOS"],
    ["TBL", "MTL"],
    ["CAR", "OTT"],
    ["PIT", "PHI"],
    ["COL", "LAK"],
    ["DAL", "MIN"],
    ["VGK", "UTA"],
    ["EDM", "ANA"]
]

states = [
    (0, 0),

    (1, 0), (0, 1),

    (2, 0), (1, 1), (0, 2),

    (3, 0), (2, 1), (1, 2), (0, 3),

    (4, 0), (3, 1), (2, 2), (1, 3), (0, 4),

    (4, 1), (3, 2), (2, 3), (1, 4),

    (4, 2), (3, 3), (2, 4),

    (4, 3), (3, 4)
]

def matrix_power(matrix, power):
  if power == 0:
    return np.identity(len(matrix))
  elif power == 1:
    return matrix
  else:
    return np.dot(matrix, matrix_power(matrix, power-1))
  
# Game by Game Monte Carlo
winners_round_1 = []

def build_chain(matchup):
    state_index = {}
    team_a = matchup[0]
    team_b = matchup[1]
    p = rating_percentage(team_rating_dct[team_a], team_rating_dct[team_b])
    q = 1 - p

    for i in range(len(states)):
        state_index[states[i]] = i

    n = len(states)
    trans_matrix = np.zeros((n, n))

    for state in states:
        team_1_win, team_2_win = state
        row = state_index[state]

        if team_1_win == 4 or team_2_win == 4:
            trans_matrix[row][row] = 1
        else:
            next_state_1 = (team_1_win + 1, team_2_win)
            next_state_2 = (team_1_win, team_2_win + 1)

            new_col1 = state_index[next_state_1]
            new_col2 = state_index[next_state_2]

            trans_matrix[row][new_col1] = p
            trans_matrix[row][new_col2] = q



    return state_index, trans_matrix

def simulate_series_markov(matchup, state_index, trans_matrix):
    team_a_name = matchup[0]
    team_b_name = matchup [1]
    n = len(states)
    current_state = np.zeros(n)
    current_state[state_index[(0, 0)]] = 1
    final_state = np.dot(current_state, matrix_power(trans_matrix, 7))
    chosen_index = np.random.choice(range(len(states)), p=final_state)
    team_1, team_2 = states[chosen_index]
    if team_1 == 4:
        winner = team_a_name
    elif team_2 == 4:
        winner = team_b_name
    return winner

def simulate_series_monte(matchup, state_index, trans_matrix):
    team_a_name = matchup[0]
    team_b_name = matchup [1]
    team_a = 0
    team_b = 0
    current_state = (team_a, team_b)
    while current_state[0]<4 and current_state[1]<4:
        row = state_index[current_state]
        next_state = np.random.choice(range(len(states)), p = trans_matrix[row])
        current_state = states[next_state]

    if current_state[0]==4:
        winner = team_a_name
    else:
        winner = team_b_name
    return winner

def winner_append(winner_round, matchup, function):
    state_index, trans_matrix = build_chain(matchup)
    winner_round.append(function(matchup, state_index, trans_matrix))


def simulate_bracket(rounds, function):
    count = len(rounds)
    rounds = round1.copy()
    while count >1:
        next_round = []
        for i in rounds:
            winner_append(next_round, i, function)
        rounds.clear()
        for q in range(0, len(next_round), 2):
            rounds.append([next_round[q], next_round[q+1]])
        count = len(rounds)
    final_winner= []
    if count<=1:
        winner_append(final_winner, rounds[0], function)

    return final_winner[0]


df = pd.DataFrame({'Teams':playoff_teams})
def simulations(num_sims, function, df, name):
    champions = []
    while len(champions)<num_sims:
        champions.append(simulate_bracket(round1, function))
    champions_total = Counter(champions)
    wins_df = pd.DataFrame(champions_total.items(), columns = ['Teams', f'Wins {name}'])
    final_df = df.merge(wins_df, on="Teams", how="left")
    final_df[f"Wins {name}"] = final_df[f"Wins {name}"].fillna(0).astype(int)
    final_df[f'Win Percentage {name}'] = round(final_df[f'Wins {name}'] / num_sims * 100, 2)
    final_df = final_df.sort_values(f'Wins {name}', ascending = False).reset_index(drop = True)
    return final_df


        
# Monte Carlo Simulation
num_sims = 1000
monte = simulations(num_sims, simulate_series_monte, df, 'Monte Carlo')
print(monte)

#Markov Simulation
markov = simulations(num_sims, simulate_series_markov, df, 'Markov Chain')
print(markov)

both = monte.merge(markov, on = 'Teams')
print(both)


                     


# Bar plots of Stanley Cup
both.to_csv(r"C:\Users\etxux\Downloads\final_percentages1.csv", index=False)
plot_df = both.drop(columns=['Wins Monte Carlo', 'Wins Markov Chain'])
sns.set_theme(style="whitegrid")

plot_df = plot_df.melt(
    id_vars = 'Teams',
    value_vars = ['Win Percentage Monte Carlo', 'Win Percentage Markov Chain'],
    var_name='Simulation Type',
    value_name='Win Percentage'
)

plt.figure(figsize=(12, 8))

g = sns.barplot(
    data=plot_df,
    x="Win Percentage",
    y="Teams",
    hue="Simulation Type",
)
plt.title(f"Stanley Cup Odds Through {num_sims} Simulations")
plt.xlabel("Championship Probability (%)")
plt.ylabel("Team")

plt.tight_layout()

plt.savefig(r"C:\Users\etxux\Downloads\stanley_cup_odds1.png", bbox_inches="tight")

plt.show()



