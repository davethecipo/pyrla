# Testare cose a mano
import boxcars_py
import pprint

#####################################
# Guardo a mano la struttura del dato

test_path = '../../../replays/ezname.replay'

with open(test_path, 'rb') as f:
    parsed = boxcars_py.parse_replay(f.read())

def take_a_look(d):
    """Look easily at dicts of lists of dicts."""
    
    res = {}
    for k, el in d.items():
        
        if isinstance(el, (list, tuple)):
            if len(el) != 0:
                tel = el[0]
            else:
                tel = 'empty'
            num = len(el)
        else:
            tel = el
            num = 'S'
            
        if isinstance(tel, dict):
            res[f'{k} ({num})'] = take_a_look(tel)
        else:
            pr_str = f"{type(tel).__name__} ({tel})"
            res[f'{k} ({num})'] = pr_str
            
    return res

parsed_look = take_a_look(parsed)
pp = pprint.PrettyPrinter(indent=0)

print('\n')
pp.pprint(parsed_look)


###################################
# Uso carball per il pre-processing

import carball
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager

_json = carball.decompile_replay('../../../replays/ezname.replay')
game = Game()
game.initialize(loaded_json=_json)

analysis_manager = AnalysisManager(game)
analysis_manager.create_analysis()
    
# return the proto object in python
proto_object = analysis_manager.get_protobuf_data()

# return the proto object as a json object
json_oject = analysis_manager.get_json_data()

# return the pandas data frame in python
df = analysis_manager.get_data_frame()


###################################
# Gioco con df
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits import mplot3d
plt.ion()

def obj_pos_tuple(name):
    x = df[name]['pos_x']
    y = df[name]['pos_y']
    z = df[name]['pos_z']
    return x, y, z
    
ax = plt.axes(projection='3d')
ax.plot3D(*obj_pos_tuple('Nik'))
ax.plot3D(*obj_pos_tuple('import csv'))
ax.plot3D(*obj_pos_tuple('ball'))

delta_x_nik = df['ball']['pos_x'] - df['Nik']['pos_x'] 
delta_y_nik = df['ball']['pos_y'] - df['Nik']['pos_y']
delta_x_cipo = df['ball']['pos_x'] - df['import csv']['pos_x'] 
delta_y_cipo = df['ball']['pos_y'] - df['import csv']['pos_y']

ax = plt.axes()
ax.plot(delta_x_nik, delta_y_nik)
ax.plot(delta_x_cipo, delta_y_cipo)
ax.set_aspect('equal')

def find_bounds(pos_str):
    vals = df.loc[:, (slice(None), pos_str)]
    return vals.min().min(), vals.max().max()
x_bounds = find_bounds('pos_x')
y_bounds = find_bounds('pos_y')
z_bounds = find_bounds('pos_z')

import time

matplotlib.interactive(True)
ax = plt.axes(projection='3d')
ax.set_xlim(*x_bounds)
ax.set_ylim(*y_bounds)
ax.set_zlim(*z_bounds)

for _, s in df.iterrows():
    
    for n in ['ball', 'Nik', 'import csv', 'Look-My-Has', 'dard-reelu']:
        pl3d = ax.plot3D(
            s[n].pos_x, s[n].pos_y, s[n].pos_z,
            ms=20 if n == 'ball' else 10,
            marker='.')
    plt.draw()
    ax.set_xlim(*x_bounds)
    ax.set_ylim(*y_bounds)
    ax.set_zlim(*z_bounds)
    plt.pause(s['game'].delta/10)
    ax.cla()


    
###################################
# Parso tanti

import carball
from carball.json_parser.game import Game
from carball.analysis.analysis_manager import AnalysisManager
import glob
import os
import pandas as pd
import numpy as np

def parse_folder(folder_path):
    paths = glob.glob(os.path.join(folder_path, '*.replay'))
    df = {}
    for i, path in enumerate(paths):
        print(f"Processing {path}")
        _json = carball.decompile_replay(path)
        game = Game()
        game.initialize(loaded_json=_json)
        
        analysis_manager = AnalysisManager(game)
        analysis_manager.create_analysis()
        df[i] = analysis_manager.get_data_frame()
    return pd.concat(df, axis=1)

df = parse_folder('../../../replays')

boost_active_mean = df.xs('boost_active', axis=1, level=2).mean()

ball_x_dist = df.xs('pos_x', axis=1, level=2).sub(df.xs('ball', axis=1, level=1).xs('pos_x', axis=1, level=1), axis=1, level=0).drop('ball', axis=1, level=1)
ball_y_dist = df.xs('pos_y', axis=1, level=2).sub(df.xs('ball', axis=1, level=1).xs('pos_y', axis=1, level=1), axis=1, level=0).drop('ball', axis=1, level=1)
ball_z_dist = df.xs('pos_z', axis=1, level=2).sub(df.xs('ball', axis=1, level=1).xs('pos_z', axis=1, level=1), axis=1, level=0).drop('ball', axis=1, level=1)

ball_h_dist = (ball_x_dist ** 2 + ball_y_dist ** 2) ** 0.5
ball_v_dist = ball_z_dist.abs()
boost_active = df.xs('boost_active', axis=1, level=2)

bh = ball_h_dist.loc[:, (slice(None), ['Nik', 'import csv'])]
bv = ball_h_dist.loc[:, (slice(None), ['Nik', 'import csv'])]
ba = boost_active.loc[:, (slice(None), ['Nik', 'import csv'])]

bh_cut = pd.cut(bh.stack([0, 1]), bins=100)
bv_cut = pd.cut(bv.stack([0, 1]), bins=100)
boost_fun_of_hdist = ba.stack([0, 1]).groupby([bh_cut, bh_cut.index.get_level_values(2)]).mean().unstack()