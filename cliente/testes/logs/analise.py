import os
import pandas as pd
import matplotlib.pyplot as plt

here = os.path.abspath(os.path.dirname(__file__))

uploadsLog = os.path.join(here, "uploads.csv")
uploadsLogGraf = uploadsLog.replace(".csv", "_grafico.png")

log = pd.read_csv(uploadsLog)
log = log.sort_values(by="size_MB", ascending=True)

#print(log.describe())

log["_time_suave"] = log["_time"].rolling(window=5, center=True).mean()

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(log["size_MB"], log["_time"], marker='o', linestyle='-', alpha=0.3, label="Original")

ax.plot(log["size_MB"], log["_time_suave"], color='orange', linewidth=2, label="Média móvel")

ax.set_title('Tempo de transferência vs Tamanho')
ax.set_xlabel("Tamanho (MB)")
ax.set_ylabel("Tempo (s)")
ax.grid(True)
ax.legend()

plt.tight_layout()
fig.savefig(uploadsLogGraf, dpi=300)




