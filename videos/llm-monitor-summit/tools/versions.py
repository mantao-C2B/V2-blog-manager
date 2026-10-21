"""Edit decision lists for the three versions.

Times in `src` / `out` / `asrc` are source timecodes in the rushes (seconds). `talk()` splits a spoken
passage at its pauses (jump cuts, alternating framings); other shots are b-roll or soundbites.
Each version also returns its overlays (motion design), SFX cues, music spec and storyboard sections.
"""

from transcript import words_in

FPS = 30


def q(t):
    return round(round(t * FPS) / FPS, 4)


def talk(a, b, gap=0.5, pre=0.1, post=0.16, zooms=(1.0, 1.12), focal=(50, 42), prefix=None, splits=(), **kw):
    """Spoken passage: pauses longer than `gap` are cut out (jump cuts); `splits` are extra cut points
    (source times) where only the framing changes. Framings alternate through `zooms`."""
    ws = words_in(a, b)
    runs, cur = [], [ws[0]]
    for w in ws[1:]:
        if w["s"] - cur[-1]["e"] > gap:
            runs.append(cur)
            cur = [w]
        else:
            cur.append(w)
    runs.append(cur)
    spans = []
    for r in runs:
        s0 = max(a, r[0]["s"] - pre)
        s1 = min(b, r[-1]["e"] + post)
        cuts = [x for x in splits if s0 + 0.8 < x < s1 - 0.8]
        edges = [s0] + cuts + [s1]
        spans += list(zip(edges[:-1], edges[1:]))
    shots = []
    for i, (s0, s1) in enumerate(spans):
        sh = dict(src=q(s0), out=q(s1), kind="talk", zoom=zooms[i % len(zooms)], focal=list(focal), **kw)
        if prefix:
            sh["id"] = f"{prefix}{i}"
        shots.append(sh)
    return shots


def broll(src, dur, focal=(50, 50), move="push", tin="cut", **kw):
    return dict(src=q(src), out=q(src + dur), kind="broll", focal=list(focal), move=move, tin=tin, **kw)


def bite(src, out, focal=(50, 45), **kw):
    return dict(src=q(src), out=q(out), kind="bite", focal=list(focal), **kw)


class Ctx:
    def __init__(self, shots):
        self.shots = shots
        self.by_id = {s["id"]: s for s in shots}
        self.sec = []

    def t(self, sid, off=0.0):
        return round(self.by_id[sid]["start"] + off, 3)

    def end(self, sid, off=0.0):
        s = self.by_id[sid]
        return round(s["start"] + s["dur"] + off, 3)

    def src(self, t):
        for s in self.shots:
            a0 = s.get("asrc", s["src"]) if s.get("kind") in ("talk", "bite") else s["src"]
            if a0 - 1e-3 <= t <= a0 + s["dur"] + 1e-3:
                return round(s["start"] + (t - a0), 3)
        raise KeyError(f"source time {t} not in the edit")

    def word(self, text, after, before=1e9):
        from transcript import WORDS
        for w in WORDS:
            if after <= w["s"] <= before and w["w"].lower().strip(",.?!") .startswith(text.lower()):
                return self.src(w["s"])
        raise KeyError(f"word {text!r} after {after}")

    def section(self, title, sid, scene, motion=""):
        self.sec.append((title, sid, scene, motion))

    def sections(self, duration):
        out = []
        for i, (title, sid, scene, motion) in enumerate(self.sec):
            t0 = self.t(sid)
            t1 = self.t(self.sec[i + 1][1]) if i + 1 < len(self.sec) else duration
            out.append({"title": title, "t0": t0, "t1": t1, "scene": scene, "motion": motion})
        return out


CSS_WIDE = {
    "--m": "96px", "--hl-size": "150px", "--lt-bottom": "250px", "--ch-w": "980px", "--ch-size": "150px",
    "--logos-top": "96px", "--ct-top": "190px", "--ct-size": "132px", "--st-w": "780px", "--st-size": "200px",
    "--st-bottom": "200px", "--cp-size": "78px", "--qt-size": "80px", "--tk-w": "860px", "--tk-size": "70px",
    "--co-top": "200px", "--end-sym": "190px", "--end-name": "112px", "--end-tag": "66px",
    "--cap-size": "56px", "--cap-bottom": "84px",
}

CSS_PORTRAIT = {  # 1080x1350
    "--m": "72px", "--hl-size": "112px", "--lt-bottom": "330px", "--ch-w": "1080px", "--ch-size": "132px",
    "--logos-top": "150px", "--ct-top": "200px", "--ct-size": "120px", "--st-w": "936px", "--st-size": "190px",
    "--st-bottom": "300px", "--cp-size": "70px", "--qt-size": "72px", "--tk-w": "936px", "--tk-size": "66px",
    "--co-top": "190px", "--end-sym": "210px", "--end-name": "104px", "--end-tag": "62px",
    "--cap-size": "58px", "--cap-bottom": "190px",
}

