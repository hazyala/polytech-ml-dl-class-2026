# =============================================================
# 식인종-선교사 문제 (Missionaries and Cannibals Problem)
#
# [핵심 아이디어]
#   염색체 길이를 20부터 1씩 줄여가며 유전자 알고리즘 실행
#   해당 길이에서 승리 가능한 염색체를 찾으면 출력 후 길이 감소
#   더 이상 승리 불가능한 길이에서 멈춤 → 최소 길이 확인
#
# [구조]
#   외부 while: 염색체 길이 20 -> 19 -> 18 -> ...
#   내부 for  : 해당 길이로 유전자 알고리즘, 매 세대 적합도 출력
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
        gene = chromosome[idx]
        idx += 1

        if gene == prev_cmd:
            continue
        next_status = game(status, gene)
        if next_status is None:
            continue
        if next_status.to_tuple() in visited:
            continue

        result = judge(next_status)
        history.append(next_status.clone())
        visited.add(next_status.to_tuple())
        status   = next_status
        prev_cmd = gene

        if result == 'win':
            return 'win', history
        elif result == 'gameover':
            return 'gameover', history

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
# 유전자 알고리즘 (염색체 길이를 파라미터로 받음)
# -------------------------------------------------------------
POP_SIZE      = 200
GENERATIONS   = 200
MUTATION_RATE = 0.1
ELITE_SIZE    = 10

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
    point  = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(individual):
    return [random.randint(0, 4) if random.random() < MUTATION_RATE else g
            for g in individual]

def genetic_algorithm(length):
    population = [create_individual(length) for _ in range(POP_SIZE)]
    best_ind   = None
    best_fit   = -9999

    for gen in range(GENERATIONS):
        fitnesses = [fitness(ind) for ind in population]
        gen_best_fit = max(fitnesses)
        gen_best_ind = population[fitnesses.index(gen_best_fit)]

        if gen_best_fit > best_fit:
            best_fit = gen_best_fit
            best_ind = gen_best_ind

        # 매 세대 적합도 출력
        result, _ = run_chromosome(gen_best_ind)
        status_str = "WIN" if result == 'win' else ("OVER" if result == 'gameover' else "----")
        print(f"    세대 {gen+1:3d} | 최고 적합도: {gen_best_fit:5d} | {status_str}")

        # 승리 염색체 발견 시 조기 종료
        if result == "win":
            print(f"    -> 길이 {length}: 승리 염색체 발견 (세대 {gen+1})")
            return best_ind, True

        # 엘리트 보존
        sorted_pop = [x for _, x in sorted(zip(fitnesses, population),
                      key=lambda p: p[0], reverse=True)]
        new_pop  = sorted_pop[:ELITE_SIZE]
        selected = selection(population, fitnesses)
        while len(new_pop) < POP_SIZE:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutate(c1))
            if len(new_pop) < POP_SIZE:
                new_pop.append(mutate(c2))
        population = new_pop

    return best_ind, False


# -------------------------------------------------------------
# 게임 경로 출력
# -------------------------------------------------------------
def print_game_path(chromosome):
    status   = Status()
    visited  = set()
    visited.add(status.to_tuple())
    prev_cmd = None
    idx      = 0
    step     = 0

    print(f"  초기 | {status}")

    while idx < len(chromosome):
        gene = chromosome[idx]
        idx += 1
        if gene == prev_cmd:
            continue
        next_status = game(status, gene)
        if next_status is None:
            continue
        if next_status.to_tuple() in visited:
            continue

        visited.add(next_status.to_tuple())
        direction = "-> 오른쪽" if status.boat == 'left' else "<- 왼쪽 "
        step += 1
        result = judge(next_status)
        print(f"  스텝{step:2d} | {direction} [{COMMAND_NAMES[gene]}] -> {next_status}")
        status   = next_status
        prev_cmd = gene

        if result in ('win', 'gameover'):
            break


# -------------------------------------------------------------
# 메인: 외부 while - 염색체 길이 20부터 1씩 감소
# -------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 65)
    print("  식인종-선교사 문제 | 유전자 알고리즘 (염색체 길이 축소)")
    print("=" * 65)

    MAX_LEN     = 20
    best_chromosome = None
    best_length     = None

    length = MAX_LEN

    # 외부 while: 길이 20부터 줄여가며 반복
    while length >= 1:
        print(f"\n{'='*65}")
        print(f"  [염색체 길이: {length}] 유전자 알고리즘 실행")
        print(f"{'='*65}")

        chromosome, solved = genetic_algorithm(length)
        result, history    = run_chromosome(chromosome)

        if solved and result == 'win':
            print(f"\n  길이 {length} -> 승리 가능! 경로 저장 후 길이 축소 시도\n")
            best_chromosome = chromosome
            best_length     = length
            length -= 1
        else:
            print(f"\n  길이 {length} -> {GENERATIONS}세대 내 승리 불가. 탐색 종료.")
            break

    # 최종 결과 출력
    print("\n" + "=" * 65)
    print("  최종 결과")
    print("=" * 65)

    if best_chromosome is not None:
        print(f"  최소 승리 염색체 길이: {best_length}")
        print(f"  염색체: {best_chromosome}")
        print()
        print_game_path(best_chromosome)
        print(f"\n  게임 승리 (총 {len(run_chromosome(best_chromosome)[1])-1}스텝)")
    else:
        print("  승리 염색체를 찾지 못했습니다.")