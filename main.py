from bs4 import BeautifulSoup
import requests
import streamlit as st
import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt


def get_table(league="premierleague"):
    try:

        url = f"https://www.theguardian.com/football/{league}/table"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        teams = [team.text.replace('\n', '').strip(
        ) for team in soup.find_all('a', class_="team-name__long")]

        # with open("teams.html", "w", encoding='utf-8') as file:
        #     file.write(str(teams))
        return soup, teams
    except ValueError:
        return "No Info"


def calculate_possibilities(soup, team_a, team_b):
    team_a_stats = team_b_stats = []
    for row in soup.find_all('tr', class_=""):
        # if row.find('a', class_="team-name__long").text in [team_a, team_b]:
        try:
            team = str(
                row.find('a', class_="team-name__long").text).replace('\n', '').strip()

            if team == team_a:
                # team-result--drew / team-result--won / team-result--lost

                # last_5_games = temp_stats[10].find_all(
                #     'span', class_="team-result")
                temp_stats = row.find_all('td')
                for s in temp_stats[2:10]:
                    team_a_stats.append(int(s.text))

            elif team == team_b:
                temp_stats = row.find_all('td')
                for s in temp_stats[2:10]:
                    team_b_stats.append(int(s.text))

            else:
                continue

        except AttributeError:
            continue
    # GP, W, D, L, F, A, GD, Pts

    results, max, HG, AG, max2, HG2, AG2, max3, HG3, AG3, both_team_to_score, team_a_goal_probability, team_b_goal_probability = calculation_team_stregnth(
        team_a_stats[0], team_a_stats[4], team_a_stats[5], team_b_stats[0], team_b_stats[4], team_b_stats[5])
    return results, max, HG, AG, max2, HG2, AG2, max3, HG3, AG3, both_team_to_score, team_a_goal_probability, team_b_goal_probability


def result_percentage_and_prediction(team_a_goal_probability, team_b_goal_probability):
    team_a_win = 0
    draw = 0
    team_b_win = 0
    both_team_to_score = 0
    results = []

    all_results = []
    team_a_list = []
    team_b_list = []
    for i in range(1, len(team_a_goal_probability)):
        for j in range(1, len(team_b_goal_probability)):
            temp = (team_a_goal_probability[i] *
                    team_b_goal_probability[j]) * 100
            both_team_to_score += temp
    for i in range(len(team_a_goal_probability)):
        for j in range(len(team_b_goal_probability)):
            result = (
                team_a_goal_probability[i] * team_b_goal_probability[j]) * 100
            all_results.append(result)
            team_a_list.append(i)
            team_b_list.append(j)
            if i > j:
                temp = (
                    team_a_goal_probability[i] * team_b_goal_probability[j]) * 100
                team_a_win += temp
            if i == j:
                temp = (
                    team_a_goal_probability[i] * team_b_goal_probability[j]) * 100
                draw += temp
            if i < j:
                temp = (
                    team_a_goal_probability[i] * team_b_goal_probability[j]) * 100
                team_b_win += temp
    mapped = zip(all_results, team_a_list, team_b_list)
    mapped = set(mapped)
    maximum_probaility_and_goals1 = max(mapped)
    mapped.remove(maximum_probaility_and_goals1)
    maximum_probaility_and_goals2 = max(mapped)
    mapped.remove(maximum_probaility_and_goals2)
    maximum_probaility_and_goals3 = max(mapped)
    mapped.remove(maximum_probaility_and_goals3)
    max_prob1 = maximum_probaility_and_goals1[0]
    HG = maximum_probaility_and_goals1[1]
    AG = maximum_probaility_and_goals1[2]
    max_prob2 = maximum_probaility_and_goals2[0]
    HG2 = maximum_probaility_and_goals2[1]
    AG2 = maximum_probaility_and_goals2[2]
    max_prob3 = maximum_probaility_and_goals3[0]
    HG3 = maximum_probaility_and_goals3[1]
    AG3 = maximum_probaility_and_goals3[2]

    results.append(team_a_win)
    results.append(draw)
    results.append(team_b_win)
    max_prob1 = round(max_prob1, 2)
    max_prob2 = round(max_prob2, 2)
    max_prob3 = round(max_prob3, 2)
    both_team_to_score = round(both_team_to_score, 2)
    return results, max_prob1, HG, AG, max_prob2, HG2, AG2, max_prob3, HG3, AG3, both_team_to_score