CSS_SQUARE = {  # 1080x1080
    "--m": "64px", "--hl-size": "112px", "--lt-bottom": "230px", "--ch-w": "1080px", "--ch-size": "120px",
    "--logos-top": "120px", "--ct-top": "150px", "--ct-size": "112px", "--st-w": "952px", "--st-size": "170px",
    "--st-bottom": "250px", "--cp-size": "62px", "--qt-size": "64px", "--tk-w": "952px", "--tk-size": "60px",
    "--co-top": "150px", "--end-sym": "180px", "--end-name": "96px", "--end-tag": "56px",
    "--cap-size": "52px", "--cap-bottom": "120px",
}

AI = {"chatgpt": ("ChatGPT", "chatgpt"), "gemini": ("Gemini", "gemini"), "claude": ("Claude", "claude")}


# ============================================================================== V1 — Le vlog (16:9)
def v1():
    B = 0.5  # one beat at 120 BPM
    shots = []
    # HOOK — 8 cuts on the beat
    hook = [(28.2, (50, 50)), (34.0, (40, 50)), (38.8, (45, 45)), (155.0, (55, 45)),
            (161.7, (50, 40)), (199.4, (45, 45)), (204.6, (55, 55)), (103.3, (40, 50))]
    for i, (src, f) in enumerate(hook):
        shots.append(broll(src, B, focal=f, move="push", tin="punch" if i else "zoom", id=f"hook{i}", amb=0.6))
    # INTRO — Maxence in front of the Hotel Marvel, then walking
    shots += talk(0.0, 19.40, prefix="intro", focal=(50, 38), splits=(4.08, 7.62, 13.22), zooms=(1.0, 1.14))
    shots[len(hook)]["tin"] = "zoom"
    shots += talk(24.86, 26.80, prefix="walk", focal=(48, 40), zooms=(1.0,))
    # CHAPTER 1 — the show floor
    shots += [
        broll(27.6, 2.0, focal=(50, 50), move="push", tin="whip", id="floor0"),
        broll(33.9, 1.5, focal=(35, 50), move="pan-r", tin="punch", id="floor1"),
        broll(36.4, 2.0, focal=(45, 45), move="push", tin="punch", id="floor2"),
        broll(53.4, 1.5, focal=(45, 50), move="pan-l", tin="punch", id="floor3"),
        broll(56.2, 2.0, focal=(50, 40), move="push", tin="punch", id="floor4"),
        broll(77.0, 1.5, focal=(50, 50), move="pan-r", tin="punch", id="floor5", tout="whip"),
    ]
    shots += talk(80.27, 95.62, prefix="salon", focal=(45, 40), splits=(84.55, 91.45))
    c_salon = next(i for i, x in enumerate(shots) if x.get("id") == "salon0")
    shots[c_salon]["tin"] = "whip"
    # CHAPTER 2 — the booth + Guillaume
    shots += [
        broll(103.1, 1.8, focal=(40, 50), move="pan-l", tin="whip", id="booth0"),
        broll(96.2, 1.5, focal=(45, 45), move="push", tin="punch", id="booth1"),
        broll(99.9, 1.5, focal=(40, 45), move="push", tin="punch", id="booth2"),
        broll(110.5, 1.5, focal=(35, 45), move="pull", tin="punch", id="booth3"),
        broll(113.8, 1.7, focal=(45, 45), move="push", tin="punch", id="booth4"),
    ]
    shots += talk(116.52, 128.25, prefix="ceo", focal=(58, 38), zooms=(1.0, 1.12), splits=(120.72, 126.30))
    shots += talk(132.72, 141.30, prefix="ceob", focal=(58, 38), zooms=(1.12, 1.0), splits=(136.72, 139.20))
    shots += talk(141.33, 153.05, prefix="go", focal=(50, 38), splits=(147.50, 151.45))
    # CHAPTER 3 — the conference
    shots += [
        broll(154.0, 2.5, focal=(60, 45), move="push", tin="whip", id="conf0"),
        broll(159.9, 3.2, focal=(50, 40), move="push", tin="punch", id="conf1", amb=1.4),
        bite(180.45, 182.45, focal=(55, 45), id="conf2", tin="punch"),
        bite(198.50, 201.55, focal=(45, 45), id="conf3", tin="punch"),
        bite(236.35, 241.05, focal=(40, 50), id="conf5"),
        broll(242.0, 2.6, focal=(50, 40), move="push", tin="cut", id="conf6", amb=1.4),
        bite(256.70, 260.95, focal=(50, 40), id="conf7", tin="punch"),
        broll(248.6, 1.6, focal=(50, 50), move="pan-l", tin="punch", id="conf8"),
        broll(302.3, 2.0, focal=(50, 50), move="pull", tin="punch", id="conf9", tout="whip"),
    ]
    # OUTRO — Maxence at the booth, cutaways on the audience while he talks about it
    shots += talk(308.62, 315.95, prefix="outro", focal=(50, 40), splits=(310.45,))
    c_out = next(i for i, x in enumerate(shots) if x.get("id") == "outro0")
    shots[c_out]["tin"] = "whip"
    shots += [
        dict(src=q(169.4), out=q(169.4 + 1.9), asrc=q(316.05), kind="talk", focal=[50, 50], move="push", tin="punch", id="cut0"),
        dict(src=q(204.5), out=q(204.5 + 1.1), asrc=q(317.95), kind="talk", focal=[55, 55], move="push", tin="punch", id="cut1"),
        dict(src=q(230.2), out=q(230.2 + 2.8), asrc=q(319.05), kind="talk", focal=[50, 50], move="push", tin="punch", id="cut2"),
        dict(src=q(244.4), out=q(244.4 + 0.8), asrc=q(321.85), kind="talk", focal=[45, 45], move="push", tin="punch", id="cut3"),
    ]
    shots += talk(333.70, 344.45, prefix="close", focal=(50, 40), splits=(338.42,), zooms=(1.12, 1.0))

    def post(c):
        o, sfx = [], []
        end_t = c.end(shots[-1]["id"])
        # hook
        o.append(dict(type="headline", start=0.0, dur=c.t("intro0") - 0.02, kicker="Vlog · 15 & 16 octobre 2026", kickerAt=0.05,
                      lines=[dict(text="SEO & GEO", style="big", fx="slam", at=0.5, stagger=0.12),
                             dict(text="Summit", style="serif", fx="slam", at=1.0)],
                      sub="Disneyland Paris · avec l'équipe LLM Monitor", subAt=1.6))
        sfx += [(0.5, "impact-bass-1", 0.55), (1.0, "whoosh-short", 0.4), (c.t("intro0"), "whoosh", 0.35)]
        # intro
        o.append(dict(type="bug", start=c.t("intro0") + 0.4, dur=end_t - c.t("intro0") - 0.4, text="SEO & GEO Summit 2026"))
        o.append(dict(type="lower", start=c.t("intro0") + 0.3, dur=3.6, name="Maxence Antao", role="Responsable communication · Market Connect"))
        sfx.append((c.t("intro0") + 0.3, "click-soft", 0.35))
        tl = c.word("Disneyland", 4)
        o.append(dict(type="location", start=tl, dur=3.6, place="Disneyland Paris", detail="Hôtel Marvel · SEO & GEO Summit"))
        sfx.append((tl, "pop", 0.3))
        items = []
        for key, after in (("chatgpt", 13), ("gemini", 13), ("claude", 13)):
            tt = c.word(AI[key][0], after, 20)
            items.append(dict(name=AI[key][0], logo=AI[key][1], t=tt))
            sfx.append((tt, "pop", 0.32))
        o.append(dict(type="logos", start=items[0]["t"], dur=c.word("stratégies", 18) - items[0]["t"] + 0.6, items=items))
        # chapter 1
        o.append(dict(type="chapter", start=c.t("floor0"), dur=1.9, num="01", title="Le salon", kicker="SEO & GEO Summit"))
        sfx += [(c.t("floor0"), "whoosh-cinematic", 0.3)]
        tc = c.word("cit", 88)
        o.append(dict(type="callout", start=tc - 0.2, dur=3.0, icon="message-square", text="Être cité par les IA", pos="right"))
        tm = c.word("mesurer", 92)
        o.append(dict(type="callout", start=tm - 0.2, dur=3.2, icon="chart-column", text="Mesurer sa visibilité", pos="right"))
        sfx += [(tc - 0.2, "click", 0.3), (tm - 0.2, "click", 0.3)]
        # chapter 2
        o.append(dict(type="chapter", start=c.t("booth0"), dur=1.9, num="02", title="Le stand", kicker="LLM Monitor"))
        sfx += [(c.t("booth0"), "whoosh-cinematic", 0.3)]
        o.append(dict(type="lower", start=c.t("ceo0") + 0.3, dur=3.8, name="Guillaume Fraybin", role="CEO · LLM Monitor", side="left"))
        sfx.append((c.t("ceo0") + 0.3, "click-soft", 0.35))
        tv = c.word("mesurer", 122)
        o.append(dict(type="callout", start=tv - 0.1, dur=3.6, icon="radar", text="Votre visibilité dans les IA", pos="right"))
        items = []
        for key in ("gemini", "chatgpt", "claude"):
            tt = c.word(AI[key][0][:5], 126, 128.5)
            items.append(dict(name=AI[key][0], logo=AI[key][1], t=tt))
            sfx.append((tt, "pop", 0.3))
        o.append(dict(type="logos", start=items[0]["t"], dur=2.4, items=items))
        tli = c.word("LinkedIn", 137)
        o.append(dict(type="callout", start=tli - 0.3, dur=3.2, icon="bell", text="Résultats de l'étude sur LinkedIn", pos="right"))
        sfx.append((tli - 0.3, "notification", 0.25))
        t150 = c.word("150", 144)
        o.append(dict(type="counter", start=t150 - 0.25, dur=4.2, value=150000, prefix="+", kicker="L'étude présentée", label="conversations ChatGPT analysées", pos="right"))
        sfx.append((t150 - 0.25, "sparkle", 0.3))
        # chapter 3
        o.append(dict(type="chapter", start=c.t("conf0"), dur=2.1, num="03", title="La conférence", kicker="Guillaume Fraybin · CEO"))
        sfx += [(c.t("conf0"), "whoosh-cinematic", 0.3)]
        o.append(dict(type="talk", start=c.t("conf1"), dur=c.end("conf1") - c.t("conf1") + 0.1, kicker="Conférence · SEO & GEO Summit",
                      title="ChatGPT préfère vos **concurrents** !", sub="…et comment reprendre la place.", by="Guillaume Fraybin · CEO LLM Monitor"))
        o.append(dict(type="callout", start=c.word("quatre", 200) - 0.6, dur=2.6, icon="refresh-cw", text="Tous les 4 jours, ça change", pos="right"))
        sfx.append((c.word("quatre", 200) - 0.6, "click", 0.3))
        o.append(dict(type="stat", start=c.t("conf5") + 0.2, dur=c.end("conf6") - c.t("conf5") - 0.2, value=11, pos="right",
                      kicker="Nos données · ChatGPT, Claude, Gemini",
                      text="des sources citées pour recommander une marque sont le site de la marque.",
                      foot="Quand l'IA recommande une marque, elle cite son site environ <b>1 fois sur 9</b>.", footAt=1.6))
        sfx += [(c.t("conf5") + 0.2, "whoosh", 0.3), (c.t("conf5") + 0.5, "sparkle", 0.25)]
        o.append(dict(type="callout", start=c.word("majorité", 256) - 0.2, dur=3.6, icon="users", text="La majorité est sur ChatGPT", pos="right"))
        sfx.append((c.word("majorité", 256) - 0.2, "click", 0.3))
        # end card
        o.append(dict(type="end", start=end_t, dur=6.0, tagline="Pilotez votre visibilité dans les **IA.**",
                      cta="Suivez LLM Monitor sur LinkedIn", url="llm-monitor.com"))
        sfx += [(end_t - 0.05, "impact-bass-2", 0.5), (end_t + 1.25, "chime", 0.28)]
        flashes = [c.t("intro0"), c.t("conf5")]
        dips = []
        c.section("Accroche", "hook0", "8 plans sur le tempo, titre SEO & GEO Summit qui claque", "headline slam + punch cuts")
        c.section("Intro de Maxence", "intro0", "Maxence devant l'Hôtel Marvel puis en marche vers le salon", "lower third, location tag, logos IA")
        c.section("01 Le salon", "floor0", "Allées, stand LLM Monitor, échanges", "chapter card, whip/punch cuts, pans")
        c.section("Maxence au salon", "salon0", "L'enjeu : être cité par les IA et mesurer sa visibilité", "callouts")
        c.section("02 Le stand", "booth0", "Le stand LLM Monitor et l'équipe", "chapter card, punch cuts")
        c.section("Interview de Guillaume", "ceo0", "Ce qu'est LLM Monitor, la conférence, LinkedIn", "lower third, logos IA, callouts")
        c.section("Direction la conférence", "go0", "150 000 conversations ChatGPT", "counter")
        c.section("03 La conférence", "conf0", "Salle pleine, extraits de Guillaume, la donnée 11 %", "talk card, stat card, callout")
        c.section("Conclusion de Maxence", "outro0", "Bilan, cutaways sur le public qui photographie les slides", "jump cuts")
        return o, sfx, flashes, dips

    def music(c, duration):
        end_t = c.end(shots[-1]["id"])
        S = [
            [0.0, c.t("intro0"), 3],
            [c.t("intro0"), c.t("floor0"), 1],
            [c.t("floor0"), c.t("salon0"), 3],
            [c.t("salon0"), c.t("booth0"), 1],
            [c.t("booth0"), c.t("ceo0"), 2],
            [c.t("ceo0"), c.t("conf0"), 1],
            [c.t("conf0"), c.t("outro0"), 2],
            [c.t("outro0"), end_t, 1],
            [end_t, duration, 3],
        ]
        return {"style": "vlog", "duration": duration, "sections": S,
                "impacts": [c.t("floor0"), end_t], "risers": [c.t("floor0"), c.t("booth0"), c.t("conf0"), end_t],
                "stops": [], "fills": [], "fade_out": 2.5}

    return dict(
        folder="v1-vlog", title="LLM Monitor au SEO & GEO Summit — le vlog", W=1920, H=1080, css=CSS_WIDE,
        message="LLM Monitor était au SEO & GEO Summit : un stand, une conférence, une étude sur ChatGPT.",
        arc="Accroche → Intro → Salon → Stand → Interview → Conférence → Conclusion → Carton de fin",
        shots=shots, post=post, music=music, tail=6.0, cap_chars=30, cap_words=5,
        cap_overrides={147.06: "", 91.11: "réponses", 91.57: "des", 140.6: "À", 237.74: "des", 308.72: "Conférence",
                       316.12: "Il", 124.16: "visibilité"},
        music_level=0.8, music_duck=0.15, ambience=1.0,
        music_overrides=[],
    )




