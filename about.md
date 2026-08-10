---
friend_address:
  - name: Facetory
    url: https://github.com/AstralSightStudios/Facetory
    desc: 移动端表盘编辑工具，本站驱动主要用于在此导入使用
  - name: Drific
    url: https://github.com/Drific
    desc: Mesa 源码 workflow 构建实践，PanVK 编译贡献者
  - name: Banners-Turnip
    url: https://github.com/The412Banner/Banners-Turnip
    desc: Adreno Turnip 驱动社区构建源
  - name: Mesa 3D
    url: https://www.mesa3d.org/
    desc: 开源 3D 图形库，Turnip / Freedreno / Panfrost 上游
  - name: VulkanCapsViewer
    url: https://vulkan.gpuinfo.org/download.php
    desc: 查看设备 Vulkan 能力、扩展与限制
---

# VK Driver For Facetory

## 这是什么？

一个 Vulkan 驱动下载站，收集各平台 Turnip / Freedreno / Panfrost 等 Mesa Vulkan 驱动。

本项目旨用于收集并分享可以用于设备 GPU VK 版本不支持、不完整及不适配的设备能够使用 Facetory 进行表盘编辑。

因为市面上的驱动版本极多且资料复杂，故这个项目花了我们不少精力，给个免费的 Star 支持一下🌟

## 叠甲

本项目中所分享的驱动并非全部经过测试，故部分驱动对部分设备可能出现：

- 驱动不兼容设备 GPU
- 驱动无法在本设备正常工作
- 驱动无法安装
- 驱动安装后应用闪退
- 驱动安装后设备受影响
- 驱动安装后设备无法正常工作

故请擦亮眼睛，别下错驱动后找我叭叭。

## 本项目中支持的 GPU

| 分类 | GPU | 代表设备 |
|------|-----|---------|
| Adreno | Adreno 6xx / 7xx / 8xx | 骁龙 8 Elite / 8 Gen 3 / 8 Gen 2 |
| Mali (天玑) | Mali-Gxx | 天玑 9000 / 9300 / 9400 |
| Xclipse (三星) | AMD RDNA | Exynos 2200 / 2400 |
| Mali (Tensor) | Mali-Gxx | Pixel 6 / 7 / 8 / 9 |
| Mali (麒麟/其他) | Mali-Gxx | 麒麟 9000 / 9020 |
| PowerVR（不受支持） | PowerVR | 虎贲 / 部分入门芯片 |

## Facetory 中所适配的移动端 GPU

- Qualcomm Snapdragon 865 或更高
- MediaTek Dimensity 1000 或更高
- Google Tensor G2 或更高
- Samsung Exynos 990 或更高
- HUAWEI Kirin 9000 或更高

详见 [Facetory 仓库说明](https://github.com/AstralSightStudios/Facetory)

> **TIP**  
> 当前部分上游仓库未完全开放，请耐心等候。

## 驱动说明

- **Turnip** — 高通 Adreno 开源 Vulkan 驱动（Mesa Freedreno 项目）
- **libvulkan_freedreno** — Freedreno 官方 Vulkan 驱动
- **libvulkan_panfrost** — ARM Mali 开源 Vulkan 驱动（Mesa Panfrost 项目）

## 使用方法

1. 确认设备 GPU 型号
2. 选择对应分类下载 `.so` 文件
3. 导入至 Facetory 以正常使用

## 外部工具

- [VulkanCapsViewer](https://vulkan.gpuinfo.org/download.php) — 查看设备 Vulkan 能力，详见官网
