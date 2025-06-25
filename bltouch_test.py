import machine
import utime

# BLTouch PWM 脉冲宽度定义 (单位: 微秒 µs)
'''
https://www.antclabs.com/bltouch-v3 中表格定义
通过 G 代码控制
# BLTouch – Smart V3.1 指令及对应参数表
| BLTouch Instruction               | Center Of PWM<br>(Available PWM Rage ±20) | G - code                          | x: Servo Pin or No. |
|-----------------------------------|--------------------------------------------|-----------------------------------|---------------------|
| Push - pin Down (deploy)          | 647 μs (10°)                               | Marlin / Duet: M280 Px S10<br>Repetier: M340 Px S647<br>Smoothieware: M280 S3.24 |                     |
| Alarm Release & Touch SW Mode(M119) | 1162 μs (60°)                              | Marlin / Duet: M280 Px S60<br>Repetier: M340 Px S1162<br>Smoothieware: M280 S5.81 |                     |
| Push - pin Up (Stow)              | 1473 μs (90°)                              | Marlin / Duet: M280 Px S90<br>Repetier: M340 Px S1473<br>Smoothieware: M280 S7.36 |                     |
| Self - test (10 Times)            | 1782 μs (120°)                             | Marlin / Duet: M280 Px S120<br>Repetier: M340 Px S1782<br>Smoothieware: M280 S8.9 |                     |
| EEPROM Conversion Request         | 1884 μs (130°)                             | Marlin / Duet: M280 Px S130<br>Repetier: M340 Px S1884<br>Smoothieware: M280 S9.42 |                     |
| EEPROM:5V Logic Zmin<br>(Do not activate on 3.3V logic system) | 1988 μs (140°)                              | Marlin / Duet: M280 Px S140<br>Repetier: M340 Px S1988<br>Smoothieware: M280 S9.94 |                     |
| EEPROM:Logic voltage Free Zmin<br>(Return to default: Open Drain) | 2091 μs (150°)                              | Marlin / Duet: M280 Px S150<br>Repetier: M340 Px S2091<br>Smoothieware: M280 S10.45 |                     |
| Alarm Release & Push - pin UP     | 2194 μs (160°)                             | Marlin / Duet: M280 Px S160<br>Repetier: M340 Px S2194<br>Smoothieware: M280 S10.97 |                     |

### 备注
- ※ Depending on your board, you can need to adjust the PWM range or Duty cycle.
- ※ EEPROM:5V Logic Zmin: Used with 130° when the Z probe input pin on the control board is not pull - up or has an abnormal input circuit.
- ※ see Logic Voltage Conversion 

# BLTouch – Smart V3.1
| BLTouch 指令 | 脉冲宽度调制中心值（可用脉冲宽度调制范围±20） | G 代码 | x：伺服引脚或编号 |
| ---- | ---- | ---- | ---- |
| 探针下压（部署） | 647 微秒（10°） | 马林/杜埃特：M280 Px S10<br>重复器：M340 Px S647<br>平滑固件：M280 S3.24 |  |
| 报警解除及触碰开关模式（M119） | 1162 微秒（60°） | 马林/杜埃特：M280 Px S60<br>重复器：M340 Px S1162<br>平滑固件：M280 S5.81 |  |
| 探针上抬（收起） | 1473 微秒（90°） | 马林/杜埃特：M280 Px S90<br>重复器：M340 Px S1473<br>平滑固件：M280 S7.36 |  |
| 自检（10 次） | 1782 微秒（120°） | 马林/杜埃特：M280 Px S120<br>重复器：M340 Px S1782<br>平滑固件：M280 S8.9 |  |
| EEPROM 转换请求 | 1884 微秒（130°） | 马林/杜埃特：M280 Px S130<br>重复器：M340 Px S1884<br>平滑固件：M280 S9.42 |  |
| EEPROM：5V 逻辑 Z 最小值<br>（请勿在 3.3V 逻辑系统上激活） | 1988 微秒（140°） | 马林/杜埃特：M280 Px S140<br>重复器：M340 Px S1988<br>平滑固件：M280 S9.94 |  |
| EEPROM：逻辑电压自由 Z 最小值<br>（恢复默认：开漏） | 2091 微秒（150°） | 马林/杜埃特：M280 Px S150<br>重复器：M340 Px S2091<br>平滑固件：M280 S10.45 |  |
| 报警解除及探针上抬 | 2194 微秒（160°） | 马林/杜埃特：M280 Px S160<br>重复器：M340 Px S2194<br>平滑固件：M280 S10.97 |  |

### 备注
- ※ 根据您的控制板，您可能需要调整脉冲宽度调制范围或占空比。
- ※ EEPROM：5V 逻辑 Z 最小值：当控制板上的 Z 探针输入引脚未上拉或输入电路异常时，配合 130° 使用。 
- ※ 参见逻辑电压转换 
'''

