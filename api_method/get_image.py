# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import math
from uuid import uuid4
from io import BytesIO
from matplotlib.ticker import MaxNLocator

def plot_rating_score(data, name="小诗乃", show=False):
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    ids = list(data.keys())
    ratings = [data[k]["rating"] for k in ids]
    scores = [data[k]["score"] for k in ids]

    x = np.arange(1, len(ids) + 1)
    cum_score = np.cumsum(scores)

    avg_rating = sum(ratings) / len(ratings)

    y_min = math.floor(min(ratings) / 5) * 5 if min(ratings) < 60 else 60
    y_max = 100

    # =========================
    # Figure
    # =========================
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(14, 8),
        sharex=True,
        gridspec_kw={"height_ratios": [1, 1.3]}
    )

    # =========================
    # ⭐ Rating
    # =========================
    ax1.plot(x, ratings, marker="o", color="#1f77b4", linewidth=2)
    ax1.fill_between(x, ratings, alpha=0.08, color="#1f77b4")

    for i, v in enumerate(ratings):
        up = i == 0 or v >= ratings[i - 1]

        ax1.text(
            x[i] - 0.15,  # ⭐ 关键修复点（只改这里）
            v + (0.25 if up else -0.25),
            f"{v:.2f}",
            ha="right",
            va="bottom" if up else "top",
            fontsize=6,
            color="#1f77b4",
            alpha=0.9
        )

    ax1.axhline(avg_rating, linestyle="--", alpha=0.7, color="#ff7f0e")

    ax1.text(
        len(ids) + 0.2, avg_rating - 1.0,
        f"AVG {avg_rating:.2f}",
        ha="left",
        va="center",
        fontsize=9,
        color="#ff7f0e"
    )

    ax1.set_ylabel("Rating")
    ax1.set_ylim(y_min, y_max)
    ax1.set_title(f"{name}的motral4.1 Rating  均值:{avg_rating:.2f}", fontsize=12)
    ax1.grid(alpha=0.2)

    # =========================
    # ⭐ PT
    # =========================
    colors = np.where(np.array(scores) >= 0, "#2ca02c", "#d62728")

    bars = ax2.bar(x, scores, color=colors, alpha=0.35)
    for bar, score in zip(bars, scores):
        height = bar.get_height()

        if height >= 0:
            # 正数：显示在柱子顶部上方
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height + 2,
                str(score),
                ha="center",
                va="bottom",
                fontsize=4,
            )
        else:
            # 负数：显示在柱子底部下方
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height - 2,
                str(score),
                ha="center",
                va="top",
                fontsize=4,
            )
    ax2.plot(x, cum_score, color="#6a5acd", linewidth=2)

    ax2.axhline(0, color="gray", linewidth=1)

    # for i, v in enumerate(cum_score):
    #     ax2.text(
    #         i,
    #         v + (5 if v >= 0 else -5),
    #         f"{v:.0f}",
    #         ha="center",
    #         fontsize=6,
    #         color="black",
    #         alpha=0.85
    #     )

    if len(cum_score):
        ax2.text(
            len(cum_score),
            cum_score[-1] + (5 if cum_score[-1] >= 0 else -5),
            f"{cum_score[-1]:.0f}",
            ha="center",
            fontsize=6,
            color="black",
            alpha=0.85
        )

    ax2.set_ylabel("PT")
    ax2.set_title(f"{name}的近期PT点 获取趋势", fontsize=12)
    ax2.grid(alpha=0.2)

    # =========================
    # X axis
    # =========================
    # x_labels = [f"{i+1}" for i in range(len(ids))]
    x = np.arange(1, len(ids) + 1)
    ax2.set_xlim(0.5, len(ids) + 0.5)
    ax2.xaxis.set_major_locator(MaxNLocator(nbins=15, integer=True))

    # plt.xlim(-0.5, len(ids) + 0.8)
    plt.tight_layout()


    buf = BytesIO()

    plt.savefig(
        buf,
        format="png",
        dpi=150,
        bbox_inches="tight"
    )
    buf.seek(0)
    if show:
        plt.show()
    image_bytes = buf.getvalue()

    plt.close(fig)

    return image_bytes

if __name__ == '__main__':
    data = {"260623-01700ed5-e647-4bf6-9008-c22cbade8688_a111674862": {"rating": 85.91, "score": 67}, "260623-95d95407-67be-4175-8d95-a83da29fb2f3_a111674862": {"rating": 88.03, "score": -214}, "260623-65b952cd-1cae-49f2-9256-1b6aee0bb6a3_a111674862": {"rating": 78.2, "score": -221}, "260624-ec775e27-917c-4211-8d38-54969384521c_a111674862": {"rating": 81.97, "score": 62}, "260624-2155f811-f2f7-4471-9523-4b6be1550313_a111674862": {"rating": 87.37, "score": 132}, "260624-001d84a3-d36c-404f-9e8b-f2df29e96108_a111674862": {"rating": 85.29, "score": -218}, "260624-748c2ae2-fd1b-4761-8a1d-07ca733e9851_a111674862": {"rating": 86.25, "score": 134}, "260624-a51a25d1-f446-4a11-8788-7bcd9e319a9c_a111674862": {"rating": 81.55, "score": -8}, "260624-049d7aa5-ec77-48ab-8db9-8e998fb62a15_a111674862": {"rating": 82.85, "score": -9}, "260625-7566c29b-fb8a-4810-b64d-59ab2882eca1_a111674862": {"rating": 85.43, "score": 63}, "260625-942a35a9-61b5-4b0b-9e3e-20e832c2cd67_a111674862": {"rating": 84.4, "score": 59}, "260625-a2e80515-a9ff-484f-9341-ae7f8f7fea3a_a111674862": {"rating": 87.0, "score": 70}, "260625-9f85f24d-eb2c-4c39-8016-36057a6bbd7d_a111674862": {"rating": 83.59, "score": -13}, "260625-5f31e208-e604-4a03-a72d-610d51ca43e8_a111674862": {"rating": 86.15, "score": 135}, "260625-2bcc6c2b-0d5c-4869-a3fa-37f1233ba34e_a111674862": {"rating": 87.55, "score": -208}, "260625-e2f48a99-096c-42f0-8f09-ac3f4872ea0a_a111674862": {"rating": 81.06, "score": 144}, "260625-a1ddbd7b-ed66-4632-9ad7-7d6851c739f3_a111674862": {"rating": 76.51, "score": 57}, "260625-45aa759d-f93c-4f4a-b576-6a45ec4fa2ba_a111674862": {"rating": 80.37, "score": -17}, "260625-fa7f9ae3-3168-45d2-bdc5-fe5df882a7c1_a111674862": {"rating": 87.74, "score": 66}, "260625-a1a54be9-3717-4a10-ba42-ae990afcacec_a111674862": {"rating": 91.18, "score": 62}}
    image_bytes = plot_rating_score(data, "小诗乃", show=True)
    # with open(f"小诗乃_{uuid4().hex[:8]}.png", "wb") as f:
    #     f.write(image_bytes)