# ============================================================================== V2 — L'aftermovie (4:5)
def v2():
    B = 60 / 128  # beat
    BAR = 4 * B
    shots = []
    # A — hook: 8 cuts on the beat under a slammed title
    hook = [(28.2, 50), (34.0, 30), (38.8, 40), (103.4, 30), (155.0, 62), (161.9, 50), (199.4, 42), (204.6, 55)]
    for i, (src, fx) in enumerate(hook):
        shots.append(broll(src, B, focal=(fx, 50), move="push", tin="punch" if i else "zoom", id=f"hook{i}"))
    # B — Maxence: "on n'est pas là pour faire les attractions..."
    shots += talk(8.46, 13.05, prefix="max", focal=(55, 40), zooms=(1.0, 1.12), splits=(9.96,))
    shots[len(hook)]["tin"] = "zoom"
    # C — build: cuts every 2 beats
    build = [(27.6, 50, "push"), (33.9, 25, "pan-r"), (36.6, 40, "push"), (53.6, 45, "pan-l"),
             (56.4, 45, "push"), (103.2, 32, "pan-l"), (114.0, 45, "push"), (96.4, 45, "push")]
    for i, (src, fx, mv) in enumerate(build):
        shots.append(broll(src, 2 * B, focal=(fx, 50), move=mv, tin="whip" if i == 0 else "punch", id=f"build{i}"))
    # D — Guillaume: what LLM Monitor is
    shots += talk(121.98, 128.10, prefix="ceo", focal=(60, 38), zooms=(1.0, 1.12), splits=(126.30,))
    shots[-2]["tin"] = "zoom"
    # E — drop: the conference
    drop = [(154.0, 62, 4), (160.2, 50, 2), (169.0, 50, 2), (178.0, 45, 1), (162.0, 50, 1), (188.0, 40, 2),
            (192.4, 45, 2), (199.0, 42, 1), (204.6, 55, 1), (208.6, 55, 2), (230.4, 50, 2), (256.8, 45, 2),
            (249.0, 50, 1), (283.6, 50, 1), (302.4, 50, 2)]
    for i, (src, fx, nb) in enumerate(drop):
        shots.append(broll(src, nb * B, focal=(fx, 45), move="push" if i % 2 else "pull", tin="zoom" if i == 0 else "punch", id=f"drop{i}"))
    shots.append(broll(236.4, 2 * BAR, focal=(30, 45), move="push", tin="punch", id="stat"))
    # F — Maxence closing line
    shots += talk(338.46, 344.40, prefix="close", focal=(50, 40), zooms=(1.0, 1.12), splits=(341.85,))
    shots[-2]["tin"] = "whip"

    def post(c):
        o, sfx = [], []
        end_t = c.end(shots[-1]["id"])
        o.append(dict(type="headline", start=0.0, dur=c.t("max0") - 0.02, kicker="15 & 16 octobre 2026", kickerAt=0.0,
                      lines=[dict(text="SEO & GEO", style="big", fx="slam", at=0.0, stagger=0.15),
                             dict(text="Summit", style="serif", fx="slam", at=2 * B)],
                      sub="Disneyland Paris", subAt=4 * B))
        sfx += [(0.0, "impact-bass-1", 0.5), (2 * B, "whoosh-short", 0.35)]
        o.append(dict(type="lower", start=c.t("max0") + 0.2, dur=3.4, name="Maxence Antao", role="Market Connect"))
        # build words
        for i, word in enumerate(("Rencontres.", "Démos.", "Échanges.")):
            t0 = c.t(f"build{2 * i}")
            o.append(dict(type="headline", start=t0, dur=4 * B - 0.05, shade=False, cls="beatword",
                          lines=[dict(text=word, style="sora", fx="slam", at=0.0, stagger=0.0)]))
            sfx.append((t0, "whoosh-short", 0.3))
        o.append(dict(type="lower", start=c.t("ceo0") + 0.15, dur=3.4, name="Guillaume Fraybin", role="CEO · LLM Monitor"))
        items = []
        for key in ("gemini", "chatgpt", "claude"):
            tt = c.word(AI[key][0][:5], 126, 128.5)
            items.append(dict(name=AI[key][0], logo=AI[key][1], t=tt))
            sfx.append((tt, "pop", 0.3))
        o.append(dict(type="logos", start=items[0]["t"], dur=c.t("drop0") - items[0]["t"], items=items))
        o.append(dict(type="talk", start=c.t("drop0"), dur=4 * B - 0.05, kicker="La conférence de LLM Monitor",
                      title="ChatGPT préfère vos **concurrents** !", by="Guillaume Fraybin · CEO", pos="bottom"))
        o.append(dict(type="stat", start=c.t("stat") + 0.1, dur=2 * BAR - 0.1, value=11, pos="bottom",
                      kicker="Nos données · ChatGPT, Claude, Gemini",
                      text="des sources citées par l'IA pour recommander une marque sont son propre site.",
                      foot="Environ <b>1 fois sur 9</b>.", footAt=1.4))
        sfx += [(c.t("stat") + 0.1, "whoosh", 0.3), (c.t("stat") + 0.4, "sparkle", 0.25)]
        o.append(dict(type="end", start=end_t, dur=5.6, tagline="Pilotez votre visibilité dans les **IA.**",
                      cta="Suivez LLM Monitor sur LinkedIn", url="llm-monitor.com"))
        sfx += [(end_t - 0.05, "impact-bass-2", 0.5), (end_t + 1.25, "chime", 0.28)]
        flashes = [c.t("drop0"), c.t("stat")]
        c.section("Accroche", "hook0", "8 plans au temps, titre SEO & GEO Summit", "headline slam, punch cuts")
        c.section("Maxence", "max0", "« On n'est pas là pour faire les attractions »", "lower third, captions")
        c.section("Montée", "build0", "Le salon et le stand, coupes toutes les 2 temps", "beat words, whips")
        c.section("Guillaume", "ceo0", "LLM Monitor mesure votre visibilité dans les IA", "lower third, logos IA")
        c.section("Drop — la conférence", "drop0", "Salle pleine, gestes, public qui photographie", "talk card, beat cuts, flash")
        c.section("La donnée", "stat", "11 % : la slide de l'étude", "stat card count-up")
        c.section("Conclusion", "close0", "« Je repars armé… avec LLM Monitor »", "captions")
        return o, sfx, flashes, []

    def music(c, duration):
        end_t = c.end(shots[-1]["id"])
        S = [
            [0.0, c.t("max0"), 3],
            [c.t("max0"), c.t("build0"), 1],
            [c.t("build0"), c.t("ceo0"), 2],
            [c.t("ceo0"), c.t("drop0"), 1],
            [c.t("drop0"), c.t("close0"), 3],
            [c.t("close0"), end_t, 1],
            [end_t, duration, 3],
        ]
        return {"style": "aftermovie", "duration": duration, "sections": S,
                "impacts": [0.0, c.t("drop0"), end_t], "risers": [c.t("build0"), c.t("drop0"), end_t],
                "stops": [c.t("drop0")], "fills": [], "fade_out": 2.2}

    return dict(
        folder="v2-aftermovie", title="LLM Monitor au SEO & GEO Summit — l'aftermovie", W=1080, H=1350, css=CSS_PORTRAIT,
        message="LLM Monitor au SEO & GEO Summit : l'énergie du salon et de la conférence en 45 secondes.",
        arc="Accroche → Maxence → Montée → Guillaume → Drop conférence → Donnée 11 % → Conclusion → Carton de fin",
        shots=shots, post=post, music=music, tail=5.6, cap_chars=22, cap_words=4,
        cap_overrides={}, music_level=0.95, music_duck=0.2, ambience=0.35,
    )


