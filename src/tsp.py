# Import
# -----------------------------------------------------------------------------
import time
from typing import Any

import pyscipopt


# Main
# -----------------------------------------------------------------------------
print(f"-" * 8)


# 都市の集合（便宜上、リストを用いる）
City = ["A", "B", "C", "D"]

print(f"都市の集合 I = {City}")


# # タスクの集合（便宜上、リストを用いる）
# J = ["仕事イ", "仕事ロ", "仕事ハ"]

# print(f"タスクの集合 J = {J}")


# 各都市間の移動コストの集合（一時的なリスト）
tmpCost = [
    [0, 6, 5, 5],
    [6, 0, 7, 4],
    [5, 7, 0, 3],
    [5, 4, 3, 0]
]
# tmpCost = [
#     [0, 6.5, 5.2, 5.1],
#     [6.9, 0, 7.2, 4.1],
#     [5.1, 7.1, 0, 3.9],
#     [5.1, 4.2, 3.3, 0]
# ]

# cc はリストであり、添え字が数値なので、
# 辞書 c を定義し、例えば cc[0][0] は c["Aさん", "仕事イ"] でアクセスするようにする
Cost = {}  # 空の辞書
for i in City:
    for j in City:
        Cost[i, j] = tmpCost[City.index(i)][City.index(j)]

print(f"コスト Cost[i,j]: ")
for i in City:
    print(f"    ", end="")
    for j in City:
        print(f"Cost[{i},{j}] = {Cost[i,j]},  ", end="")
    print(f"")
print(f"")


# 数理最適化モデルを宣言
m = pyscipopt.Model(
    problemName="Problem-2",
)


# 変数集合を表す辞書
x = {}  # 空の辞書
# x[i,j] または x[(i,j)] で、(i,j) というタプルをキーにしてバリューを読み書き

# 0-1変数を宣言
for i in City:
    for j in City:
        if i == j:
            continue
        x[i, j] = m.addVar(
            name=f"Var_x({i},{j})",
            vtype="B",
        )

y = {}
# 整数の中間変数を宣言
for i in City:
    if City.index(i) == 0:
        continue
    y[i] = m.addVar(
        name=f"Var_y({i})",
        vtype="I",
    )


# 目的関数を宣言
m.setObjective(
    pyscipopt.quicksum(Cost[i, j] * x[i, j] for i in City for j in City if i != j),
    sense="minimize",
)

# 制約条件を宣言
# 都市iから別都市の1つに移動する
for i in City:
    m.addCons(
        pyscipopt.quicksum(x[i, j] for j in City if i != j) == 1,
        name=f"Constraint_from_{i}",
    )

# 都市iへ別都市の1つから移動する
for i in City:
    m.addCons(
        pyscipopt.quicksum(x[j, i] for j in City if i != j) == 1,
        name=f"Constraint_for_{i}",
    )

# 中間変数の訪問順の上下限
for i in City:
    if City.index(i) == 0:
        continue
    m.addCons(y[i] <= len(City)-1)
    m.addCons(y[i] >= 1)

# サブツアー排除制約
for i in City:
    if City.index(i) == 0:
        continue
    for j in City:
        if City.index(j) == 0:
            continue
        if i == j :
            continue
        m.addCons(y[i] - y[j] + 3*x[i, j] <= len(City)-2)


print(f"-" * 8)


# 計算
time_start: float = time.perf_counter()
m.optimize()
time_stop: float = time.perf_counter()
print(f"")


print(f"-" * 8)


# （解が得られていれば）目的関数値や解を表示
print(f"最適性 = {m.getStatus()}, ", end="")
print(f"目的関数値 = {m.getObjVal()}, ", end="")
print(f"計算時間 = {time_stop - time_start:.3f} (秒)")
print(f"解 x[i,j]: ")
for i in City:
    print(f"    ", end="")
    for j in City:
        if i == j:
            continue
        print(f"{x[i,j]} = {m.getVal(x[i,j])},  ", end="")
    print(f"")
print(f"")
