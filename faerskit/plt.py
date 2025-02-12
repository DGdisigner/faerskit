import scipy
from sklearn.metrics import roc_curve, auc, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 绘制 ROC 曲线
def plot_roc(y_true, y_pred_proba, fname):
    # 计算 ROC 曲线
    fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)
    # 计算 AUC 值
    roc_auc = auc(fpr, tpr)
    # 绘制 ROC 曲线
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig(fname, bbox_inches='tight', pad_inches=0.1)


# 定义 DCA 函数
def calculate_net_benefit(y_label, y_pred_prob, thresholds):
    net_benefit_model = np.array([])
    for thresh in thresholds:
        y_pred_label = y_pred_prob > thresh
        tn, fp, fn, tp = confusion_matrix(y_label, y_pred_label).ravel()
        n = len(y_label)
        net_benefit = (tp / n) - (fp / n) * (thresh / (1 - thresh))
        net_benefit_model = np.append(net_benefit_model, net_benefit)
    return net_benefit_model


def calculate_net_benefit_all(y_label, thresholds):
    net_benefit_all = np.array([])
    tn, fp, fn, tp = confusion_matrix(y_label, y_label).ravel()
    total = tp + tn
    for thresh in thresholds:
        net_benefit = (tp / total) - (tn / total) * (thresh / (1 - thresh))
        net_benefit_all = np.append(net_benefit_all, net_benefit)
    return net_benefit_all


def plot_dca(y_true, y_pred_prob, fname):
    # 定义阈值范围
    thresholds = np.arange(0, 1, 0.01)
    # 计算净收益
    net_benefits_model = calculate_net_benefit(y_true, y_pred_prob, thresholds)
    net_benefits_treat_all = calculate_net_benefit_all(y_true, thresholds)
    net_benefits_treat_none = np.zeros_like(thresholds)
    # 绘制 DCA 曲线
    fig, ax = plt.subplots()
    ax.plot(thresholds, net_benefits_model, label='Model', color='blue')
    ax.plot(thresholds, net_benefits_treat_all, label='Treat All', color='red', linestyle='--')
    ax.plot(thresholds, net_benefits_treat_none, label='Treat None', color='green', linestyle='--')

    # Fill，显示出模型较于treat all和treat none好的部分
    y2 = np.maximum(net_benefits_treat_all, 0)
    y1 = np.maximum(net_benefits_model, y2)
    ax.fill_between(thresholds, y1, y2, color='crimson', alpha=0.2)
    ax.set_xlim(0, 1)
    ax.set_ylim(net_benefits_model.min() - 0.15, net_benefits_model.max() + 0.15)  # adjustify the y axis limitation
    ax.set_xlabel(
        xlabel='Threshold Probability',
        fontdict={'family': 'Times New Roman', 'fontsize': 15}
    )
    ax.set_ylabel(
        ylabel='Net Benefit',
        fontdict={'family': 'Times New Roman', 'fontsize': 15}
    )
    ax.grid('major')
    ax.spines['right'].set_color((0.8, 0.8, 0.8))
    ax.spines['top'].set_color((0.8, 0.8, 0.8))
    ax.legend(loc='upper right')
    plt.savefig(fname, bbox_inches='tight', pad_inches=0.1)


def plot_calibration(y_true, y_pred_prob, n, fname):
    """
    参数说明：
    true: 实际标签值
    pred: 模型输出的预测概率
    n: 分组数目 (校准区间中有几个点)
        先加工绘图需要的数据形式：df_cal_trans
        然后绘图，可以选择是否带误差棒
    """
    df_cal = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred_prob})  # 现将实际值和预测值拼接成一个dataframe
    df_cal = df_cal.sort_values(by='y_pred')  ## 根据预测概率值进行排序
    df_cal['group'], cut_bin = pd.qcut(df_cal['y_pred'], q=n, retbins=True, labels=list(range(1, n + 1)), duplicates='drop')  ## 将数据进行分箱
    output_list = list()
    for i in range(1, n + 1):
        counts = df_cal.loc[df_cal['group'] == i, 'y_true'].value_counts(1)
        if 0 in counts.index:
            true_pos_rate = 1 - counts[0]
        else:
            true_pos_rate = 1
        y_pred_mean = df_cal.loc[df_cal['group'] == i, 'y_pred'].mean()
        y_pred_sd = df_cal.loc[df_cal['group'] == i, 'y_pred'].std()
        output = {'group': i, 'true_pos_rate': true_pos_rate, 'y_pred_mean': y_pred_mean, 'y_pred_sd': y_pred_sd}
        output_list.append(output)
    df_cal_trans = pd.DataFrame(output_list)
    calibration_slop = round(scipy.stats.linregress(df_cal_trans['y_pred_mean'], df_cal_trans['true_pos_rate']).slope
                             , 3)

    plt.figure(figsize=(6, 4))
    plt.rcParams['axes.spines.right'] = False  # 不绘制右边的框线
    plt.rcParams['axes.spines.top'] = False  # 不绘制上方的框线
    line = plt.errorbar(df_cal_trans['y_pred_mean'], df_cal_trans['true_pos_rate'],
                        fmt='--o',  # 数据点标记式样和数据点标记的连线式样
                        ecolor="#00688B",  # 误差棒的颜色
                        elinewidth=0.8,  # 误差棒线条粗细
                        ms=4,  # 数据点大小
                        mfc="#00688B",  # 数据点颜色
                        capthick=1,  # 误差棒边界横线的厚度
                        capsize=2  # 误差棒边界横线的大小
                        )
    limits = round(max(df_cal_trans['true_pos_rate'].max(), df_cal_trans['y_pred_mean'].max()) + 0.02, 3)
    plt.plot([0, limits], [0, limits], "--", lw=1, color="grey")
    plt.xlim(0, limits)
    plt.ylim(0, limits)
    plt.xlabel('Predicted event probability', fontsize=10)
    plt.ylabel('Observed event probability', fontsize=10)
    # plt.legend(handles=[line],labels=['HL P-value: > 0.05'], loc='best')
    plt.legend(handles=[line], labels=['Calibration slope: {}'.format(calibration_slop)], loc='best')  # 'lower right'
    plt.grid(axis="y")  # 设置横向网格线
    plt.savefig(fname, bbox_inches='tight', pad_inches=0.1)
