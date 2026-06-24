# =============================================
# game_engine.py
# 식인종-선교사 게임 엔진
# PPT(07식인종선교사 프로그래밍.pdf) 구조 그대로 구현
# 상태(Status) → 커맨드(Command) → 게임(Game) → 판정(Judge)
# =============================================

# 커맨드 정의 (PPT Command 목록과 동일)
# key: 커맨드 번호, value: (선교사 수, 식인종 수)
COMMANDS = {
    0: (1, 0),  # 선교사 1명
    1: (2, 0),  # 선교사 2명
    2: (0, 1),  # 식인종 1명
    3: (0, 2),  # 식인종 2명
    4: (1, 1),  # 선교사 1명 + 식인종 1명
}

# 화면 표시용 커맨드 이름
COMMAND_NAMES = {
    0: "선교사 1명",
    1: "선교사 2명",
    2: "식인종 1명",
    3: "식인종 2명",
    4: "선교사 1명 + 식인종 1명",
}


class Status:
    """
    게임 상태 클래스 (PPT 상태 정의 그대로)
    왼쪽/오른쪽 선교사 수, 식인종 수, 배 위치 총 5개 값
    """
    def __init__(self, left_m=3, left_c=3, right_m=0, right_c=0, boat="left"):
        self.left_m  = left_m   # 왼쪽 선교사 수
        self.left_c  = left_c   # 왼쪽 식인종 수
        self.right_m = right_m  # 오른쪽 선교사 수
        self.right_c = right_c  # 오른쪽 식인종 수
        self.boat    = boat     # 배 위치 ("left" / "right")

    def clone(self):
        """상태 복사"""
        return Status(self.left_m, self.left_c, self.right_m, self.right_c, self.boat)

    def to_dict(self):
        """JSON 직렬화용"""
        return {
            "left_m":  self.left_m,
            "left_c":  self.left_c,
            "right_m": self.right_m,
            "right_c": self.right_c,
            "boat":    self.boat,
        }

    def to_tuple(self):
        """방문 상태 중복 체크용 튜플"""
        return (self.left_m, self.left_c, self.right_m, self.right_c, self.boat)


def get_valid_commands(status):
    """
    현재 상태에서 실행 가능한 커맨드 번호 목록 반환
    PPT 제약조건: 해당 강가 인원이 부족하면 실행 불가
    """
    valid = []
    for cmd_id, (m, c) in COMMANDS.items():
        if status.boat == "left":
            if status.left_m >= m and status.left_c >= c:
                valid.append(cmd_id)
        else:
            if status.right_m >= m and status.right_c >= c:
                valid.append(cmd_id)
    return valid


def get_safe_commands(status, visited=None):
    """
    현재 상태에서 즉시 gameover가 되지 않는 커맨드 목록 반환.
    visited가 주어지면 이미 방문한 상태로 되돌아가는 커맨드는 뒤로 미룬다.
    """
    visited = set(visited or [])
    safe = []
    revisit = []
    for cmd_id in get_valid_commands(status):
        next_status = game(status, cmd_id)
        if next_status is None or judge(next_status) == "gameover":
            continue
        if next_status.to_tuple() in visited:
            revisit.append(cmd_id)
        else:
            safe.append(cmd_id)
    return safe or revisit


def find_solution_command(status, visited=None):
    """
    BFS로 현재 상태에서 승리까지 가는 최단 경로의 첫 커맨드를 찾는다.
    LLM이 잘못 고를 때도 AI 모드가 문제해결 흐름을 유지하도록 하는 안전장치다.
    """
    visited = set(visited or [])
    start = status.to_tuple()
    queue = [(status, [])]
    seen = {start}

    while queue:
        cur, path = queue.pop(0)
        for cmd_id in get_valid_commands(cur):
            next_status = game(cur, cmd_id)
            if next_status is None or judge(next_status) == "gameover":
                continue

            next_key = next_status.to_tuple()
            if next_key in seen:
                continue
            seen.add(next_key)

            next_path = path + [cmd_id]
            if judge(next_status) == "win":
                return next_path[0]

            queue.append((next_status, next_path))

    safe = get_safe_commands(status, visited)
    return safe[0] if safe else None


def game(status, command):
    """
    게임 함수 (PPT 게임 정의 그대로)
    현재 상태 + 커맨드 → 다음 상태 반환
    실행 불가 커맨드면 None 반환
    """
    s = status.clone()
    m, c = COMMANDS[command]

    if s.boat == "left":
        # 왼쪽 → 오른쪽 이동
        if s.left_m < m or s.left_c < c:
            return None
        s.left_m  -= m;  s.left_c  -= c
        s.right_m += m;  s.right_c += c
        s.boat = "right"
    else:
        # 오른쪽 → 왼쪽 이동
        if s.right_m < m or s.right_c < c:
            return None
        s.right_m -= m;  s.right_c -= c
        s.left_m  += m;  s.left_c  += c
        s.boat = "left"

    return s


def judge(status):
    """
    판정 함수 (PPT 판정 정의 그대로)
    선교사 < 식인종 → gameover
    오른쪽 선교사==3, 식인종==3 → win
    그 외 → continue
    """
    if status.left_m > 0 and status.left_m < status.left_c:
        return "gameover"
    if status.right_m > 0 and status.right_m < status.right_c:
        return "gameover"
    if status.right_m == 3 and status.right_c == 3:
        return "win"
    return "continue"