def calculation_team_stregnth(HGP, HGF, HGA, AGP, AGF, AGA):
    # HGP : Host Games Played
    # HGF : Host Goals For
    # HGA : Host Goals Against

    # AGP : Away Games Played
    # AGF : Away Goals For
    # AGA : Away Goals Against

    # HGR =  Host Team Goal Rate
    # AGR =  Away Team Goal Rate
    # HCR =  Host Team Goal Conceded Rate
    # ACR =  Away Team Goal Conceded Rate
    HGR = HGA / HGP
    AGR = AGA / AGP
    HCR = HGF / HGP
    ACR = AGF / AGP

    # HEG (Host Expected Goals : multiplication between team_a Team Attack Strength and Away Team Defance Strength
    HEG = HGR * ACR
    # AEG (Away Expected Goals : multiplication between Away Team Attack Strength and Host Team Defance Strength
    AEG = AGR * HCR
    i = np.arange(0, 6)
    team_a_goal_probability = poisson.pmf(i, HEG)
    team_b_goal_probability = poisson.pmf(i, AEG)

    results, max, HG, AG, max2, HG2, AG2, max3, HG3, AG3, both_team_to_score = result_percentage_and_prediction(
        team_a_goal_probability, team_b_goal_probability)

    return results, max, HG, AG, max2, HG2, AG2, max3, HG3, AG3, both_team_to_score, team_a_goal_probability, team_b_goal_probability


option = st.selectbox(
    'Choose the league?',
    ('Premier League', 'Bundes Liga', 'La Liga', 'Serie A', 'Ligue 1'))

league_dict = {'Premier League': "premierleague",
               "Bundes Liga": 'bundesligafootball', 'La Liga': 'laligafootball', "Serie A": 'serieafootball', 'Ligue 1': 'ligue1football'}

soup, teams = get_table(league_dict[option])


c2, c3 = st.columns([0.5, 0.5])


with c2:
    team_a = st.selectbox("Team A: ", (teams))
with c3:
    team_b = st.selectbox("Team B: ", (teams))

if st.button('Calculate'):
    try:
        results, max, HG, AG, max2, HG2, AG2, max3, HG3, AG3, both_team_to_score, team_a_goal_probability, team_b_goal_probability = calculate_possibilities(
            soup, team_a, team_b)
        barFig, ax = plt.subplots(1, 2)
        i = np.arange(0, 6)
        ax[0].bar(i,  team_b_goal_probability)
        ax[0].set(title=team_a, xlabel="Goals", ylabel="Probability")
        ax[1].bar(i, team_a_goal_probability, color="Green")
        ax[1].set(title=team_b, xlabel="Goals", ylabel="Probability")
        barFig.subplots_adjust(left=0.125, right=0.9, bottom=0.1,
                               top=0.9, wspace=0.5, hspace=0.5)

        # Pie Chart
        labels = [team_b + " Win", "Draw", team_a + " Win"]
        pieFig = plt.figure()
        plt.pie(results, labels=labels, autopct='%1.1f%%')
        st.markdown(f"""<p>{team_a} {AG} - {HG} {team_b} Possibility: {max}% </p>
                        <p>{team_a} {AG2} - {HG2} {team_b} Possibility: {max2}%</p>
                        <p>{team_a} {AG3} - {HG3} {team_b} Possibility: {max3}%</p>
                        """, unsafe_allow_html=True)
        st.pyplot(barFig)
        st.pyplot(pieFig)
    except IndexError:
        st.markdown(
            "Sth wrong with the data fetching please try to wait some seconds after changing teams or league")