# ============================================================================== V3 — Les enseignements (1:1)
def v3():
    B = 0.6  # 100 BPM
    BAR = 4 * B
    shots = [
        broll(154.0, BAR, focal=(62, 45), move="push", tin="zoom", id="hook0"),
        broll(160.2, BAR, focal=(50, 40), move="push", tin="punch", id="hook1"),
    ]
    shots += talk(116.52, 120.50, prefix="ceo", focal=(60, 38), zooms=(1.0,))
    shots += talk(132.72, 136.72, prefix="ceob", focal=(60, 38), zooms=(1.12,))
    # insight 1 — the 11 %
    shots.append(broll(236.2, 1.9, focal=(30, 45), move="push", tin="whip", id="i1card", amb=0.0))
    shots.append(bite(236.35, 241.05, focal=(32, 45), id="i1"))
    shots += [
        dict(src=q(230.2), out=q(230.2 + 2.4), kind="broll", focal=[50, 50], move="push", tin="punch", id="todo0"),
        dict(src=q(244.3), out=q(244.3 + 1.4), kind="broll", focal=[45, 45], move="push", tin="punch", id="todo1"),
        dict(src=q(177.8), out=q(177.8 + 1.1), kind="broll", focal=[50, 45], move="push", tin="punch", id="todo2"),
        dict(src=q(188.2), out=q(188.2 + 1.9), kind="broll", focal=[40, 45], move="push", tin="punch", id="todo3"),
    ]
    # insight 2 — answers move every four days
    shots.append(broll(192.4, 1.8, focal=(45, 40), move="push", tin="whip", id="i2card"))
    shots.append(bite(196.70, 198.12, focal=(48, 40), id="i2a", tin="punch"))
    shots.append(bite(198.50, 201.55, focal=(45, 45), id="i2b", tin="punch"))
    # insight 3 — ChatGPT dominates
    shots.append(broll(283.5, 1.8, focal=(50, 40), move="push", tin="whip", id="i3card"))
    shots.append(bite(256.70, 260.95, focal=(50, 40), id="i3", tin="punch"))
    # social proof — Maxence over the audience
    shots += [
        dict(src=q(169.4), out=q(169.4 + 1.9), asrc=q(316.05), kind="talk", focal=[50, 50], move="push", tin="whip", id="cut0"),
        dict(src=q(204.5), out=q(204.5 + 1.1), asrc=q(317.95), kind="talk", focal=[55, 55], move="push", tin="punch", id="cut1"),
        dict(src=q(198.8), out=q(198.8 + 2.8), asrc=q(319.05), kind="talk", focal=[45, 45], move="push", tin="punch", id="cut2"),
        dict(src=q(302.6), out=q(302.6 + 0.8), asrc=q(321.85), kind="talk", focal=[50, 50], move="pull", tin="punch", id="cut3"),
    ]
    # CTA — Guillaume: results on LinkedIn
    shots += talk(136.72, 141.25, prefix="cta", focal=(60, 38), zooms=(1.0, 1.12), splits=(139.20,))
    shots[-2]["tin"] = "whip"

    def post(c):
        o, sfx = [], []
        end_t = c.end(shots[-1]["id"])
        o.append(dict(type="headline", start=0.0, dur=c.t("ceo0") - 0.02, kicker="Conférence · SEO & GEO Summit", kickerAt=0.0,
                      lines=[dict(text="ChatGPT préfère", style="sora", fx="slam", at=0.25, stagger=0.12),
                             dict(text="vos **concurrents** !", style="sora", fx="slam", at=1.2, stagger=0.12)],
                      sub="Ce qu'on a appris de l'étude", subAt=2.4))
        sfx += [(0.25, "impact-bass-1", 0.45), (1.2, "whoosh-short", 0.35)]
        o.append(dict(type="lower", start=c.t("ceo0") + 0.25, dur=3.6, name="Guillaume Fraybin", role="CEO · LLM Monitor"))
        sfx.append((c.t("ceo0") + 0.25, "click-soft", 0.3))
        # insight 1
        o.append(dict(type="chapter", start=c.t("i1card"), dur=1.85, num="01", title="Votre site ne suffit pas"))
        sfx.append((c.t("i1card"), "whoosh-cinematic", 0.28))
        o.append(dict(type="stat", start=c.t("i1") + 0.05, dur=c.end("i1") - c.t("i1") - 0.05, value=11, pos="bottom",
                      kicker="Nos données · ChatGPT, Claude, Gemini",
                      text="des sources citées par l'IA pour recommander une marque sont son propre site.",
                      foot="Environ <b>1 fois sur 9</b>.", footAt=1.5))
        sfx += [(c.t("i1") + 0.05, "whoosh", 0.28), (c.t("i1") + 0.35, "sparkle", 0.25)]
        o.append(dict(type="chips", start=c.t("todo0"), dur=c.end("todo3") - c.t("todo0"), kicker="À faire",
                      title="Votre visibilité IA se gagne **chez** **les** **autres**",
                      items=[dict(icon="newspaper", text="Médias"), dict(icon="star", text="Sites d'avis"),
                             dict(icon="scan-search", text="Comparateurs"), dict(icon="store", text="Distributeurs")],
                      itemsAt=1.0, itemStagger=0.35))
        for i in range(4):
            sfx.append((c.t("todo0") + 1.0 + i * 0.35, "pop", 0.25))
        # insight 2
        o.append(dict(type="chapter", start=c.t("i2card"), dur=1.75, num="02", title="Les réponses bougent vite"))
        sfx.append((c.t("i2card"), "whoosh-cinematic", 0.28))
        tq = c.word("quatre", 200)
        o.append(dict(type="counter", start=tq - 0.35, dur=c.end("i2b") - tq + 0.3, value=4, prefix="", suffix=" jours",
                      kicker="Guillaume Fraybin", label="« Tous les quatre jours, ça change. »", pos="center", countDur=0.6))
        sfx.append((tq - 0.35, "ping", 0.25))
        # insight 3
        o.append(dict(type="chapter", start=c.t("i3card"), dur=1.75, num="03", title="ChatGPT reste la porte d'entrée"))
        sfx.append((c.t("i3card"), "whoosh-cinematic", 0.28))
        tl = c.word("ChatGPT", 258)
        o.append(dict(type="logos", start=tl, dur=c.end("i3") - tl, items=[dict(name="ChatGPT", logo="chatgpt", t=tl)]))
        sfx.append((tl, "pop", 0.3))
        # social proof
        o.append(dict(type="lower", start=c.t("cut0") + 0.1, dur=3.2, name="Maxence Antao", role="Market Connect"))
        # CTA
        tli = c.word("LinkedIn", 137)
        o.append(dict(type="callout", start=tli - 0.3, dur=c.end(shots[-1]["id"]) - tli + 0.1, icon="bell", text="Les résultats sur LinkedIn", pos="right"))
        sfx.append((tli - 0.3, "notification", 0.22))
        o.append(dict(type="end", start=end_t, dur=6.0, tagline="Pilotez votre visibilité dans les **IA.**",
                      cta="Les résultats de l'étude sur LinkedIn", url="llm-monitor.com"))
        sfx += [(end_t - 0.05, "impact-bass-2", 0.45), (end_t + 1.25, "chime", 0.26)]
        flashes = [c.t("ceo0")]
        c.section("Accroche", "hook0", "« ChatGPT préfère vos concurrents ! » sur la salle de conférence", "headline slam")
        c.section("Guillaume", "ceo0", "Le CEO présente l'étude menée sur trois mois", "lower third")
        c.section("01 Votre site ne suffit pas", "i1card", "La slide 11 %, puis la liste « À faire »", "chapter, stat count-up, chips")
        c.section("02 Les réponses bougent vite", "i2card", "« Tous les quatre jours, ça change »", "chapter, counter")
        c.section("03 ChatGPT reste la porte d'entrée", "i3card", "« Ma maman est sur ChatGPT en version gratuite »", "chapter, logo")
        c.section("Le public", "cut0", "Maxence : une salle qui prend des notes et photographie les slides", "cutaways")
        c.section("Appel à l'action", "cta0", "Les résultats complets sur LinkedIn", "callout, end card")
        return o, sfx, flashes, []

    def music(c, duration):
        end_t = c.end(shots[-1]["id"])
        S = [
            [0.0, c.t("ceo0"), 2],
            [c.t("ceo0"), c.t("i1card"), 0],
            [c.t("i1card"), c.t("todo0"), 1],
            [c.t("todo0"), c.t("i2card"), 2],
            [c.t("i2card"), c.t("cut0"), 1],
            [c.t("cut0"), c.t("cta0"), 2],
            [c.t("cta0"), end_t, 1],
            [end_t, duration, 3],
        ]
        return {"style": "insights", "duration": duration, "sections": S,
                "impacts": [0.25, end_t], "risers": [end_t], "stops": [], "fills": [], "fade_out": 2.5}

    return dict(
        folder="v3-insights", title="LLM Monitor au SEO & GEO Summit — les enseignements", W=1080, H=1080, css=CSS_SQUARE,
        message="Ce que la conférence LLM Monitor a appris sur ChatGPT et la visibilité des marques.",
        arc="Accroche → Contexte → 3 enseignements → Preuve sociale → Appel à l'action → Carton de fin",
        shots=shots, post=post, music=music, tail=6.0, cap_chars=24, cap_words=4,
        cap_overrides={237.74: "des", 140.6: "À", 316.12: "Il"}, music_level=0.75, music_duck=0.14, ambience=0.6,
    )


VERSIONS = {"v1": v1, "v2": v2, "v3": v3}
