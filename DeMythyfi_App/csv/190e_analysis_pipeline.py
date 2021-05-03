#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


def get_metrics(name, topic_influence, k1=20, k2=0.72):
    print(f"Metrics and Figures for {name}")
    preds = analysts[analysts['Name']==name].drop('Name', axis=1)
    results = {}
    
    ### METRICS
    # experience
    earliest, latest = preds['Date'].min(), preds['Date'].max()
    analyst_exp = (latest-earliest).days + preds.shape[0]

    npreds_total = analysts[(analysts['Date'] >= earliest) & (analysts['Date']<= latest)].shape[0]
    cumulative_exp = (analysts['Date'].max() - analysts['Date'].min()).days + 1.5*npreds_total
    
    results['experience'] = analyst_exp/cumulative_exp * 5
    
    # accuracy weighted by topic influence
    unique_topics = preds['Topic'].unique()
    weighted_accs = dict.fromkeys(unique_topics)
    overall_acc = 0
    for topic in unique_topics:
        t_inf = topic_influence[topic]
        
        # weighted accuracy based on topic influence
        topic_preds = preds[preds['Topic']==topic]
        x = topic_preds[['1mo', '6mo', '12mo']].to_numpy().flatten().astype(float)
        x = x[~np.isnan(x)]
        factor = topic_preds.shape[0] * t_inf
        w_acc = sum(x)/len(x) * factor
        weighted_accs[topic] = w_acc
        overall_acc += w_acc
        
    results['accuracy'] = overall_acc/len(unique_topics)
    
    # confidence rating
    results['confidence'] = (k2*results['experience'] + (1-k2)*results['accuracy']) * k1
    
    for metric in results.keys():
        print(f'\t {metric} : {results[metric]}')
    
    # FIGURES
    
    # topic dist
    group = preds[['Topic', 'Prediction']].groupby(by=['Topic']).count()
    counts = np.array(group['Prediction'])
    xs = np.array(group.index)
    topic_dist_fig = plt.bar(xs, counts/sum(counts))
    plt.xlabel('Topic')
    plt.ylabel('Proportion')
    plt.title('Distribution of predictions per topic')
    plt.show()
    plt.clf()
    
    # topic influence dist
    xs = [t for t in unique_topics]
    ys = [topic_influence[t] for t in unique_topics]
    plt.bar(xs, ys)
    plt.xlabel('Topic')
    plt.ylabel('Influence level')
    plt.title('Topic influence')
    plt.show()
    plt.clf()
    
    # experience over time
    curr, start = dt.datetime.now(), analysts['Date'].min()
    days_diff = (curr - start).days
    timerange = np.array([start + dt.timedelta(days=i) for i in range(days_diff)])
    cumsum_time = preds[['Prediction']].groupby(pd.cut(preds['Date'], bins=timerange)).count()
    ys = np.cumsum(cumsum_time['Prediction'])
    start_str, end_str = start.strftime("%Y-%m-%d"), ys.index[-1].left.strftime("%Y-%m-%d")
    xs = pd.date_range(start_str, end_str).tolist()
    plt.plot(xs,np.array(ys))
    plt.title('Prediction count over time')
    plt.xlabel('time')
    plt.xticks(rotation=-45)
    plt.ylabel('count')
    plt.show()
    plt.clf();
    
    return results


if __name__ == "__main__":

    # read and process data set
    analysts = pd.read_csv('./analysts_dataset.csv', parse_dates=['Date'],)
    analysts.rename({'Analyst Name':'Name'}, axis=1, inplace=True)
    dropcols = ['Prediction Source', 'Result Source']
    analysts = analysts.drop(dropcols, axis=1)

    # generate a topic influence dictionary
    topic_influence = dict.fromkeys(analysts['Topic'].unique())

    for topic in analysts['Topic'].unique():
        count = len(analysts[analysts['Topic']==topic]['Name'].unique())
        topic_influence[topic] = 1/count # inversely related to num unique analysts predicting on that topic

    # get metrics for each unique analyst
    unique_ana = np.unique(analysts['Name'])
    ana_metrics = dict.fromkeys(unique_ana)

    for ana in unique_ana:
        ana_metrics = get_metrics(ana, topic_influence)


    

