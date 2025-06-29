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

def two_opt(cities, tour):
    def dist(i, j):
        dx = cities[i][0] - cities[j][0]
        dy = cities[i][1] - cities[j][1]
        return math.hypot(dx, dy) #原点からの距離を計算
    
    #改善があったかどうかをフラグで記録し改善がなくなるまでループ
    n = len(tour)
    improved = True
    while improved:
        improved = False

        for i in range(1, n-2): 
            for j in range(i + 1, n-1): #隣り合う辺を選ばないように
                a, b = tour[i - 1], tour[i]
                c, d = tour[j], tour[j + 1]

                before = dist(a, b) + dist(c, d)
                after = dist(a, c) + dist(b, d)
                if after < before:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
    return tour

#python my_solver.py input_0.csv > output_0.csvでoutput_0.csvに結果が出力される
if __name__ == '__main__':
    assert len(sys.argv) == 2, "入力ファイルを１つだけ指定してください"
    cities = read_input(sys.argv[1])  # [(x,y),...]
    tour0 = spiral_tour(cities)
    tour1 = two_opt(cities, tour0)
    print_tour(tour1)