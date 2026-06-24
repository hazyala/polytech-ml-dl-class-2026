import random
import copy

# ============================================================
# 상태(Status) 정의
# ============================================================
class Status:
    def __init__(self, left_m=3, left_c=3, right_m=0, right_c=0, boat='left'):
        self.left_m = left_m    # 왼쪽 선교사 수
        self.left_c = left_c    # 왼쪽 식인종 수
        self.right_m = right_m  # 오른쪽 선교사 수
        self.right_c = right_c  # 오른쪽 식인종 수
        self.boat = boat        # 배 위치 ('left' or 'right')

    def clone(self):
        return Status(self.left_m, self.left_c, self.right_m, self.right_c, self.boat)

    def to_tuple(self):
        return (self.left_m, self.left_c, self.right_m, self.right_c, self.boat)

    def __str__(self):
        return (f"[왼쪽] 선교사:{self.left_m} 식인종:{self.left_c} | "
                f"배:{'←왼쪽' if self.boat=='left' else '오른쪽→'} | "
                f"[오른쪽] 선교사:{self.right_m} 식인종:{self.right_c}")


# ============================================================
# Command 정의 (5가지)
# ============================================================
COMMANDS = {
    0: (1, 0),  # 선교사 1명
    1: (2, 0),  # 선교사 2명
    2: (0, 1),  # 식인종 1명
    3: (0, 2),  # 식인종 2명
    4: (1, 1),  # 선교사 1명 + 식인종 1명
}
COMMAND_NAMES = {
    0: "선교사 1명",
    1: "선교사 2명",
    2: "식인종 1명",
    3: "식인종 2명",
    4: "선교사 1명 + 식인종 1명",
}


# ============================================================
# 게임(Game): 상태 + 커맨드 → 다음 상태
# ============================================================
def game(status, command):
    s = status.clone()
    m, c = COMMANDS[command]

    # 제약조건: 해당 사람 수 이상이어야 가능
    if s.boat == 'left':
        if s.left_m < m or s.left_c < c:
            return None  # 불가능한 커맨드
        s.left_m -= m
        s.left_c -= c
        s.right_m += m
        s.right_c += c
        s.boat = 'right'
    else:
        if s.right_m < m or s.right_c < c:
            return None  # 불가능한 커맨드
        s.right_m -= m
        s.right_c -= c
        s.left_m += m
        s.left_c += c
        s.boat = 'left'

    return s


# ============================================================
# 판정(Judge): 다음 상태 → 계속/게임오버/승리
# ============================================================
def judge(status):
    # 배 위치 쪽의 선교사 < 식인종 이면 게임오버 (선교사가 0명이면 해당없음)
    if status.boat == 'left':
        if status.left_m > 0 and status.left_m < status.left_c:
            return 'gameover'
        if status.right_m > 0 and status.right_m < status.right_c:
            return 'gameover'
    else:
        if status.right_m > 0 and status.right_m < status.right_c:
            return 'gameover'
        if status.left_m > 0 and status.left_m < status.left_c:
            return 'gameover'

    # 오른쪽 선교사==3, 식인종==3 이면 승리
    if status.right_m == 3 and status.right_c == 3:
        return 'win'

    return 'continue'


# ============================================================
# 염색체 실행: 염색체(command 리스트) → 점수 + 이력
# ============================================================
CHROMOSOME_LEN = 20

def run_chromosome(chromosome):
    status = Status()
    history = [status.clone()]
    visited = set()
    visited.add(status.to_tuple())
    prev_command = None

    for gene in chromosome:
        # 문제의 상황 1: 이전 커맨드와 같으면 스킵 (무한반복 방지)
        if gene == prev_command:
            continue

        next_status = game(status, gene)

        if next_status is None:
            continue  # 불가능한 커맨드 무시

        # 문제의 상황 2: 이미 방문한 상태면 스킵 (무한반복 방지)
        if next_status.to_tuple() in visited:
            continue

        result = judge(next_status)
        history.append(next_status.clone())
        visited.add(next_status.to_tuple())
        status = next_status
        prev_command = gene

        if result == 'win':
            return 'win', history
        elif result == 'gameover':
            return 'gameover', history

    return 'continue', history


