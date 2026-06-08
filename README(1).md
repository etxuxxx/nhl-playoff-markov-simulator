# NHL Playoff Markov Chain Simulator

This project predicts Stanley Cup championship odds using NHL team statistics, a custom team rating system, Markov chains, Monte Carlo simulation, and data visualization.

The model builds a rating for each playoff team from MoneyPuck-style hockey statistics, converts rating differences into single-game win probabilities, models each best-of-seven series with Markov chain states, and simulates the full playoff bracket many times.

## Project Overview

The goal of this project is to estimate each playoff team's chance of winning the Stanley Cup.

This project combines:

- Hockey analytics
- Data cleaning with pandas
- Z-score standardization
- Logistic win probability modeling
- Best-of-seven Markov chain modeling
- Monte Carlo bracket simulation
- Seaborn visualization

Each playoff team receives a rating based on several team-level statistics. These ratings are then used to estimate game win probabilities. The project then uses those probabilities to simulate playoff series and the full Stanley Cup bracket.

## Data and Features

The model uses team statistics from different game situations:

- 5-on-5 play
- Power play
- Penalty kill
- All situations

The rating system includes the following features:

- 5-on-5 expected goals percentage
- 5-on-5 expected goals for
- 5-on-5 expected goals against
- 5-on-5 high-danger expected goals for
- 5-on-5 high-danger expected goals against
- 5-on-4 power-play expected goals for
- 4-on-5 penalty-kill expected goals against
- Goal differential
- Corsi percentage

Each statistic is standardized using a z-score:

```text
z = (value - mean) / standard deviation
```

This allows different types of hockey statistics to be compared on the same scale.

Defensive statistics, such as expected goals against, are multiplied by `-1` so that better defensive performance increases a team's rating.

## Team Rating System

Each team receives a rating based on a weighted sum of standardized statistics:

```text
Team Rating =
0.30 * 5v5 xGoalsPercentage
+ 0.12 * 5v5 xGoalsFor
+ 0.12 * 5v5 xGoalsAgainst defense
+ 0.10 * 5v5 highDangerxGoalsFor
+ 0.10 * 5v5 highDangerxGoalsAgainst defense
+ 0.08 * power-play xGoalsFor
+ 0.08 * penalty-kill xGoalsAgainst defense
+ 0.06 * goal differential
+ 0.04 * corsiPercentage
```

The weights are manually chosen based on hockey reasoning.

5-on-5 expected goals percentage receives the highest weight because most hockey is played at even strength, and expected goals measure shot quality better than raw goal totals.

## Logistic Win Probability

For each matchup, the model compares the two team ratings:

```text
rating_difference = Team A rating - Team B rating
```

Then it uses a logistic function to convert the rating difference into a single-game win probability:

```text
P(Team A wins) = 1 / (1 + e^(-k * rating_difference))
```

This project uses:

```text
k = 0.50
```

The `k` value controls how strongly the model trusts the rating difference.

A lower `k` keeps the model more uncertain, which makes sense for hockey because individual games are noisy and can be affected by goaltending, puck luck, special teams, and low-scoring variance.

## Markov Chain Series Model

Each best-of-seven playoff series is modeled as a Markov chain.

Each state represents the current series score:

```text
(0, 0), (1, 0), (0, 1), (2, 0), ..., (4, 3), (3, 4)
```

For example:

```text
(2, 1)
```

means Team A has 2 wins and Team B has 1 win.

From each non-final state, there are two possible transitions:

```text
Team A wins next game -> (team_a_wins + 1, team_b_wins)
Team B wins next game -> (team_a_wins, team_b_wins + 1)
```

Once either team reaches 4 wins, the series reaches an absorbing state.

Example absorbing states:

```text
(4, 0), (4, 1), (4, 2), (4, 3)
(0, 4), (1, 4), (2, 4), (3, 4)
```

The transition matrix stores the probability of moving from one series score to the next.

For example, from state `(2, 1)`:

```text
P((2, 1) -> (3, 1)) = Team A single-game win probability
P((2, 1) -> (2, 2)) = Team B single-game win probability
```

The model then uses matrix powers to calculate the probability distribution of final series outcomes after up to seven games:

```python
final_state = current_state @ matrix_power(trans_matrix, 7)
```

This `final_state` vector contains the probabilities of ending in each possible final series state.

## Monte Carlo Bracket Simulation

The full playoff bracket is simulated many times.

For each simulation:

1. Simulate every first-round matchup.
2. Advance the winners.
3. Pair the winners into the next round.
4. Continue until one champion remains.
5. Record the Stanley Cup winner.

After many simulations, the project counts how many times each team wins the Stanley Cup and converts those counts into championship probabilities.

Example:

```text
Championship Probability = Team Cup Wins / Number of Simulations
```

## Markov Chain vs Monte Carlo

This project includes both Markov chain modeling and Monte Carlo simulation.

The Markov chain is used to represent each best-of-seven series as a set of possible series-score states and transition probabilities.

The Monte Carlo simulation is used to repeatedly simulate the entire playoff bracket and estimate championship odds.

In other words:

```text
Markov chain = models an individual playoff series
Monte Carlo = repeats the full playoff bracket many times
```

This makes the project a combination of Markov chain probability modeling and Monte Carlo simulation.

## Visualization

The project uses seaborn to create a horizontal bar chart comparing championship probabilities.

The final graph shows each team's simulated Stanley Cup odds and compares results from the Monte Carlo and Markov chain methods.

Output file:

```text
stanley_cup_odds1.png
```

## Files

```text
markov_playoff_simulator.py     Main Python simulation script
teams.csv                       Team statistics dataset
final_percentages1.csv          Output file with championship odds
stanley_cup_odds1.png           Output bar chart
README.md                       Project explanation
```

## How to Run

Clone the repository and make sure `teams.csv` is in the same folder as the Python file.

Install the required libraries:

```bash
pip install pandas numpy matplotlib seaborn
```

Run the simulator:

```bash
python markov_playoff_simulator.py
```

The program will generate:

```text
final_percentages1.csv
stanley_cup_odds1.png
```

## Example Output

The CSV output contains each playoff team, the number of simulated Stanley Cup wins, and the championship probability from each simulation method.

Example format:

```text
Teams,Wins Monte Carlo,Win Percentage Monte Carlo,Wins Markov Chain,Win Percentage Markov Chain
COL,184,18.4,179,17.9
EDM,132,13.2,136,13.6
VGK,101,10.1,107,10.7
```

Because the project uses random simulation, results may change slightly each time the program is run.

## Current Limitations

This model is a simplified hockey prediction system. Important limitations include:

- Team rating weights are manually chosen instead of learned from historical data.
- The model assumes each team has the same single-game win probability throughout a series.
- The model does not currently include home-ice advantage.
- The model does not account for injuries, goalie changes, trades, rest days, or matchup-specific strategy.
- The playoff bracket is manually entered.
- Monte Carlo results vary slightly each time the program runs.
- The Markov chain currently models series score states, not changing team strength over time.

## Future Improvements

Possible future improvements include:

- Use the `final_state` vector directly to calculate exact series win probabilities.
- Build a fully deterministic Markov chain bracket model.
- Add home-ice advantage.
- Add goalie statistics.
- Include injury or roster adjustments.
- Use historical NHL data to learn rating weights with logistic regression.
- Make the bracket simulator scalable for 32-team, 64-team, or custom brackets.
- Refactor the bracket simulation using a divide-and-conquer structure.
- Reduce global variables by passing more variables into functions.
- Use more pandas vectorized operations for cleaner and faster data transformations.
- Add confidence intervals for championship probabilities.
- Build an interactive dashboard with Streamlit.

## Technologies Used

- Python
- pandas
- NumPy
- matplotlib
- seaborn
- Markov chains
- Monte Carlo simulation
- Hockey analytics

## What I Learned

Through this project, I learned how to:

- Clean and organize sports data with pandas.
- Standardize statistics using z-scores.
- Build a custom team rating model.
- Convert rating differences into win probabilities with a logistic function.
- Represent a best-of-seven playoff series as a Markov chain.
- Use a transition matrix to model changes between series states.
- Use matrix powers to calculate final state probabilities.
- Simulate a full playoff bracket many times using Monte Carlo methods.
- Compare simulation outputs using pandas and seaborn.

## Acknowledgements

Thank you to Kevin Yan for providing helpful feedback on the project, especially around improving the Markov chain implementation, making the code more scalable, reducing global variables, and using pandas more effectively.

## Summary

This project uses hockey statistics, probability, Markov chains, and Monte Carlo simulation to estimate Stanley Cup championship odds.

It started as a basic playoff simulator and developed into a larger sports analytics project involving data processing, rating systems, probability modeling, bracket simulation, and visualization.
