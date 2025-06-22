#!/usr/bin/env python3
import sys
import math

from common import print_tour, read_input

def distance(city1, city2):
    return math.sqrt((city1[0] - city2[0]) ** 2 + (city1[1] - city2[1]) ** 2)


def solve(cities):
    N = len(cities)

    dist = [[0] * N for i in range(N)]
    for i in range(N):
        for j in range(i, N):
            dist[i][j] = dist[j][i] = distance(cities[i], cities[j])

    current_city = 0
    unvisited_cities = set(range(1, N))
    tour = [current_city]

    while unvisited_cities:
        next_city = min(unvisited_cities,
                        key=lambda city: dist[current_city][city])
        unvisited_cities.remove(next_city)
        tour.append(next_city)
        current_city = next_city
    return tour

def two_opt(cities, tour):
    def dist(i, j):
        dx = cities[i][0] - cities[j][0]
        dy = cities[i][1] - cities[j][1]
        return math.hypot(dx, dy)
    
    n = len(tour)
    improved = True
    while improved:
        improved = False

        for i in range(1, n-2):
            for j in range(i + 1, n-1):
                a, b = tour[i - 1], tour[i]
                c, d = tour[j], tour[j + 1]

                before = dist(a, b) + dist(c, d)
                after = dist(a, c) + dist(b, d)
                if after < before:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
    return tour

if __name__ == '__main__':
    assert len(sys.argv) == 2, "入力ファイルを１つだけ指定してください"
    cities = read_input(sys.argv[1])  # [(x,y),...]
    # 1) 初期ツアーを作成
    tour0 = solve(cities)
    # 2) 2-opt で改善
    tour1 = two_opt(cities, tour0)
    # 3) 結果を出力
    print_tour(tour1)