# ============================================================
# 평가함수(Fitness)
# ============================================================
def fitness(chromosome):
    result, history = run_chromosome(chromosome)

    if result == 'win':
        # 승리 시 최고 점수 (적은 스텝일수록 보너스)
        return 1000 - len(history)

    last = history[-1]
    # 오른쪽으로 이동한 진척도 (선교사+식인종 합계)
    score = (last.right_m + last.right_c) * 10

    if result == 'gameover':
        score -= 50  # 게임오버 패널티

    return score


# ============================================================
# 유전자 알고리즘
# ============================================================
POP_SIZE = 200
GENERATIONS = 500
MUTATION_RATE = 0.1
ELITE_SIZE = 10

def create_individual():
    return [random.randint(0, 4) for _ in range(CHROMOSOME_LEN)]

def selection(population, fitnesses):
    # 토너먼트 선택
    tournament_size = 5
    selected = []
    for _ in range(len(population)):
        tournament = random.sample(list(zip(population, fitnesses)), tournament_size)
        winner = max(tournament, key=lambda x: x[1])
        selected.append(winner[0])
    return selected

def crossover(parent1, parent2):
    point = random.randint(1, CHROMOSOME_LEN - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(individual):
    return [random.randint(0, 4) if random.random() < MUTATION_RATE else gene
            for gene in individual]

def genetic_algorithm():
    population = [create_individual() for _ in range(POP_SIZE)]

    for gen in range(GENERATIONS):
        fitnesses = [fitness(ind) for ind in population]
        best_fit = max(fitnesses)
        best_ind = population[fitnesses.index(best_fit)]

        result, _ = run_chromosome(best_ind)

        if result == 'win':
            print(f"\n[확인] {gen+1}세대에서 해답 발견! (점수: {best_fit})")
            return best_ind, gen+1

        if gen % 50 == 0:
            print(f"세대 {gen:4d} | 최고점수: {best_fit:5d}")

        # 엘리트 보존
        sorted_pop = [x for _, x in sorted(zip(fitnesses, population), key=lambda p: p[0], reverse=True)]
        new_population = sorted_pop[:ELITE_SIZE]

        # 선택 & 교차 & 돌연변이
        selected = selection(population, fitnesses)
        while len(new_population) < POP_SIZE:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2)
            new_population.append(mutate(c1))
            if len(new_population) < POP_SIZE:
                new_population.append(mutate(c2))

        population = new_population

    fitnesses = [fitness(ind) for ind in population]
    best_ind = population[fitnesses.index(max(fitnesses))]
    print(f"\n[주의]  {GENERATIONS}세대 내 완전한 해답을 찾지 못했습니다.")
    return best_ind, GENERATIONS


# ============================================================
# 메인 실행
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("   식인종-선교사 문제 | 유전자 알고리즘으로 해결")
    print("=" * 60)
    print(f"초기 상태: 왼쪽(선교사 3, 식인종 3) / 배: 왼쪽\n")

    best, generation = genetic_algorithm()

    print("\n" + "=" * 60)
    print("   최적 염색체(Command 순서)")
    print("=" * 60)
    print("염색체:", best)
    print("커맨드:", [COMMAND_NAMES[g] for g in best])

    print("\n" + "=" * 60)
    print("   게임 실행 화면")
    print("=" * 60)

    result, history = run_chromosome(best)
    status = Status()
    print(f"초기   | {status}")

    prev_command = None
    step = 0
    temp_status = Status()
    visited = set()
    visited.add(temp_status.to_tuple())

    for gene in best:
        if gene == prev_command:
            continue
        next_status = game(temp_status, gene)
        if next_status is None:
            continue
        if next_status.to_tuple() in visited:
            continue
        visited.add(next_status.to_tuple())
        r = judge(next_status)
        step += 1
        direction = "→ 오른쪽" if temp_status.boat == 'left' else "← 왼쪽"
        print(f"스텝{step:2d} | {direction} [{COMMAND_NAMES[gene]}] → {next_status}")
        temp_status = next_status
        prev_command = gene
        if r in ('win', 'gameover'):
            break

    print(f"\n결과: {' 게임 승리!' if result == 'win' else ' 게임 오버' if result == 'gameover' else '미완료'}")