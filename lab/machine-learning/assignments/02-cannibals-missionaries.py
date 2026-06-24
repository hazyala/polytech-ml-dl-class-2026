# =============================================================
# 식인종-선교사 문제 (Missionaries and Cannibals Problem)
#
# [핵심 아이디어 - 10세대마다 길이 축소]
#   단일 유전자 알고리즘 루프 안에서
#   10세대마다 염색체 길이를 1씩 줄여나감
#   길이가 줄어들 때 집단의 염색체도 앞부분만 잘라서 유지
#   WIN이 나온 시점의 길이와 경로를 기록
# =============================================================

import random

# -------------------------------------------------------------
# 상태(Status) 정의
# -------------------------------------------------------------
class Status:
    def __init__(self, left_m=3, left_c=3, right_m=0, right_c=0, boat='left'):
        self.left_m  = left_m
        self.left_c  = left_c
        self.right_m = right_m
        self.right_c = right_c
        self.boat    = boat

    def clone(self):
        return Status(self.left_m, self.left_c, self.right_m, self.right_c, self.boat)

    def to_tuple(self):
        return (self.left_m, self.left_c, self.right_m, self.right_c, self.boat)

    def __str__(self):
        side = "왼쪽" if self.boat == 'left' else "오른쪽"
        return (f"[왼쪽] 선교사:{self.left_m} 식인종:{self.left_c} "
                f"| 배:{side} | "
                f"[오른쪽] 선교사:{self.right_m} 식인종:{self.right_c}")


# -------------------------------------------------------------
# Command 정의
# -------------------------------------------------------------
COMMANDS = {
    0: (1, 0),
    1: (2, 0),
    2: (0, 1),
    3: (0, 2),
    4: (1, 1),
}
COMMAND_NAMES = {
    0: "선교사 1명",
    1: "선교사 2명",
    2: "식인종 1명",
    3: "식인종 2명",
    4: "선교사 1명 + 식인종 1명",
}


# -------------------------------------------------------------
# 게임(Game)
# -------------------------------------------------------------
def game(status, command):
    s = status.clone()
    m, c = COMMANDS[command]
    if s.boat == 'left':
        if s.left_m < m or s.left_c < c:
            return None
        s.left_m -= m;  s.left_c -= c
        s.right_m += m; s.right_c += c
        s.boat = 'right'
    else:
        if s.right_m < m or s.right_c < c:
            return None
        s.right_m -= m; s.right_c -= c
        s.left_m += m;  s.left_c += c
        s.boat = 'left'
    return s


# -------------------------------------------------------------
# 판정(Judge)
# -------------------------------------------------------------
def judge(status):
    if status.left_m > 0 and status.left_m < status.left_c:
        return 'gameover'
    if status.right_m > 0 and status.right_m < status.right_c:
        return 'gameover'
    if status.right_m == 3 and status.right_c == 3:
        return 'win'
    return 'continue'


# -------------------------------------------------------------
# 염색체 실행
# -------------------------------------------------------------
def run_chromosome(chromosome):
    status   = Status()
    history  = [status.clone()]
    visited  = set()
    visited.add(status.to_tuple())
    prev_cmd = None
    idx      = 0

    while idx < len(chromosome):
        gene = chromosome[idx]; idx += 1
        if gene == prev_cmd: continue
        next_status = game(status, gene)
        if next_status is None: continue
        if next_status.to_tuple() in visited: continue
        result = judge(next_status)
        history.append(next_status.clone())
        visited.add(next_status.to_tuple())
        status   = next_status
        prev_cmd = gene
        if result == 'win':   return 'win', history
        if result == 'gameover': return 'gameover', history

    return 'continue', history


# -------------------------------------------------------------
# 평가함수(Fitness)
# -------------------------------------------------------------
def fitness(chromosome):
    result, history = run_chromosome(chromosome)
    if result == 'win':
        return 1000 - len(history)
    last  = history[-1]
    score = (last.right_m + last.right_c) * 10
    if result == 'gameover':
        score -= 50
    return score


# -------------------------------------------------------------
# 유전자 연산
# -------------------------------------------------------------
POP_SIZE      = 200
GENERATIONS   = 300
MUTATION_RATE = 0.15
ELITE_SIZE    = 10
SHRINK_EVERY  = 10   # 몇 세대마다 길이 축소

