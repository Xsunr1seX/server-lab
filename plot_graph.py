import json
import matplotlib.pyplot as plt
with open('benchmark_results.json', 'r') as f:
    data = json.load(f)
workers = [r['workers'] for r in data]
speeds = [r['speed'] for r in data]
times = [r['time'] for r in data]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
ax1.plot(workers, speeds, 'o-')
ax1.set_xlabel('Воркеры')
ax1.set_ylabel('Скорость (изобр/сек)')
ax1.set_title('Производительность')
ax1.grid(True, alpha=0.3)
ax2.plot(workers, times, 's-', color='red')
ax2.set_xlabel('Воркеры')
ax2.set_ylabel('Время (сек)')
ax2.set_title('Время обработки')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graph.png', dpi=300)
plt.show()