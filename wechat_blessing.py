
import pyautogui
import pygetwindow as gw
import time
import logging
import pyperclip
import random

pyautogui.FAILSAFE = True

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_blessing.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

CONFIG = {
    'name_file': 'name.txt',
    'template_file': 'text.txt',
    'word_file': 'word.txt',
    'preparation_time': 10,
    'search_delay': 1.5,
    'select_contact_delay': 2.5,
    'input_delay': 0.8,
    'send_delay': 1.2,
    'next_person_delay': 2.5,
    'wechat_window_title': '微信'
}


def read_names(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        logger.info('成功读取 %d 个联系人', len(names))
        return names
    except FileNotFoundError:
        logger.error('文件 %s 不存在', file_path)
        raise
    except Exception as e:
        logger.error('读取文件失败: %s', e)
        raise


def read_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        logger.info('成功读取祝福语模板')
        return template
    except FileNotFoundError:
        logger.error('文件 %s 不存在', file_path)
        raise
    except Exception as e:
        logger.error('读取模板文件失败: %s', e)
        raise


def read_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
        logger.info('成功读取 %d 条祝福附加句', len(words))
        return words
    except FileNotFoundError:
        logger.error('文件 %s 不存在', file_path)
        raise
    except Exception as e:
        logger.error('读取祝福附加句文件失败: %s', e)
        raise


def activate_wechat_window():
    try:
        windows = gw.getWindowsWithTitle(CONFIG['wechat_window_title'])
        if not windows:
            logger.error('未找到微信窗口')
            return False
        
        wechat_window = windows[0]
        if wechat_window.isMinimized:
            wechat_window.restore()
        wechat_window.activate()
        time.sleep(1)
        logger.info('微信窗口已激活')
        return True
    except Exception as e:
        logger.error('激活微信窗口失败: %s', e)
        return False


def search_contact(name):
    try:
        activate_wechat_window()
        time.sleep(0.5)
        
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(CONFIG['search_delay'])
        pyperclip.copy(name)
        time.sleep(0.3)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(CONFIG['search_delay'])
        pyautogui.press('enter')
        time.sleep(CONFIG['select_contact_delay'])
        
        activate_wechat_window()
        time.sleep(0.5)
        return True
    except Exception as e:
        logger.error('搜索联系人 %s 失败: %s', name, e)
        return False


def click_input_box():
    try:
        windows = gw.getWindowsWithTitle(CONFIG['wechat_window_title'])
        if windows:
            win = windows[0]
            center_x = win.left + win.width // 2
            click_y = win.bottom - 100
            pyautogui.moveTo(center_x, click_y)
            time.sleep(0.2)
            pyautogui.click()
            time.sleep(0.3)
            return True
    except Exception as e:
        logger.warning('点击输入框失败: %s', e)
    return False


def send_blessing(name, template, words):
    try:
        selected_word = random.choice(words)
        message = template.replace('{name}', name).replace('{word}', selected_word)
        pyperclip.copy(message)
        time.sleep(0.3)
        
        click_input_box()
        
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(CONFIG['input_delay'])
        pyautogui.press('enter')
        time.sleep(CONFIG['send_delay'])
        logger.info('给 %s 发送成功', name)
        return True
    except Exception as e:
        logger.error('给 %s 发送失败: %s', name, e)
        return False


def main():
    try:
        names = read_names(CONFIG['name_file'])
        template = read_template(CONFIG['template_file'])
        words = read_words(CONFIG['word_file'])
        
        logger.info('程序将在 %d 秒后开始，请切换到微信界面', CONFIG['preparation_time'])
        for i in range(CONFIG['preparation_time'], 0, -1):
            print('倒计时: %d 秒' % i, end='\r')
            time.sleep(1)
        print()
        
        if not activate_wechat_window():
            return
        
        success_count = 0
        fail_count = 0
        
        for name in names:
            logger.info('正在给 %s 发送祝福', name)
            
            if search_contact(name):
                if send_blessing(name, template, words):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
            
            time.sleep(CONFIG['next_person_delay'])
        
        logger.info('发送完成！成功: %d, 失败: %d', success_count, fail_count)
        
    except Exception as e:
        logger.error('程序运行出错: %s', e)


if __name__ == '__main__':
    main()

