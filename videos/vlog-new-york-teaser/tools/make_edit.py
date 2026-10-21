#!/usr/bin/env python3
"""Write edit.json for the teaser.

Cut times are written in SONG time (seconds in the Sinatra track), taken from the
analysis of the recording: drum count-in hits, the vamp's bass/drum beats, then
the finale's band hits. They are converted here to teaser time.

Song passages used:
  A  0.30 -> 25.47   count-in, vamp, "Start spreading the news, I'm leaving today"
     + one beat of silence (black)
  B  174.27 -> 205.45  "If I can make it there ... New York, New York" to the last hit
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

A_FROM, A_TO, BREATH = 0.30, 25.47, 0.55
B_FROM, B_TO = 174.27, 205.45


def to_out(t):
    if t <= A_TO:
        return t - A_FROM
    return t - B_FROM + (A_TO - A_FROM) + BREATH


# Rushes compilation: clip number -> [start, end] in VLOG NEW YORK GOOD.mp4
CLIPS = {
    0: [0.0, 1.633], 7: [5.533, 7.0], 10: [10.1, 12.167], 19: [25.867, 27.433], 38: [49.967, 51.7],
    43: [59.667, 61.167], 45: [62.833, 64.7], 60: [92.5, 94.9], 63: [97.8, 98.667], 8: [7.0, 8.333], 9: [8.333, 10.1], 11: [12.167, 14.5],
    12: [14.5, 16.5], 13: [16.5, 18.167], 15: [19.767, 22.167], 16: [22.167, 23.367],
    18: [24.433, 25.867], 20: [27.433, 28.867], 21: [28.867, 29.967], 22: [29.967, 31.267],
    23: [31.267, 32.067], 24: [32.067, 33.667], 25: [33.667, 35.033], 26: [35.033, 36.067],
    27: [36.067, 37.667], 28: [37.667, 38.667], 29: [38.667, 40.1], 30: [40.1, 42.533],
    31: [42.533, 44.367], 32: [44.367, 45.933], 35: [45.933, 48.333], 36: [48.333, 49.967],
    41: [54.967, 57.633], 42: [57.633, 59.667], 44: [61.167, 62.833], 46: [64.7, 66.3],
    47: [66.3, 68.4], 48: [68.4, 70.367], 50: [72.133, 73.767], 52: [75.0, 77.733],
    53: [77.733, 80.3], 54: [80.3, 83.567], 55: [83.567, 85.1], 56: [85.1, 86.6],
    58: [88.2, 89.633], 59: [89.633, 92.5], 64: [98.667, 100.1], 66: [101.267, 102.467],
    68: [103.767, 105.767], 69: [105.767, 108.567], 70: [108.567, 111.467], 73: [122.967, 127.5],
    74: [127.5, 129.5], 75: [129.5, 134.3], 76: [134.3, 136.2],
}

# (song time of the cut, clip or None for black, where to take it, label)
# where: None = centred in the clip, a number = source in-point, "end" = ends on the clip's
# last frame.
SHOTS = [
    # Drum count-in: one flash per hit
    (0.30, 12, None, "Flash : écrans géants de Times Square"),
    (0.53, 31, None, "Flash : Empire State illuminé"),
    (0.68, 23, None, "Flash : Statue de la Liberté"),
    (0.88, 70, 110.0, "Flash : taxi jaune dans la vapeur"),
    # Vamp: the band comes in
    (1.46, 30, 40.12, "Times Square de nuit, la foule"),
    (3.69, 20, None, "Pont de Brooklyn"),
    (4.77, 25, None, "DUMBO, Manhattan Bridge"),
    (5.87, 70, 109.0, "Hot-dog, vapeur, taxi jaune"),
    (6.95, 27, None, "Top of the Rock"),
    (8.05, 32, 44.40, "School bus jaune"),
    (9.12, 46, None, "Camion de pompiers FDNY"),
    # one shot per beat
    (10.22, 59, 90.20, "Saxophoniste dans le métro"),
    (10.75, 35, 46.60, "Métro, ses cheveux dans le souffle de la rame"),
    (11.28, 69, 106.0, "Grand Central"),
    (11.83, 24, None, "Vapeur qui sort de la rue"),
    (12.37, 11, 12.90, "Times Square sous la pluie, il lève les yeux"),
    (12.92, 29, 39.20, "Times Square, elle lève les yeux"),
    (13.48, 64, None, "Selfie à Times Square"),
    (14.01, 12, 15.60, "Affiches géantes"),
    # one shot per half beat
    (14.55, 26, None, "Top of the Rock, Central Park"),
    (14.82, 28, None, "Malle Louis Vuitton géante"),
    (15.08, 21, None, "Muséum d'histoire naturelle"),
    (15.36, 19, None, "Taqueria, les cuisiniers"),
    (15.63, 16, None, "Van NYPD"),
    (15.90, 47, None, "Club de jazz"),
    (16.16, 45, None, "Église gospel pleine"),
    (16.42, 60, None, "Match de softball à Central Park"),
    # "Start spreading the news, I'm leaving today"
    (16.69, 41, 55.0, "Ferry, il regarde Manhattan"),
    (18.94, 9, 8.36, "Grand Central, il montre le hall"),
    (20.06, 13, None, "Métro, la rame arrive"),
    (21.15, 22, 30.0, "Water taxi"),
    (22.23, 69, 107.2, "Grand Central, il s'avance"),
    (23.34, 18, None, "Bras ouverts devant la Statue"),
    (24.43, 74, "end", "Il court et saute par-dessus la caméra"),
    # one beat of black and silence
    (A_TO, None, None, "Noir, silence"),
    # "If I can make it there"
    (B_FROM, 42, None, "Jumelles au sommet de l'Empire State"),
    (175.86, 36, 48.70, "Vélo dans Central Park"),
    (176.67, 44, 61.70, "Gospel"),
    (177.75, 56, None, "Broadway"),
    # "I'm gonna make it anywhere": one shot per beat
    (178.82, 7, 5.70, "Pluie de confettis"),
    (179.30, 8, 7.70, "Fous rires sous les confettis"),
    (179.85, 66, 101.40, "Supporters du PSG au bar"),
    (180.35, 68, 104.0, "Supporters du PSG à Times Square"),
    (180.88, 48, 69.20, "Acrobates dans le parc"),
    (181.51, 15, 20.40, "Yankee Stadium"),
    (182.01, 63, None, "Elle croque une part de pizza"),
    (182.50, 43, None, "Pizzaïolos qui lancent la pâte"),
    # "It's up to you": the breath
    (183.00, 54, 80.40, "Lui dans l'hélico"),
    # Band slam, "New York!"
    (185.78, 53, 77.90, "Hélico : Midtown"),
    (187.04, 52, 75.20, "Hélico : Downtown"),
    (188.26, 50, 72.20, "Hélico : la Statue vue du ciel"),
    # "New York!"
    (189.51, 55, None, "L'hélico au-dessus de Central Park"),
    (190.75, 10, None, "Times Square sous la pluie"),
    (192.05, 58, None, "Elle sur le pont de Brooklyn"),
    (193.31, 76, None, "Lui sur le pont de Brooklyn"),
    # "New Yooork", held
    (194.55, 0, None, "Central Park, il montre la skyline"),
    (195.77, 38, None, "Elle à vélo, la skyline derrière"),
    (197.04, 73, 124.70, "Ferry : il présente la skyline"),
    (198.38, 75, None, "Vue panoramique depuis l'Empire State"),
    # Last band hit
    (203.02, None, None, "Noir"),
]


def main():
    fps = 30
    end = to_out(B_TO)
    starts = [to_out(t) for t, *_ in SHOTS] + [end]
    shots = []
    for i, (t, clip, where, label) in enumerate(SHOTS):
        start = starts[i]
        n = round(starts[i + 1] * fps) - round(start * fps)
        shot = {"clip": clip, "start": round(start, 3), "label": label, "song": t}
        if clip is not None:
            a, b = CLIPS[clip]
            if where is None:
                src = a + max(0.0, (b - a - n / fps) / 2)
            elif where == "end":
                src = b - n / fps - 1 / fps
            else:
                src = where
            shot["src"] = round(src, 3)
        shots.append(shot)
    edit = {
        "source": "VLOG NEW YORK GOOD.mp4",
        "fps": fps,
        "end": round(end, 3),
        "music": {
            "song": "Frank Sinatra - New York, New York",
            "segments": [
                {"from": A_FROM, "to": A_TO},
                {"silence": BREATH},
                {"from": B_FROM, "to": B_TO},
            ],
            "crossfade": 0.02,
            "fade_out": 1.0,
        },
        "video_fade_out_frames": 0,
        "shots": shots,
        "clips": {str(k): v for k, v in CLIPS.items()},
    }
    (ROOT / "edit.json").write_text(json.dumps(edit, ensure_ascii=False, indent=1) + "\n")
    print(f"{len(shots)} shots, {end:.2f} s")


if __name__ == "__main__":
    main()
