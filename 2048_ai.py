import pygame
import numpy as np
import cv2
import time
import win32gui
import win32ui
import win32con
import win32com.client

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

def main():
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

    try:
        while True:
            # 捕捉視窗內容
            frame = capture_window(hwnd)
            
            # 顯示捕捉到的畫面
            cv2.imshow('Window Capture', frame)
            
            # 按 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # 控制捕捉頻率
            time.sleep(0.033)  # ~30 FPS

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()