BLTOUCH_DEPLOY_PULSE_US   = 647  # M280 Px S10 探针向下伸出 (部署)
BLTOUCH_ALARM_PULSE_US    = 1162 # M280 Px S60 解除报警并进入触摸开关模式 (对应 Marlin 的 M119 指令)
BLTOUCH_STOW_PULSE_US     = 1473 # M280 Px S90 探针向上收回 (收起)
BLTOUCH_SELFTEST_PULSE_US = 1782 # M280 Px S120 自检 (探针伸缩10次)
BLTOUCH_RESET_PULSE_US    = 2194 # M280 Px S160 解除报警并收回探针

# PWM 频率：50Hz (周期 20ms = 20000us)
PWM_FREQUENCY_HZ = 50
PWM_PERIOD_US = 1_000_000 // PWM_FREQUENCY_HZ # 20000 us

# Pico PWM 最大占空比值 (16位)
# Pico 的 PWM 计数器默认是 16 位的，范围是 0-65535
PWM_MAX_DUTY = 65535

# BLTouch 控制信号引脚 (橙色/黄色线)
# 假设连接到 GP0，GP0 对应 PWM0A
control_pin = machine.Pin(0)
pwm = machine.PWM(control_pin)
pwm.freq(PWM_FREQUENCY_HZ) # 设置 PWM 频率为 50Hz

# BLTouch 触发信号引脚 (白色线)
# 假设连接到 GP1，配置为输入并启用内部上拉电阻
# FALLING 表示下降沿触发（当探针触发时，白色线从高阻态被拉低到GND）
trigger_pin = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)

# 全局变量来表示 BLTouch 是否触发
bltouch_triggered = False
# 全局变量来记录触发次数
trigger_count = 0

# 中断回调函数
def bltouch_irq_handler(pin):
    global bltouch_triggered
    global trigger_count
    trigger_count += 1
    if trigger_count<20:
        print(f"BLTouch 触发次数: {trigger_count}")
    # 避免在中断中执行复杂操作，只设置标志
    if not bltouch_triggered: # 避免重复打印
        bltouch_triggered = True
        print("\n*** BLTouch已触发! ***") # 在中断中打印，可以快速看到
        # 注意：在中断中避免进行长时间或复杂的 IO 操作，如 sleep_ms 或过多 print

# 绑定中断
trigger_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=bltouch_irq_handler)

# --- 辅助函数 ---

def set_bltouch_pulse(pulse_us):
    """
    设置 BLTouch PWM 占空比。
    pulse_us: 脉冲宽度，单位微秒 (µs)。
    """
    # 将微秒脉冲宽度转换为 Pico PWM 的 duty_u16 值
    # duty_u16 = (pulse_us / PWM_PERIOD_US) * PWM_MAX_DUTY
    duty_u16 = int((pulse_us / PWM_PERIOD_US) * PWM_MAX_DUTY)
    pwm.duty_u16(duty_u16)
    print(f"设置 PWM 脉宽: {pulse_us} us (占空比: {duty_u16})")

def reset_bltouch():
    """
    M280 Px S160 解除报警并收回探针
    """
    set_bltouch_pulse(BLTOUCH_RESET_PULSE_US) # 发送复位脉冲
    utime.sleep_ms(800) # 等待复位

def send_message(msg):
    """发送消息到串口，MicroPython 默认输出到 REPL (USB CDC)"""
    print(msg)

# --- BLTouch 功能函数 ---

def test_deploy_probe():
    """测试探针伸出功能"""
    global bltouch_triggered
    global trigger_count
    send_message("\n--- 测试功能: 探针伸出 ---")
    reset_bltouch()
    send_message("发送部署探针脉冲 (647us)...")
    set_bltouch_pulse(BLTOUCH_DEPLOY_PULSE_US)
    trigger_count = 0 # 重置触发次数
    bltouch_triggered = False # 重置触发标志
    utime.sleep_ms(500) # 稍等片刻，让探针完全伸出

    send_message("探针已伸出。请手动触摸探针尖端以触发 (5秒超时)...")
    start_time_ms = utime.ticks_ms()
    while not bltouch_triggered and (utime.ticks_diff(utime.ticks_ms(), start_time_ms) < 5000):
        utime.sleep_ms(10)

    if bltouch_triggered:
        send_message("探针触发成功！")
        bltouch_triggered = False
    else:
        send_message("5秒内未检测到探针触发。请检查探针或连接。")
    utime.sleep_ms(1000)
    reset_bltouch()
    set_bltouch_pulse(BLTOUCH_STOW_PULSE_US) # 确保测试后收回探针
    utime.sleep_ms(1000)
    send_message("--- 探针伸出测试结束 ---")

def test_stow_probe():
    """测试探针收回功能"""
    send_message("\n--- 测试功能: 探针收回 ---")
    reset_bltouch()
    send_message("发送收回探针脉冲 (1473us)...")
    set_bltouch_pulse(BLTOUCH_STOW_PULSE_US)
    utime.sleep_ms(4000) # 等待探针收回
    send_message("探针应已收回。")
    send_message("--- 探针收回测试结束 ---")

