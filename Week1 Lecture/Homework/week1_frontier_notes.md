# Week 1 — the frontier (Oier)

Companion to `week1_frontier.ipynb` and to the post in `posts/week1.html`.
Alvaro's `week1_post_answers.md` covers the centre of the network; this covers the edge.
The two are meant to be read as one week.

---

## The question

> **What does it take to be inside Wikipedia's Marvel universe?**

The category says 303 characters belong. The link structure disagrees: it leaves 26 of
them outside entirely, and holds another 18 by a single thread.

## What it finds

1. **Nineteen components, and nothing in between.** One continent (277), one island
   (9), seventeen people in the water. No cluster of three, no pair holding hands.
2. **The island is a narrative border, not a data glitch.** All nine are *Strikeforce:
   Morituri* characters (1986–89, its own continuity). Their articles carry 21–76
   `[[links]]` each in the wiki-source — they link out plenty — but the count of links
   to any roster member outside the island is **0, nine times out of nine**.
3. **The 17 castaways are four kinds of outsider**, not one: arrived from another
   publisher (Miracleman, Solarman, Super Rabbit, Sean and Chris), born on screen
   (Baymax, Yo-Yo Rodriguez), obscure 1940s–50s (Breeze Barton, Father Time, Black Fox,
   Happy Sam Sawyer), and a scattered rest.
4. **"They are stubs" is mostly right, and that is the interesting part.** Article size
   and degree correlate at ρ = 0.82; the castaways' median article is 6.7 kB against
   18.0 kB for connected characters. But Miracleman (62 kB, 440 links in source, zero
   landing in the category) and Baymax (24 kB, 120, zero) do not fit — connected
   characters in that size band have a median degree of 11. Length explains the rim; it
   does not explain the doorway.
5. **The surprise: the rim reaches in, the centre never reaches back.** Of the 18
   pendants, 15 only link out, 1 is only linked to, 2 are reciprocal; five hold on to
   Spider-Man alone. Generalised as *polarity* = (in − out)/(in + out), the median rises
   from −0.9 at degree 1 and only turns positive above degree 20.
6. **The snapshot survives re-harvesting.** Re-pulled the wiki-source for four articles
   and re-derived their edges: Spider-Man 9/9, Toxyn 2/2, Miracleman 0/0, Baymax 0/0.

## How it meets Alvaro's half

| | Alvaro | Oier |
|---|---|---|
| Question | who gets talked about vs who does the talking | who is left outside, and why |
| Unit of attention | the hubs | the rim: island, castaways, pendants |
| Figures | six interactive Plotly, light + dark HTML | four static PNG, embedded in the post |
| Shared finding | in-degree is fame, out-degree is authorship | the same asymmetry, measured from the edge |

The overlap is one idea — the in/out asymmetry — reached from opposite ends. If the two
halves become a single post, that is the hinge, and it should be explained once.

## One thing to agree on before publishing: which "average degree"

The same file gives two different constants depending on the convention, and both of us
computed a correct one:

| | directed | undirected (reciprocal pairs collapsed) |
|---|---|---|
| edges | 1,784 | 1,434 (350 pairs link both ways) |
| density | 1.95 % | 3.13 % |
| average degree | ⟨k_in⟩ = 5.89 | ⟨k⟩ = 9.47 |

`analysis_week1.py` prints both, labelled. The post should quote one and say which —
Alvaro's notebook uses the undirected one, so that is the one to keep. Neither number
appears in the current post, so there is nothing to fix there yet.

## Files

```
Week1 Lecture/Homework/
  week1_frontier.ipynb    the narrative: components, island, castaways, polarity, API checks
  analysis_week1.py       every figure and every number the post quotes
  wiki.py                 Wikipedia API client: User-Agent, 429 back-off, disk cache
Data/                     the frozen week-1 release
assets/img/week1_*.png    the four figures, embedded by the post
posts/week1.html          the post
index.html                home, with the week-1 card pointed at it
```

Run order: `python analysis_week1.py --wiki` once (fills `Data/wiki_cache.json`), then
`python analysis_week1.py` for everything else. Figures land in `assets/img/`. The cache
is deliberately not committed; `--wiki` rebuilds it in about two minutes.

## Claims and where each comes from

- 19 components, 277 / 9 / 17×1 — snapshot
- island: 22 internal links, 0 leaving; 21–76 `[[links]]` per source article — API
- article sizes: castaways 6.7 kB, island 4.9 kB, connected 18.0 kB — API
- ρ = 0.82 between article size and degree — API
- Miracleman 62 kB / 440 links / 0; Baymax 24 kB / 120 / 0 — API
- connected articles of 20–70 kB have median degree 11 (n = 91) — both
- 18 pendants: 15 out-only, 1 in-only, 2 reciprocal; 5 anchored on Spider-Man — snapshot
- 92 characters (30 %) with degree ≤ 3 — snapshot
- Spider-Man: in-degree 106, 700 `[[links]]` in source, 9 landing in the category — both

## What changed outside this folder

Only `index.html`, three lines on the week-1 card:

```diff
-        <div class="sans post-card__theme">Degree Distributions</div>
+        <div class="sans post-card__theme">Components &amp; degree</div>
-        <div class="post-card__title">Mapping the Marvel Network</div>
-        <div class="post-card__dek">What we asked → what we did → one figure → what surprised us.</div>
+        <div class="post-card__title">The frontier of the Marvel universe</div>
+        <div class="post-card__dek">Seventeen characters with no links at all, an island of nine, and eighteen held by a single thread.</div>
-        <a class="week-cell__title" id="footer-w1-title" href="posts/week1.html">Networks</a>
+        <a class="week-cell__title" id="footer-w1-title" href="posts/week1.html">The frontier</a>
```

It is the only file another branch is likely to touch too. If Alvaro's branch lands
first, take his version and re-apply those three lines by hand.

## Still open

- Is this *the* week-1 post, or one of two halves? Written standalone on the course's
  spine (asked → did → figure → surprised), so it folds into a joint piece by demoting
  the `h2`s.
- Which average-degree convention the group publishes.
- The post is signed "Varmel", not by a person.
- Nobody has claimed the two housekeeping items the brief requires: the Teams link by
  Monday evening, and constructive criticism on another group's post.
