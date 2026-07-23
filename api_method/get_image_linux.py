# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.ticker import MaxNLocator
from uuid import uuid4
from io import BytesIO

def plot_rating_score(data, name="小诗乃", show=False):
    plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
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
    #         fontsize=8,
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
    if show:
        plt.show()

    buf = BytesIO()

    plt.savefig(
        buf,
        format="png",
        dpi=150,
        bbox_inches="tight"
    )
    buf.seek(0)

    image_bytes = buf.getvalue()

    plt.close(fig)

    return image_bytes

if __name__ == '__main__':
    data = {"260606-f0744a73-7a1f-4374-b2e7-992d8c682f17_a231661664": {"rating": 90.06, "score": 62}, "260606-c6c26ee6-1c50-4556-a7b7-101416d25954_a231661664": {"rating": 94.28, "score": 63}, "260606-83c02f54-b297-4968-9fe8-9597fcd4207c_a231661664": {"rating": 84.01, "score": 168}, "260607-819ccb91-26a7-4ffb-991c-09b8a0469d35_a231661664": {"rating": 93.39, "score": -21}, "260607-4e816371-2f28-4cfd-98ec-ce38e970d02d_a231661664": {"rating": 89.01, "score": 161}, "260607-d2e12e41-b08b-4f6f-96dd-b1d752c14722_a231661664": {"rating": 94.94, "score": -246}, "260607-e9c421a8-5cae-408a-8174-3d7febfb5afb_a231661664": {"rating": 94.78, "score": 62}, "260607-69a98ff5-6075-493d-81e2-add9a885b87b_a231661664": {"rating": 84.81, "score": -16}, "260607-954a0ba9-b5eb-4cd7-a5de-9ab39973e1ea_a231661664": {"rating": 80.11, "score": -8}, "260608-471968a7-e5a1-45c7-b8dd-2edc880a2646_a231661664": {"rating": 97.22, "score": 66}, "260608-d7039638-28cc-411e-8495-a1cbf65ef8d3_a231661664": {"rating": 95.42, "score": 131}, "260608-4d3f7e30-f90a-4ff4-9202-49da3276e3b7_a231661664": {"rating": 91.06, "score": 142}, "260608-9a7d158b-465c-40b3-afbe-eee965b1b01f_a231661664": {"rating": 94.15, "score": 140}, "260608-8eb338b0-6adc-4b03-96b5-856e17bfe2e9_a231661664": {"rating": 93.46, "score": 142}, "260608-3e6219da-aa53-4b9d-8cb9-8e5006723d06_a231661664": {"rating": 92.04, "score": 68}, "260608-fdfab57a-8939-4090-8f3d-b5f2668408b6_a231661664": {"rating": 86.77, "score": 150}, "260608-823d1e9e-3e27-448b-89b5-e676a204d19b_a231661664": {"rating": 95.55, "score": -235}, "260609-4f46e14e-dc13-4768-b2b6-c133bd0a431f_a231661664": {"rating": 92.02, "score": 67}, "260609-353dc56d-cfad-418f-b685-77518db6bc0d_a231661664": {"rating": 94.03, "score": -237}, "260609-d384c1a3-9b92-4d21-a4a3-13611c0a1f3b_a231661664": {"rating": 95.88, "score": -240}, "260609-02f32950-84b7-4e98-95b9-d2281562f16a_a231661664": {"rating": 91.49, "score": 151}, "260609-9b9db46c-9594-47a4-9622-f11d6592cc65_a231661664": {"rating": 90.5, "score": -232}, "260609-73a7e33b-d1a2-4605-8e69-9bb166773b94_a231661664": {"rating": 94.13, "score": 154}, "260609-85458f3e-eec9-4ee4-90a7-69edb86a640b_a231661664": {"rating": 93.87, "score": 138}, "260609-305ce1e7-713c-4f01-93c3-31f4b824284c_a231661664": {"rating": 94.35, "score": 139}, "260609-5ca50d67-e89a-4e98-b59f-2b130d1ea1e9_a231661664": {"rating": 96.01, "score": 71}, "260609-6b86e85d-16e8-46a5-aefd-9595b8e1cbb1_a231661664": {"rating": 91.94, "score": 65}, "260609-e6e667db-68de-47d0-bdb4-4c7b9e176875_a231661664": {"rating": 94.64, "score": 67}, "260610-4ad0497e-4737-4446-868e-7af01ebed505_a231661664": {"rating": 94.01, "score": 68}, "260610-f3eb7df4-80a6-497d-b825-37b8733db93d_a231661664": {"rating": 91.57, "score": 153}, "260610-c8a2af5c-c1af-4838-8fc4-7a63290a3c1d_a231661664": {"rating": 95.31, "score": -249}, "260610-c01f6a9a-50f6-4a99-92e9-08831e18fd06_a231661664": {"rating": 94.01, "score": -256}, "260610-14b428a8-2d9b-423c-a1b3-48401e259a7c_a231661664": {"rating": 92.19, "score": 141}, "260610-aebb790c-63a5-4e5e-82af-4fd5cd459f81_a231661664": {"rating": 93.03, "score": 139}, "260610-10b8d83f-b1ae-49f3-b2bd-f4143bc0ea78_a231661664": {"rating": 88.96, "score": 146}, "260610-7d74f116-3565-4a7c-aa3e-9821b6304a71_a231661664": {"rating": 92.37, "score": 135}, "260610-71ce0990-1da6-475c-b187-f38a99c5ad7b_a231661664": {"rating": 95.75, "score": -251}, "260611-a31a7326-e353-4116-aec8-4b8fb92ea940_a231661664": {"rating": 94.22, "score": -1}, "260611-7e632c49-bb1f-405e-b5f1-bcfe9ca99912_a231661664": {"rating": 95.34, "score": 67}, "260611-625e87b0-8bcd-459b-9731-1ce827ac91e4_a231661664": {"rating": 95.29, "score": 60}, "260611-6dd87b85-73bd-434c-9269-261c480842dc_a231661664": {"rating": 92.6, "score": -4}, "260611-491d9a28-19a7-4bbb-bd1a-efa5fb38bb48_a231661664": {"rating": 93.12, "score": 155}, "260611-56b7f3ef-e7cb-4064-a25e-09b8f32178cc_a231661664": {"rating": 95.02, "score": -21}, "260611-0f69e6af-e647-47e1-a6f9-b9ce3f1354d2_a231661664": {"rating": 92.11, "score": 134}, "260611-687dcf7c-75ba-447c-a56c-a2716c2f597f_a231661664": {"rating": 95.54, "score": -233}, "260611-3373831d-6cf7-422e-9d81-17639479a578_a231661664": {"rating": 92.15, "score": -1}, "260612-d860fa01-14dd-4668-95ff-7b79bd5224d5_a231661664": {"rating": 91.9, "score": 139}, "260612-8a9213a0-d41b-45fc-86dd-a157fb9735a4_a231661664": {"rating": 90.75, "score": -3}, "260612-e4ad81a1-7a81-4e1e-ba95-30854302d203_a231661664": {"rating": 96.55, "score": 132}, "260612-9958f761-d63e-4681-acc6-b464b60bb220_a231661664": {"rating": 94.84, "score": -19}, "260612-dfe960ad-8de6-4670-b6a0-ea1cde9efe42_a231661664": {"rating": 97.99, "score": 72}, "260612-a64485aa-6ac1-4631-a68d-81c7ce1c2daf_a231661664": {"rating": 96.38, "score": 163}, "260612-3034ac91-ede2-4354-bc08-566cc148fa45_a231661664": {"rating": 97.82, "score": 72}, "260612-dee49dd2-b0e3-4e49-be6d-5f5f5f554b17_a231661664": {"rating": 94.46, "score": 62}, "260612-7fd16801-3a94-4264-a5ef-5504e9caaa76_a231661664": {"rating": 88.38, "score": 74}, "260613-7f95c0d4-8bf4-489e-8128-355a7f9ed737_a231661664": {"rating": 88.45, "score": 143}, "260613-0eb34943-9981-40bf-86dd-d3951a018754_a231661664": {"rating": 92.06, "score": 142}, "260613-ff5fcb1c-2edd-4730-95c8-b34f14860cde_a231661664": {"rating": 90.05, "score": 60}, "260613-c7876306-b5b4-494d-85b0-5fc1e222bb07_a231661664": {"rating": 91.9, "score": -252}, "260613-bd590b0c-2abb-4905-af8c-9ca7a8297d10_a231661664": {"rating": 93.16, "score": -254}, "260613-8e780561-07a7-4d09-ba04-b3e20cd1779e_a231661664": {"rating": 92.18, "score": 144}, "260613-11469284-e046-482b-bae9-fbaa0cb7ad9f_a231661664": {"rating": 84.38, "score": 69}, "260613-93920694-4e7b-4e58-94a0-b6349efb1aaa_a231661664": {"rating": 94.07, "score": 133}, "260613-798acb15-2348-4dbc-a014-1c4486c054ef_a231661664": {"rating": 88.35, "score": 71}, "260613-b92a6e01-f0ba-4bac-800b-33b5b8e5bf37_a231661664": {"rating": 92.5, "score": 143}, "260614-0c793073-67b4-41f9-8e22-70c4cb2f3d8a_a231661664": {"rating": 93.06, "score": -245}, "260614-3de05427-de76-4be8-ac0e-024f95caa991_a231661664": {"rating": 91.57, "score": 70}, "260614-e98ba594-c5c6-4e18-b491-5e70ae39e463_a231661664": {"rating": 92.4, "score": 151}, "260614-f9f945b6-e61e-46d5-a573-3cf94464eb4d_a231661664": {"rating": 94.64, "score": -243}, "260614-e7ce1ada-3340-46b9-992a-d94f9668517e_a231661664": {"rating": 90.5, "score": 138}, "260614-206e78b3-7c76-42d6-b20c-750d0b2b2af1_a231661664": {"rating": 94.35, "score": 143}, "260614-6cb0a106-ee23-4c86-b89e-17ba3bed3b89_a231661664": {"rating": 91.13, "score": 135}, "260614-190eb451-b9f0-469b-a362-b4362c55eedf_a231661664": {"rating": 96.93, "score": 64}, "260614-e1b54352-c8dc-4654-9bd2-9a418ead8a56_a231661664": {"rating": 91.11, "score": -4}, "260614-8ade28df-d108-4707-a459-4992975f07c7_a231661664": {"rating": 87.16, "score": 145}, "260615-5bb83ba5-59ab-4cb5-805e-26356c5f2e5a_a231661664": {"rating": 95.54, "score": 140}, "260615-026aef6e-00ac-4551-95f8-2abe88d41a42_a231661664": {"rating": 96.74, "score": -267}, "260615-78d8f02a-6868-4fc1-88a2-9c2aa6723e43_a231661664": {"rating": 94.04, "score": 70}, "260615-750a2605-f4ae-4210-8e1b-f57dc34dc5fb_a231661664": {"rating": 95.93, "score": 140}, "260615-96029145-7200-4fe6-9b60-d4f5393e5475_a231661664": {"rating": 93.54, "score": -11}, "260615-47ac98f4-f1fd-44a3-9c1d-75d258db3322_a231661664": {"rating": 92.97, "score": 70}, "260615-dfba1673-3634-474c-a731-10ab5d2034e6_a231661664": {"rating": 83.64, "score": -11}, "260615-6b0d94dd-0e5f-4c04-9d61-ba9c9fff90c8_a231661664": {"rating": 91.64, "score": 148}, "260615-11699bdc-9e87-462c-9f7a-434b30a90424_a231661664": {"rating": 92.69, "score": 55}, "260616-c4872480-0aaa-4ccf-989a-4b0c532ccac1_a231661664": {"rating": 75.62, "score": -20}, "260617-5eab8e67-f506-4b94-8046-0dcddc3f0402_a231661664": {"rating": 95.65, "score": 146}, "260617-9bea368b-79e0-4164-94f9-89d68187c3cc_a231661664": {"rating": 85.3, "score": 154}, "260617-6e905368-1352-4782-828e-bc1023123120_a231661664": {"rating": 76.64, "score": 143}, "260619-09efb1a2-6e13-463f-9952-dd282b14d48f_a231661664": {"rating": 92.83, "score": -266}, "260619-99b139ca-4381-4fcb-bf89-acfb955dd4a0_a231661664": {"rating": 90.88, "score": -20}, "260619-23cf56d3-9fce-47e3-9af6-627310fdf76e_a231661664": {"rating": 94.96, "score": -248}, "260619-0333e921-d4c2-4435-aeff-b234ed0504b7_a231661664": {"rating": 91.8, "score": -13}, "260619-4cbeccb8-1917-44c6-9560-cfa294668312_a231661664": {"rating": 84.12, "score": 66}, "260620-50a216f6-a606-489f-a5db-24ded6ed4bbe_a231661664": {"rating": 90.31, "score": -262}, "260620-dd8a56ee-e0e0-4eef-917e-a89c87518498_a231661664": {"rating": 94.95, "score": 147}, "260620-27325a27-b470-40d6-abeb-b0ac2b37b5f0_a231661664": {"rating": 88.26, "score": 132}, "260620-38b5f3b4-9717-465a-ad29-63f02af79c24_a231661664": {"rating": 94.1, "score": -6}, "260620-f1dfceaa-fd9c-455a-b260-e7c0694e6417_a231661664": {"rating": 93.76, "score": 141}, "260620-0611ca95-051a-4594-999a-a17deee58ca8_a231661664": {"rating": 95.52, "score": -255}, "260621-e521f94b-1c48-413e-b524-c9c0ba70453f_a231661664": {"rating": 83.25, "score": 137}}
    image_bytes = plot_rating_score(data, "小诗乃")
    with open(f"小诗乃_{uuid4().hex[:8]}.png", "wb") as f:
        f.write(image_bytes)