def test_self_test():
    """测试自检功能"""
    global trigger_count
    trigger_count = 0 # 重置触发次数
    send_message("\n--- 测试功能: 自检 ---")
    reset_bltouch()
    send_message("发送自检脉冲 (1782us)...")
    set_bltouch_pulse(BLTOUCH_SELFTEST_PULSE_US)
    utime.sleep_ms(15000) # 留足时间让它伸缩10次
    send_message("自检已完成。观察探针是否伸缩10次。")
    utime.sleep_ms(1000)
    set_bltouch_pulse(BLTOUCH_RESET_PULSE_US) # 确保测试后收回探针
    utime.sleep_ms(1000)
    send_message("--- 自检测试结束 ---")

def test_alarm_release_touch_sw_mode():
    """测试解除报警并进入触摸开关模式"""
    global bltouch_triggered
    global trigger_count
    send_message("\n--- 测试功能: 解除报警并进入触摸开关模式 ---")
    reset_bltouch()
    send_message("发送解除报警并进入触摸开关模式脉冲 (1162us)...")
    set_bltouch_pulse(BLTOUCH_ALARM_PULSE_US)
    utime.sleep_ms(1000) # 等待进入模式
    send_message("已进入触摸开关模式。请手动触摸探针。如果看到'BLTouch Triggered!'，则表示工作正常。")
    trigger_count = 0 
    bltouch_triggered = False # 重置触发标志
    start_time_ms = utime.ticks_ms()
    while not bltouch_triggered and (utime.ticks_diff(utime.ticks_ms(), start_time_ms) < 5000):
        utime.sleep_ms(10) # 等待手动触发

    if bltouch_triggered:
        send_message("手动触发在触摸开关模式下确认成功！")
        bltouch_triggered = False
    else:
        send_message("5秒内未检测到手动触发。")

    utime.sleep_ms(1000)
    set_bltouch_pulse(BLTOUCH_RESET_PULSE_US) # 确保测试后收回探针
    utime.sleep_ms(1000)
    send_message("--- 解除报警并进入触摸开关模式测试结束 ---")

def test_reset_probe():
    """测试重置和收回探针功能"""
    send_message("\n--- 测试功能: 重置探针 ---")
    send_message("发送解除报警并收回探针脉冲 (2194us)...")
    set_bltouch_pulse(BLTOUCH_RESET_PULSE_US)
    utime.sleep_ms(4000)
    send_message("探针应已收回，且报警已解除（如果之前有报警）。")
    send_message("--- 重置探针测试结束 ---")

def bltouch_full_test_sequence():
    """执行完整的 BLTouch 测试序列"""
    send_message("\n--- BLTouch 完整测试序列开始 ---")
    
    test_reset_probe() # 先重置，确保良好初始状态
    test_deploy_probe()
    test_stow_probe()
    test_self_test()
    test_alarm_release_touch_sw_mode()
    test_reset_probe() # 最终重置

    send_message("--- BLTouch 完整测试序列结束 ---")

# --- 菜单功能 ---

def display_menu():
    """显示测试菜单"""
    send_message("\n--- BLTouch 测试菜单 ---")
    send_message("请选择要执行的功能：")
    send_message("1. 探针伸出 (Deploy Probe)")
    send_message("2. 探针收回 (Stow Probe)")
    send_message("3. 自检 (Self-test)")
    send_message("4. 解除报警并进入触摸开关模式 (Alarm Release & Touch SW Mode)")
    send_message("5. 重置探针 (Reset Probe)")
    send_message("6. 执行完整测试序列 (Full Test Sequence)")
    send_message("0. 退出程序 (Exit)")
    send_message("--------------------------")

def get_user_choice():
    """获取用户输入的选择"""
    while True:
        try:
            choice = input("请输入你的选择 (0-6): ")
            choice = int(choice)
            if 0 <= choice <= 6:
                return choice
            else:
                send_message("输入无效，请输入 0 到 6 之间的数字。")
        except ValueError:
            send_message("输入无效，请输入一个数字。")

# --- 主程序 ---

send_message("BLTouch 测试程序已启动 (MicroPython on Pico)。")
send_message("请确保 BLTouch 已正确连接到 GP0 (PWM) 和 GP1 (触发)。")

# 启动 PWM 到一个初始状态 (例如，收回状态)
set_bltouch_pulse(BLTOUCH_RESET_PULSE_US) # 确保探针初始是收回的
utime.sleep_ms(1000)

while True:
    display_menu()
    choice = get_user_choice()

    if choice == 1:
        test_deploy_probe()
    elif choice == 2:
        test_stow_probe()
    elif choice == 3:
        test_self_test()
    elif choice == 4:
        test_alarm_release_touch_sw_mode()
    elif choice == 5:
        test_reset_probe()
    elif choice == 6:
        bltouch_full_test_sequence()
    elif choice == 0:
        send_message("程序退出。")
        set_bltouch_pulse(BLTOUCH_RESET_PULSE_US) # 退出前确保探针收回
        break # 退出主循环
    
    # send_message("\n测试完成。按回车键继续...")
    # input() # 等待用户按回车键，以便在下次菜单显示前有时间阅读输出
    utime.sleep_ms(500) # 稍作延时，避免菜单显示过快


