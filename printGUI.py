import os
import shutil
from time import sleep
import matplotlib.pyplot as plt
import objectProperties as op

# 상수 정의
CELL_SIZE = 50  # 셀 크기
GRID_SIZE = 4   # 격자 크기
SAVE_PATH = 'result'  # 저장 경로

# 절대 경로로 변환
SAVE_PATH = os.path.abspath(SAVE_PATH)

# 디렉토리 삭제 후 생성
def reset_directory():
    if os.path.exists(SAVE_PATH):
        shutil.rmtree(SAVE_PATH)
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)

    
# 격자 그리기
def draw_grid():
    fig, ax = plt.subplots()
    for i in range(GRID_SIZE + 1):
        ax.plot([0, GRID_SIZE * CELL_SIZE], [i * CELL_SIZE, i * CELL_SIZE], color='black', linewidth=5)
        ax.plot([i * CELL_SIZE, i * CELL_SIZE], [0, GRID_SIZE * CELL_SIZE], color='black', linewidth=5)
    ax.set_aspect('equal')
    plt.axis('off')
    return fig, ax


# Object 그리기
def draw_object(ax, x, y, object_type):
    marker = ''
    if object_type in op.value and op.value[object_type] is not None:
        marker = op.value[object_type]
    ax.plot(x * CELL_SIZE + CELL_SIZE / 2, y * CELL_SIZE + CELL_SIZE / 2, marker, markersize=20)

# 텍스트 출력
def print_text(ax, x, y, text):
    ax.text(x, y, text, ha='left', va='center', transform=ax.transAxes, fontsize=12, color='black')

# percept 출력
def print_percept(ax, percept_dictionary):
    percept_str = ""
    for name in op.percept_name:
        if name == "Reward":
            continue
        if percept_dictionary[name]:
            name += "!\n"
            percept_str += name
    ax.text(0.66, -0.07, percept_str, ha='left', va='center', transform=ax.transAxes, fontsize=12, color='red')
    
    
def save_img(num, grid, current_action_name, next_action_name, percept_dictionary, is_headless = True):
    fig, ax = draw_grid()
    
    text = f'Process : {num}\nCurrent Action : {current_action_name}\nNext Action : {next_action_name}'
    print_text(ax, 0, -0.06, text)  # 텍스트 추가
    
    print_percept(ax, percept_dictionary)    # percept 추가
    
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            for object_type in grid[y][x] :
                #draw_object(ax, x, GRID_SIZE - 1 - y, object_type)
                draw_object(ax, x, y, object_type)
    
    state_path = os.path.join(SAVE_PATH, f'state_{num}.png')
    plt.savefig(state_path)  # 이미지로 저장
    
    if not is_headless :
        plt.show()
    
    plt.close(fig)
    print(f'{num} 번째 이미지 파일 생성 완료\n')