BLTouch Probe Testing Utility for Raspberry Pi Pico (MicroPython)

A comprehensive testing script for BLTouch 3D printer auto - leveling sensors, specifically designed for Raspberry Pi Pico running MicroPython.

Key Features:
- Interactive menu system for easy test execution
- Supports all essential BLTouch functions: deploy, stow, self-test, alarm release
- Trigger detection with interrupt-based counting
- PWM signal generation compliant with BLTouch specifications
- Real-time status reporting and error detection

Hardware Requirements:
- Raspberry Pi Pico (or compatible RP2040 board)
- BLTouch v3.0+/Smart v3.1 sensor
- Minimum 3杜邦线 for connections

Pin Configuration:
- PWM Control Signal: GP0
- Trigger Detection: GP1 (with internal pull-up)

This utility helps diagnose BLTouch sensor issues, verify wiring correctness, and ensure proper operation before integrating with 3D printer firmware.

树莓派Pico BLTouch探针测试工具 (MicroPython)

一个专为树莓派Pico开发的BLTouch 3D打印机自动调平传感器测试脚本，基于MicroPython平台。

核心功能：
- 交互式菜单系统，便于执行各项测试
- 支持BLTouch全部基本功能：伸出、收回、自检、报警解除
- 基于中断的触发计数检测
- 符合BLTouch规范的PWM信号生成
- 实时状态报告和错误检测

硬件要求：
- 树莓派Pico (或兼容的RP2040开发板)
- BLTouch v3.0+/Smart v3.1传感器
- 至少3根杜邦线用于连接

引脚配置：
- PWM控制信号：GP0
- 触发检测信号：GP1 (带内部上拉电阻)

该工具可帮助诊断BLTouch传感器故障、验证接线正确性，并在集成到3D打印机固件前确保设备正常工作。
