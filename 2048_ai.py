import pygame
import numpy as np
import cv2
import time
import win32gui
import win32ui
import win32con
import win32com.client
import tensorflow as tf
from collections import deque
import random
import pyautogui
import pytesseract

# 定義遊戲狀態處理函數
def preprocess_state(state):
    # 將捕獲的遊戲畫面轉換為適合模型輸入的格式
    # 這裡需要根據實際情況進行調整
    processed_state = cv2.resize(state, (84, 84))
    processed_state = cv2.cvtColor(processed_state, cv2.COLOR_BGR2GRAY)
    return np.reshape(processed_state, [1, 84, 84, 1])

# 定義深度Q網絡模型
def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, (8, 8), strides=(4, 4), activation='relu', input_shape=(84, 84, 1)),
        tf.keras.layers.Conv2D(64, (4, 4), strides=(2, 2), activation='relu'),
        tf.keras.layers.Conv2D(64, (3, 3), strides=(1, 1), activation='relu'),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dense(4, activation='linear')  # 4個輸出對應上下左右四個動作
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mse')
    return model

# 定義經驗回放緩衝區
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.model = create_model()
        self.target_model = create_model()
        self.target_model.set_weights(self.model.get_weights())
        self.replay_buffer = ReplayBuffer(10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 32

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        q_values = self.model.predict(state)
        return np.argmax(q_values[0])

    def train(self):
        if len(self.replay_buffer.buffer) < self.batch_size:
            return
        
        batch = self.replay_buffer.sample(self.batch_size)
        states = np.array([i[0] for i in batch])
        actions = np.array([i[1] for i in batch])
        rewards = np.array([i[2] for i in batch])
        next_states = np.array([i[3] for i in batch])
        dones = np.array([i[4] for i in batch])

        states = np.squeeze(states)
        next_states = np.squeeze(next_states)

        targets = self.model.predict(states)
        next_q_values = self.target_model.predict(next_states)

        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.amax(next_q_values[i])

        self.model.fit(states, targets, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())
        
def get_window_handle(window_title):
    """獲取指定標題的視窗句柄"""
    return win32gui.FindWindow(None, window_title)

def capture_window(hwnd):
    """捕捉指定句柄的視窗內容"""
    # 獲取視窗的尺寸
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # 創建設備上下文（DC）
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 創建位圖對象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 複製視窗內容到位圖
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # 轉換位圖為 numpy array
    signedIntsArray = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(signedIntsArray, dtype='uint8')
    img.shape = (height, width, 4)

    # 清理資源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    # 轉換為 BGR 格式
    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
def get_score_from_state(state):
    # 假設分數在遊戲畫面的右上角
    # 這些值需要根據實際遊戲窗口進行調整
    score_region = state[10:50, -150:-10]  # 調整這些值以準確定位分數區域
    
    # 轉換為灰度圖像
    gray = cv2.cvtColor(score_region, cv2.COLOR_BGR2GRAY)
    
    # 二值化處理
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # 使用Tesseract OCR識別文字
    text = pytesseract.image_to_string(binary, config='--psm 7 -c tessedit_char_whitelist=0123456789')
    
    # 提取數字
    score = ''.join(filter(str.isdigit, text))
    
    # 轉換為整數
    try:
        return int(score)
    except ValueError:
        print("無法識別分數,返回0")
        return 0

def execute_action(action):
    """執行動作並返回下一個狀態、獎勵和是否結束"""
    global hwnd, previos_state, previous_score # 使用全局變量

    # 確保2048遊戲窗口處於活動狀態
    win32gui.SetForegroundWindow(hwnd)
    
    # 根據action執行相應的按鍵操作
    if action == 0:  # 上
        pyautogui.press('up')
    elif action == 1:  # 下
        pyautogui.press('down')
    elif action == 2:  # 左
        pyautogui.press('left')
    elif action == 3:  # 右
        pyautogui.press('right')

    # 等待遊戲響應
    time.sleep(0.1)

        # 捕獲新的遊戲狀態
    next_state = capture_window(hwnd)
    
    # 獲取當前分數（這需要你實現一個函數來從遊戲畫面中提取分數）
    current_score = get_score_from_state(next_state)

    # 計算獎勵
    reward = calculate_reward(next_state, previous_state, previous_score, current_score)

    # 判斷遊戲是否結束
    done = is_game_over(next_state)
    
    # 如果遊戲結束，給予額外的負面獎勵
    if done:
        reward -= 100

    # 更新前一個狀態和分數
    previous_state = next_state
    previous_score = current_score

    return next_state, reward, done

def calculate_reward(current_state, previous_state, previous_score, current_score):
    reward = 0
    
    # 分數增加獎勵
    score_increase = current_score - previous_score
    reward += score_increase * 0.1  # 可以調整係數
    
    # 最大數字獎勵
    current_max = np.max(current_state)
    previous_max = np.max(previous_state)
    if current_max > previous_max:
        reward += 50 * np.log2(current_max)  # 對數獎勵，避免獎勵過大
    
    # 空格數量獎勵
    current_empty = np.count_nonzero(current_state == 0)
    previous_empty = np.count_nonzero(previous_state == 0)
    reward += (current_empty - previous_empty) * 5
    
    # 合併獎勵（這需要更複雜的邏輯來檢測合併，這裡用一個簡化版本）
    if np.sum(current_state) > np.sum(previous_state):
        reward += 10
    
    # 無效移動懲罰
    if np.array_equal(current_state, previous_state):
        reward -= 5
    
    return reward

def is_game_over(state):
    # 檢查是否還有空格
    if 0 in state:
        return False
    
    # 檢查水平和垂直方向是否還有可以合併的相鄰數字
    for i in range(4):
        for j in range(3):
            if state[i][j] == state[i][j+1] or state[j][i] == state[j+1][i]:
                return False
    
    return True  # 如果沒有空格且沒有可合併的數字，遊戲結束

def train_model():
    global hwnd  # 使用全局變量
    agent = DQNAgent(state_size=(84, 84, 1), action_size=4)
    episodes = 1000
    
    for episode in range(episodes):
        state = preprocess_state(capture_window(hwnd))
        total_reward = 0
        done = False
        
        while not done:
            action = agent.act(state)
            next_state, reward, done = execute_action(action)
            next_state = preprocess_state(next_state)
            
            agent.replay_buffer.add(state, action, reward, next_state, done)
            state = next_state
            total_reward += reward
            
            agent.train()
        
        if episode % 10 == 0:
            agent.update_target_model()
        
        print(f"Episode: {episode}, Total Reward: {total_reward}, Epsilon: {agent.epsilon}")

def main():
    global hwnd  # 聲明全局變量
    
    # 啟動 2048.py
    import subprocess
    subprocess.Popen(['python', '2048.py'])
    
    # 等待遊戲視窗出現
    time.sleep(2)
    
    # 尋找視窗句柄 (視窗標題可能需要調整)
    hwnd = get_window_handle('2048')
    if not hwnd:
        print("找不到2048視窗！")
        return

    # 將2048遊戲窗口置於前台
    win32gui.SetForegroundWindow(hwnd)

    # 開始訓練模型
    train_model()


# if __name__ == "__main__":
#     main()
    
if __name__ == "__main__":
    # 載入一個測試圖像
    test_image = cv2.imread('test_2048_screenshot.png')
    score = get_score_from_state(test_image)
    print(f"識別的分數: {score}")