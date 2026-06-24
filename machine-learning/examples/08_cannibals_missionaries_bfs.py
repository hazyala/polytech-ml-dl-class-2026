"""Breadth-first search starter for the cannibals and missionaries problem."""

from collections import deque
from dataclasses import dataclass


MOVES = [
    (1, 0, "one missionary"),
    (2, 0, "two missionaries"),
    (0, 1, "one cannibal"),
    (0, 2, "two cannibals"),
    (1, 1, "one missionary and one cannibal"),
]


@dataclass(frozen=True)
class State:
    left_m: int = 3
    left_c: int = 3
    boat_left: bool = True

    @property
    def right_m(self) -> int:
        return 3 - self.left_m

    @property
    def right_c(self) -> int:
        return 3 - self.left_c

    def is_valid(self) -> bool:
        if not (0 <= self.left_m <= 3 and 0 <= self.left_c <= 3):
            return False
        left_safe = self.left_m == 0 or self.left_m >= self.left_c
        right_safe = self.right_m == 0 or self.right_m >= self.right_c
        return left_safe and right_safe

    def is_goal(self) -> bool:
        return self.left_m == 0 and self.left_c == 0 and not self.boat_left

    def move(self, missionaries: int, cannibals: int) -> "State | None":
        direction = -1 if self.boat_left else 1
        next_state = State(
            self.left_m + direction * missionaries,
            self.left_c + direction * cannibals,
            not self.boat_left,
        )
        return next_state if next_state.is_valid() else None


def solve() -> list[tuple[str, State]]:
    start = State()
    queue = deque([(start, [])])
    visited = {start}

    while queue:
        state, path = queue.popleft()
        if state.is_goal():
            return path
        for missionaries, cannibals, label in MOVES:
            next_state = state.move(missionaries, cannibals)
            if next_state and next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [(label, next_state)]))
    return []


def main() -> None:
    for step, (move_label, state) in enumerate(solve(), start=1):
        boat = "left" if state.boat_left else "right"
        print(
            f"{step:02d}. move {move_label:<28} "
            f"left=({state.left_m}M,{state.left_c}C) "
            f"right=({state.right_m}M,{state.right_c}C) boat={boat}"
        )


if __name__ == "__main__":
    main()

