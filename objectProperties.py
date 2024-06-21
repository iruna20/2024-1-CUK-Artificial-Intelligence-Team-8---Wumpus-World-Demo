# 객체 타입에 따라 색상과 모양을 지정하는 딕셔너리
# 색상: b(파란색), g(초록색), r(빨간색), c(청록색), y(노란색), k(검은색), w(흰색)
# 마커: o(원), v(역삼각형), ^(삼각형), s(네모), +(플러스), .(점)
# 예시 - gv는 초록색 역삼각형
# 더 많은 참고 : https://wikidocs.net/92083#_3

value = {
    'Agent_1': 'b^',
    'Agent_2': 'bv',
    'Agent_3': 'b>',
    'Agent_4': 'b<',
    'Wumpus': 'ro',
    'DeadWumpus': 'go',
    'Stench': 'rx',
    'Pit': 'cs',
    'Breeze': 'c.',
    'Gold': 'y*',
    'Glitter': 'y+',
    '': None    # 빈 칸은 그리지 않음
}

percept_name = ['Stench', 'Breeze', 'Glitter', 'Bump', 'Scream', 'Terminated', 'Reward']