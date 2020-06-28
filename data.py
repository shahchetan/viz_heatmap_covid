import requests, json, pandas as pd
from collections import defaultdict
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

statewise_uri = "https://api.covid19india.org/v3/timeseries.json"


def getTimeSeriesDataStateWise():
    req = requests.get(statewise_uri, verify=False)
    return req.json()


def createTableFromJson(jsondata):
    # col = ['date', 'state','delta_confirmed', 'delta_recovered', 'delta_tested',
    #        'total_confirmed', 'total_deceased', 'total_recovered', 'total_tested']

    d = defaultdict(list)

    for state, data in jsondata.items():
        for date, v in data.items():
            d['state'].append(state)
            d['date'].append(date)
            delta = v.get('delta', {})
            d['delta_confirmed'].append(delta.get('confirmed', 0))
            d['delta_deceased'].append(delta.get('deceased', 0))
            d['delta_recovered'].append(delta.get('recovered', 0))
            d['delta_tested'].append(delta.get('tested', 0))
            total = v.get('total', {})
            d['total_confirmed'].append(total.get('confirmed', 0))
            d['total_deceased'].append(total.get('deceased', 0))
            d['total_recovered'].append(total.get('recovered', 0))
            d['total_tested'].append(total.get('tested', 0))

    df = pd.DataFrame.from_dict(d)

    mask_curr_date = (df['date'] > '2020-06-26') & (df['state'] != 'TT')
    new_df = df.loc[mask_curr_date].sort_values(by=['total_confirmed'], ascending=False)
    top_states = []
    for state in new_df[['state']].head(5).values.tolist():
        top_states.append(state[0])
    print(top_states)

    basic_mask = (df['date'] > '2020-04-15') & (df['state'] != 'TT') & (df['state'] != 'UN')
    top_states_mask, remaining_states_mask = False, basic_mask
    for state in top_states:
        top_states_mask = top_states_mask | (df['state'] == state)
        remaining_states_mask = remaining_states_mask & (df['state'] != state)

    top_states_mask = basic_mask & top_states_mask

    # mask = (df['date'] > '2020-04-15') & (df['state'] != 'TT') & (df['state'] != 'MH') &
    # (df['state'] != 'DL') & (df['state'] != 'TN')
    # mask = mask & (df['state'] != 'UN')

    df['delta_confirmed_sma'] = df.iloc[:, 2].rolling(window=3).mean()

    # print(df.loc[remaining_states_mask].head())
    # print(df.loc[top_states_mask].head())
    for mask in [top_states_mask, remaining_states_mask]:
        heatmap_table = pd.pivot_table(df.loc[mask], values='delta_confirmed_sma', index=['state'], columns='date')
        ax = sns.heatmap(heatmap_table, xticklabels=True, yticklabels=True, linewidths=.2, cmap='YlGn')
        plt.yticks(fontsize=6)
        plt.xticks(fontsize=6, rotation=45)
        plt.show(ax)


def main():
    # sj = getTimeSeriesDataStateWise()
    with open('raw_data/timeseries.json') as file:
        sj = json.load(file)

    createTableFromJson(sj)


main()
