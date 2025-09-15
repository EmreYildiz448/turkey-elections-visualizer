#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.config import color_map

def fix_labels_based_on_touch(mylabels, separation_factor=0.01, max_iters=20):
    """Fix label positions by moving them apart based on where their bounding boxes touch."""
    
    def are_overlapping(bbox1, bbox2):
        """Check if two bounding boxes overlap."""
        return not (bbox1.x1 < bbox2.x0 or bbox1.x0 > bbox2.x1 or
                    bbox1.y1 < bbox2.y0 or bbox1.y0 > bbox2.y1)
    
    def move_apart(label_a, label_b, separation_factor):
        """Move labels apart in the direction where they overlap."""
        pos_a = label_a.get_position()
        pos_b = label_b.get_position()
        bbox_a = label_a.get_window_extent()
        bbox_b = label_b.get_window_extent()
        if abs(bbox_a.x0 - bbox_b.x1) < abs(bbox_a.y0 - bbox_b.y1):
            if pos_a[0] > pos_b[0]:
                label_a.set_position((pos_a[0] + separation_factor, pos_a[1]))
                label_b.set_position((pos_b[0] - separation_factor, pos_b[1]))
            else:
                label_a.set_position((pos_a[0] - separation_factor, pos_a[1]))
                label_b.set_position((pos_b[0] + separation_factor, pos_b[1]))
        else:
            if pos_a[1] > pos_b[1]:
                label_a.set_position((pos_a[0], pos_a[1] + separation_factor))
                label_b.set_position((pos_b[0], pos_b[1] - separation_factor))
            else:
                label_a.set_position((pos_a[0], pos_a[1] - separation_factor))
                label_b.set_position((pos_b[0], pos_b[1] + separation_factor))
    iterations = 0
    while iterations < max_iters:
        changed = False
        for i in range(len(mylabels)):
            bbox_i = mylabels[i].get_window_extent()
            for j in range(i + 1, len(mylabels)):
                bbox_j = mylabels[j].get_window_extent()
                if are_overlapping(bbox_i, bbox_j):
                    move_apart(mylabels[i], mylabels[j], separation_factor)
                    changed = True
        if not changed:
            break
        iterations += 1
    return mylabels

def rename_columns(df):
    df.rename(index={'bagimsiz toplam oy': 'bagimsiz'}, inplace=True)
    df.rename(index={'gelecek partisi': 'gelecek'}, inplace=True)

def filter_and_group_diger(df, threshold):
    total = df.sum()
    diger = 0
    dropper_list = []
    for index in df.index:
        if df[index] / total * 100 <= threshold:
            diger += df[index]
            dropper_list.append(index)
    df.drop(dropper_list, inplace=True)
    if diger > 0:
        df['diger'] = diger
    return df, total

def create_labels(df, total, include_count=False):
    if include_count:
        labels = [f'{label}\n{value / total * 100:.1f}%, ({int(value)})' for label, value in zip(df.index, df.values)]
    else:
        labels = [f'{label}\n{value / total * 100:.1f}%' for label, value in zip(df.index, df.values)]
    return labels

def annotate_pie_chart(axes, wedges, labels, colors):
    annotated_texts = []
    for j, wedge in enumerate(wedges):
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = np.cos(np.radians(angle)) * 1
        y = np.sin(np.radians(angle)) * 1.1
        annotation = axes.annotate(
            labels[j],
            xy=(x, y),
            xytext=(x * 1.1, y * 1),
            bbox=dict(facecolor=colors[j], alpha=0.4, edgecolor='black', boxstyle='round,pad=0.2'),
            fontweight = 'bold',
            ha='center', va='center')
        annotated_texts.append(annotation)
    return annotated_texts

def get_colors(df):
    return [color_map.get(col, 'grey') for col in df.index]
    
def create_pie_chart(df, ax, colors):
    wedges, texts = ax.pie(df.values, labels=None, colors=colors,
                           wedgeprops=dict(linewidth=0.2, edgecolor='black'), startangle=45)
    return wedges, texts
    
def df_row_selector(df, threshold, fig_name, footnote):
    labels_for_legend = set()
    rename_columns(df)
    df = df[df != 0]
    df, total = filter_and_group_diger(df, threshold)
    labels_for_legend.update(df.index)
    colors = get_colors(df)
    labels = create_labels(df, total)
    fig, ax = plt.subplots()
    wedges, _ = create_pie_chart(df, ax, colors)
    annotated_texts = annotate_pie_chart(ax, wedges, labels, colors)
    handles = [plt.Line2D([0], [0], color=color_map.get(label, 'grey'), lw=4) for label in labels_for_legend]
    fig.legend(handles, labels_for_legend, loc='upper right', fontsize='x-small')
    fix_labels_based_on_touch(annotated_texts)
    fig.text(1, 0, footnote, fontsize=8, style='italic', ha='right', va='bottom', color='black')
    plt.title(fig_name, size='x-large', weight='bold', y=1.05)
    plt.tight_layout()
    return fig, df

