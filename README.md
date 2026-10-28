<div align="center">

# Linglong Robot Toolkit

### 灵龙机器人 · 离线规划与反馈检查工具

Offline trajectory planning & fail-closed feedback validation

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Mode](https://img.shields.io/badge/Mode-Offline_Only-0F766E?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-64748B?style=flat-square)

[快速开始](#快速开始) · [功能与结构](#功能与结构) · [公开范围](#公开范围) · [English](#english)

</div>

---

这是围绕灵龙机器人控制实践整理的独立开源工具层，提供位置参考轨迹生成、关节反馈检查和合成数据演示，便于学习、测试与扩展。Python 标准库即可运行。

代码不建立网络连接、不调用硬件，也不包含实机通信适配器。示例中的坐标、关节值与阈值均为任意合成值，不能作为实机配置。

## 快速开始

需要 Python 3.9 或更新版本，无需安装第三方依赖。从仓库根目录执行：

```bash
python3 -m linglong_toolkit
python3 -m unittest discover -s tests -v
```

演示输出 JSON：一组有效反馈、一组过期反馈，以及五个位置参考采样点。所有计算都在本机内存中完成。

## 功能与结构

| 模块 | 功能 |
| --- | --- |
| [`planning.py`](linglong_toolkit/planning.py) | 三维位置的三次 smoothstep 插值；检查有限数值、采样数量和时长 |
| [`safety.py`](linglong_toolkit/safety.py) | 检查反馈年龄、关节跟踪误差及可选的启动基线漂移；输入缺失或无效时拒绝 |
| [`__main__.py`](linglong_toolkit/__main__.py) | 合成数据的离线演示 |
| [`tests/`](tests/) | 端点、时间顺序、过期反馈、非有限数值、形状错误和阈值测试 |

```text
合成起点 / 终点 ──→ smoothstep ──→ 位置参考采样

关节实测值 / 期望值 / 数据年龄
                 ↓
    有限数值 → 新鲜度 → 跟踪误差 → 基线漂移
                 ↓
         通过或拒绝 + 原因
```

使用示例：

```python
from linglong_toolkit import Feedback, GuardLimits, check_feedback, plan_translation

points = plan_translation((0, 0, 0), (0.01, 0, 0), duration_s=2, samples=21)
limits = GuardLimits(max_age_s=1, max_tracking_error=0.08, max_baseline_drift=0.03)
decision = check_feedback(Feedback((0.01, 0.02), (0.01, 0.02), age_s=0.1), limits)
print(decision.allowed, decision.reasons)
```

误差阈值必须与调用者输入的关节单位一致。数据年龄应由调用者通过可信的本机单调时钟计算，不能直接信任远端提供的年龄。

## 使用边界

位置插值不包含姿态规划、逆运动学、碰撞检测、关节限位或执行器控制，也不保证加速度连续。反馈检查通过仅表示传入数据满足配置的检查条件，不代表机械臂可以安全运动。

本仓库未进行实机验证，不提供一键驱动机器人的命令；实际部署还需要独立的设备适配、风险评估与现场确认。这里也不重新分发厂商 SDK 或宣称与厂商存在官方关联。

## 公开范围

| 公开内容 | 留在私有工作区的内容 |
| --- | --- |
| 独立编写的通用计算与反馈检查代码 | 现场地址、账户、主机路径与设备标识 |
| 任意合成值与离线示例 | 原始日志、抓包、照片和运行记录 |
| 单元测试、说明与 MIT 许可证 | 厂商源码、SDK、设备协议与通信适配器 |

本仓库采用独立 Git 历史，仅纳入本目录列出的公开文件。MIT 许可只适用于本仓库代码与文档，不授予任何第三方软件或设备的权利。

## English

An independent, offline companion toolkit developed around Linglong robot control work. It contains position-only smoothstep interpolation, fail-closed feedback checks, a synthetic JSON demo, and standard-library unit tests.

Run `python3 -m linglong_toolkit` for the demo and `python3 -m unittest discover -s tests -v` for tests. Python 3.9+ is required; no third-party packages are needed.

The public implementation has no network or hardware transport. It excludes deployment settings, identifiers, captures, operational records, vendor code and device protocols. Demo values are synthetic. It does not perform IK, collision checking, orientation planning or actuator control, and a successful feedback check is not authorization to move hardware. This public version has not been validated on a physical robot.

Licensed under [MIT](LICENSE).
