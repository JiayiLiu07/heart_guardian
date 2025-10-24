import matplotlib.pyplot as plt
import seaborn as sns

def apply_custom_style():
    """
    应用统一的图表样式，符合高科技风格，图表标签使用英文

    返回:
        None: 直接修改当前 Matplotlib 图表的样式
    """
    # 设置 Seaborn 主题
    sns.set_style("whitegrid")
    
    # 自定义 Matplotlib 参数
    plt.rcParams.update({
        'font.family': 'Arial',  # 使用 Arial 字体，适合英文标签
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'axes.titleweight': 'bold',
        'axes.labelweight': 'medium',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'grid.color': '#e0e0e0',
        'axes.edgecolor': '#2979ff',  # 边框颜色与主题一致
        'axes.facecolor': 'rgba(255, 255, 255, 0.95)',  # 背景略带透明
        'figure.facecolor': 'rgba(255, 255, 255, 0)',  # 图表背景透明
        'axes.spines.top': False,  # 移除顶部边框
        'axes.spines.right': False,  # 移除右侧边框
        'axes.prop_cycle': plt.cycler(color=['#2979ff', '#00e5ff', '#ff4081', '#1a237e'])  # 主题渐变色
    })
    
    # 添加圆角效果（通过设置 axes 的边框样式）
    for spine in plt.gca().spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('#2979ff')
    
    # 设置网格线样式
    plt.grid(True, linestyle='--', alpha=0.3)