def create_individual(length):
    return [random.randint(0, 4) for _ in range(length)]

def selection(population, fitnesses):
    selected = []
    for _ in range(len(population)):
        candidates = random.sample(list(zip(population, fitnesses)), 5)
        winner = max(candidates, key=lambda x: x[1])
        selected.append(winner[0])
    return selected

def crossover(p1, p2):
    if len(p1) < 2:
        return p1[:], p2[:]
    point  = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(individual):
    return [random.randint(0, 4) if random.random() < MUTATION_RATE else g
            for g in individual]

def trim_population(population, new_length):
    return [ind[:new_length] for ind in population]


# -------------------------------------------------------------
# 게임 경로 출력
# -------------------------------------------------------------
def print_game_path(chromosome):
    status   = Status()
    visited  = set()
    visited.add(status.to_tuple())
    prev_cmd = None
    idx = 0; step = 0
    print(f"  초기 | {status}")
    while idx < len(chromosome):
        gene = chromosome[idx]; idx += 1
        if gene == prev_cmd: continue
        next_status = game(status, gene)
        if next_status is None: continue
        if next_status.to_tuple() in visited: continue
        visited.add(next_status.to_tuple())
        direction = "-> 오른쪽" if status.boat == 'left' else "<- 왼쪽 "
        step += 1
        result = judge(next_status)
        print(f"  스텝{step:2d} | {direction} [{COMMAND_NAMES[gene]}] -> {next_status}")
        status = next_status; prev_cmd = gene
        if result in ('win', 'gameover'): break


# -------------------------------------------------------------
# 메인: 10세대마다 염색체 길이 1 축소
# -------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 65)
    print("  식인종-선교사 문제 | 유전자 알고리즘 (10세대마다 길이 축소)")
    print("=" * 65)
    print(f"  시작 길이: 20  |  {SHRINK_EVERY}세대마다 길이 1 감소")
    print("=" * 65)

    cur_length  = 20
    population  = [create_individual(cur_length) for _ in range(POP_SIZE)]
    best_win_chromosome = None
    best_win_length     = None

    for gen in range(1, GENERATIONS + 1):

        # 10세대마다 길이 축소
        if gen > 1 and (gen - 1) % SHRINK_EVERY == 0 and cur_length > 1 and best_win_chromosome is not None:
            cur_length -= 1
            population  = trim_population(population, cur_length)
            print(f"  {'─'*57}")
            print(f"  >>> {SHRINK_EVERY}세대 경과 -> 염색체 길이 축소: {cur_length+1} -> {cur_length}")
            print(f"  {'─'*57}")

        fitnesses  = [fitness(ind) for ind in population]
        best_fit   = max(fitnesses)
        best_ind   = population[fitnesses.index(best_fit)]
        result, _  = run_chromosome(best_ind)
        status_str = "WIN " if result == 'win' else ("OVER" if result == 'gameover' else "----")

        print(f"  세대 {gen:3d} | 길이 {cur_length:2d} | 최고 적합도: {best_fit:5d} | {status_str}")

        # WIN 기록 (가장 최근 + 짧은 길이 우선)
        if result == 'win':
            if best_win_length is None or cur_length <= best_win_length:
                best_win_chromosome = best_ind[:]
                best_win_length     = cur_length

        # 엘리트 보존
        sorted_pop = [x for _, x in sorted(zip(fitnesses, population),
                      key=lambda p: p[0], reverse=True)]
        new_pop    = sorted_pop[:ELITE_SIZE]
        selected   = selection(population, fitnesses)
        while len(new_pop) < POP_SIZE:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutate(c1))
            if len(new_pop) < POP_SIZE:
                new_pop.append(mutate(c2))
        population = new_pop

    # 최종 결과
    print("\n" + "=" * 65)
    print("  최종 결과")
    print("=" * 65)
    if best_win_chromosome is not None:
        steps = len(run_chromosome(best_win_chromosome)[1]) - 1
        print(f"  WIN 달성 최소 염색체 길이: {best_win_length}")
        print(f"  염색체: {best_win_chromosome}\n")
        print_game_path(best_win_chromosome)
        print(f"\n  게임 승리 (총 {steps}스텝)")
    else:
        print("  WIN 달성 염색체를 찾지 못했습니다.")
    print("=" * 65)