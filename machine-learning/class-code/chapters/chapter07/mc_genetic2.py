# =============================================================
# 식인종-선교사 문제 (Missionaries and Cannibals Problem)
#
# [모드 선택]
#   1. 수동 모드 (INPUT)   : 사람이 직접 커맨드를 입력
#   2. 자동 모드 (자동화)  : 유전자 알고리즘이 커맨드를 자동 선택
#
# [프로그램 구조] - 수업 설계도 기반
#   환경(Status) + Command -> 게임(Game) -> 다음 환경(Status) -> 판정(Judge)
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
# 게임(Game): 현재 상태 + 커맨드 -> 다음 상태
# -------------------------------------------------------------
def game(status, command):
    s = status.clone()
    m, c = COMMANDS[command]

    if s.boat == 'left':
        if s.left_m < m or s.left_c < c:
            return None
        s.left_m  -= m;  s.left_c  -= c
        s.right_m += m;  s.right_c += c
        s.boat = 'right'
    else:
        if s.right_m < m or s.right_c < c:
            return None
        s.right_m -= m;  s.right_c -= c
        s.left_m  += m;  s.left_c  += c
        s.boat = 'left'

    return s


# -------------------------------------------------------------
# 판정(Judge): 다음 상태 -> 'gameover' / 'win' / 'continue'
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
# 가능한 커맨드 목록 반환
# -------------------------------------------------------------
def get_valid_commands(status):
    valid = []
    for cmd in COMMANDS:
        if game(status, cmd) is not None:
            valid.append(cmd)
    return valid


# -------------------------------------------------------------
# 상태 출력
# -------------------------------------------------------------
def print_status(step, status):
    print(f"\n  [스텝 {step}] {status}")


def print_commands(valid_cmds):
    print("  사용 가능한 커맨드:")
    for cmd in valid_cmds:
        print(f"    {cmd} : {COMMAND_NAMES[cmd]}")


# -------------------------------------------------------------
# 수동 모드 (INPUT)
# -------------------------------------------------------------
def run_manual():
    print("\n" + "=" * 60)
    print("  [수동 모드] 커맨드를 직접 입력하세요")
    print("=" * 60)

    status = Status()
    step   = 0

    while True:
        print_status(step, status)

        valid_cmds = get_valid_commands(status)
        print_commands(valid_cmds)

        # 커맨드 입력
        while True:
            try:
                cmd = int(input("  커맨드 번호 입력 >> "))
                if cmd in valid_cmds:
                    break
                else:
                    print("  불가능한 커맨드입니다. 다시 입력하세요.")
            except ValueError:
                print("  숫자를 입력하세요.")

        next_status = game(status, cmd)
        step += 1
        direction = "-> 오른쪽" if status.boat == 'left' else "<- 왼쪽 "
        print(f"\n  {direction} [{COMMAND_NAMES[cmd]}]")

        result = judge(next_status)
        status = next_status
        print_status(step, status)

        if result == 'win':
            print("\n  결과: 게임 승리! (총 {}스텝)".format(step))
            break
        elif result == 'gameover':
            print("\n  결과: 게임 오버!")
            break


# -------------------------------------------------------------
# 자동 모드 - 유전자 알고리즘
# -------------------------------------------------------------
CHROMOSOME_LEN = 20
POP_SIZE       = 200
GENERATIONS    = 300
MUTATION_RATE  = 0.1
ELITE_SIZE     = 10

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


def fitness(chromosome):
    result, history = run_chromosome(chromosome)
    if result == 'win':
        return 1000 - len(history)
    last  = history[-1]
    score = (last.right_m + last.right_c) * 10
    if result == 'gameover':
        score -= 50
    return score


def create_individual():
    return [random.randint(0, 4) for _ in range(CHROMOSOME_LEN)]

def selection(population, fitnesses):
    selected = []
    for _ in range(len(population)):
        candidates = random.sample(list(zip(population, fitnesses)), 5)
        winner = max(candidates, key=lambda x: x[1])
        selected.append(winner[0])
    return selected

def crossover(p1, p2):
    point  = random.randint(1, CHROMOSOME_LEN - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]

def mutate(individual):
    return [random.randint(0, 4) if random.random() < MUTATION_RATE else g
            for g in individual]

def genetic_algorithm():
    population = [create_individual() for _ in range(POP_SIZE)]
    for gen in range(GENERATIONS):
        fitnesses = [fitness(ind) for ind in population]
        best_fit  = max(fitnesses)
        best_ind  = population[fitnesses.index(best_fit)]

        if best_fit >= 990:
            return best_ind, gen + 1

        sorted_pop = [x for _, x in sorted(zip(fitnesses, population),
                      key=lambda p: p[0], reverse=True)]
        new_pop = sorted_pop[:ELITE_SIZE]
        selected = selection(population, fitnesses)
        while len(new_pop) < POP_SIZE:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2)
            new_pop.append(mutate(c1))
            if len(new_pop) < POP_SIZE:
                new_pop.append(mutate(c2))
        population = new_pop

    fitnesses = [fitness(ind) for ind in population]
    best_ind  = population[fitnesses.index(max(fitnesses))]
    return best_ind, GENERATIONS


def run_auto():
    print("\n" + "=" * 60)
    print("  [자동 모드] 유전자 알고리즘으로 해답 탐색 중...")
    print("=" * 60)

    attempt = 1

    # 외부 while: 승리할 때까지 반복
    while True:
        print(f"\n  [시도 {attempt}회차] 진화 중...")
        best, gen = genetic_algorithm()
        result, history = run_chromosome(best)

        if result == 'win':
            print(f"  해답 발견 ({gen}세대)\n")
            break
        attempt += 1

    # 찾은 염색체를 한 스텝씩 출력
    status   = Status()
    visited  = set()
    visited.add(status.to_tuple())
    prev_cmd = None
    idx      = 0
    step     = 0

    print_status(step, status)

    while idx < len(best):
        gene = best[idx]
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
        print(f"\n  커맨드: [{COMMAND_NAMES[gene]}]  {direction}")

        result  = judge(next_status)
        status  = next_status
        prev_cmd = gene
        print_status(step, status)

        if result == 'win':
            print("\n  결과: 게임 승리! (총 {}스텝)".format(step))
            break
        elif result == 'gameover':
            print("\n  결과: 게임 오버!")
            break


# -------------------------------------------------------------
# 메인: 모드 선택
# -------------------------------------------------------------
if __name__ == '__main__':
    print("=" * 60)
    print("  식인종-선교사 문제")
    print("=" * 60)
    print("  초기 상태: 왼쪽(선교사 3, 식인종 3) / 배: 왼쪽")
    print("  목표: 모두 오른쪽으로 이동")
    print()
    print("  1. 수동 모드 (직접 입력)")
    print("  2. 자동 모드 (유전자 알고리즘)")
    print()

    while True:
        try:
            mode = int(input("  모드 선택 (1 or 2) >> "))
            if mode in (1, 2):
                break
            print("  1 또는 2를 입력하세요.")
        except ValueError:
            print("  숫자를 입력하세요.")

    if mode == 1:
        run_manual()
    else:
        run_auto()