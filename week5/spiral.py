#!/usr/bin/env python3
import sys
import math

from common import print_tour, read_input

def spiral_tour(cities):
    center_x = sum(x for x, y in cities)/len(cities)
    center_y = sum(y for x, y in cities)/len(cities)

    city = []
    for i, (x, y) in enumerate(cities):
        dx = x - center_x
        dy = y - center_y
        angle = math.atan2(dy, dx)
        radius = math.hypot(dx, dy)
        city.append((angle, radius, i))
    
    city.sort(key=lambda x:(-x[0], x[1]))  # 角度でソート、同じ角度なら半径でソート
    tour = [i for _, _, i in city]  # ソートされたインデックスを取得
    return tour

#python my_solver.py input_0.csv > output_0.csvでoutput_0.csvに結果が出力される
if __name__ == '__main__':
    assert len(sys.argv) == 2, "入力ファイルを１つだけ指定してください"
    cities = read_input(sys.argv[1])  # [(x,y),...]
    tour0 = spiral_tour(cities)
    print_tour(tour0)