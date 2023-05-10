from alive_progress import alive_bar
import time

for x in 1000, 1500, 700, 0:
    with alive_bar(x, title="Title Here", enrich_print=True, stats="({rate}, eta: {eta})") as bar:
        for i in range(1000):
            time.sleep(.005)
            bar()
