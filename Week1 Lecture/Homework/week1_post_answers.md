# Week 1 — answers for the post

---

## What we asked

> **In a network where every single link was typed by a human editor, who gets talked
> about and who does the talking? Are they ever the same character?**

We started with the three candidate questions in the template and they collapsed into that
one. "Who is linked to most / who links out most" is really the same question as "does the
in-degree have a heavy tail while the out-degree does not", because both are asking *who
creates the edge*. And the isolates turned out to be part of the same story, so they stayed
in as the last act instead of a separate question.

Since we are Marvel fans, we had a guess ready: the top of the list would be the movie
characters. That guess was half right, and the half that was wrong is the interesting half.

---

## The data (the missing stat)

| stat | value |
|---|---|
| Characters | **303** |
| Directed links | **1,784** |
| Isolates | **17** |
| **Giant component** | **277** (91% of the network) |

Extra numbers we use later in the post:

- Undirected pairs: **1,434** — because **350** pairs link both ways, and 1,784 − 350 = 1,434.
- Average degree ⟨k⟩ = 2m/n = **9.47**. Density = **3.1%**, out of 45,753 possible pairs.
- Components: **19** in total — one giant blob of 277, one island of 9, and 17 lonely nodes.
- Reciprocity: **39%** of directed links have a partner pointing back.
- The **strongly** connected core (everyone can reach everyone, following the arrows) is only
  **229** nodes. That is 48 fewer than the giant component. We did not expect the definition of
  "connected" to move 17% of the network.

---

## What we did

1. Loaded the snapshot as a `DiGraph` with **the node roster first**, then the edges. We
   checked `n = 303` on purpose, because loading only the edge list gives 286 and you would
   never notice.
2. Re-computed every number on the course page — n, m, both edge counts, ⟨k⟩, density,
   isolates, giant component — as an `assert` in the notebook. If the course page and our code
   disagree, the notebook refuses to run.
3. Plotted the degree distribution on linear axes first. It looked like a boring cliff. Then
   log–log with the `k+1` shift, and suddenly there was a straight line and a dot far out on
   the right.
4. **Dead end 1.** We first plotted the *undirected* degree distribution, because that is the
   default in our heads. It gave one mediocre curve and no story. Splitting in-degree from
   out-degree is what made the week click.
5. **Dead end 2.** Our first binning was `np.logspace` edges plus a histogram, exactly the
   recipe the course page warns about. Some bins held no integer at all and vanished on the log
   axis, and the binned curve did not sit on the raw dots at small k. We rewrote it with the
   scheme from the Goodies (width-1 bins up to k+1 = 7, then doubling bins, divided by the
   number of **integers** in the bin, drawn at the geometric mean) and now the two agree exactly
   where they must. That check is in the notebook.
6. Put both degrees of every character on one scatter plot, which is the figure that actually
   answers our question.
7. Drew the giant component under five layouts, then went looking for what the drawing throws
   away: the island and the isolates.
8. Added one thing the explorables do not have: the degree distribution of a **random** network
   with the same size and the same average degree, on the same axes. We wanted "heavy tail" to
   be a comparison and not just a word.

---

## The figures

**Fig. 1 — Degree distributions, against the random-graph baseline.**
*What you should see:* the in-degree dots fall on a rough straight line on log–log axes and
reach all the way to Spider-Man at k = 106, while the dotted curve — the same 303 characters
wired up at random — has already fallen off the bottom of the plot. Switch to out-degree and
the tail stops at 28, and the random curve is suddenly a decent description of it.
*What you should not conclude:* that we measured a power law. We only looked at a shape on a
log–log plot, which is exactly what the binning note tells you not to trust. No exponent, no
fit. The proper tool is the cumulative distribution, and that is week 2.

**Fig. 2 — Fame vs. authorship.** One dot per character, in-degree across, out-degree up, both
log axes with the k+1 shift, colour = number of two-way links, dashed diagonal = "gives as many
links as it gets".
*What you should see:* the cloud sits below the diagonal on the right. The famous characters
receive far more than they give.
*What you should not conclude:* that a dot's position is exact — dots are jittered by up to
±6% so the pile-up at small numbers stays countable. The tooltips carry the real integers.

**Fig. 3 — The same 277 characters under five layouts.** This one is in the post to make a
point rather than a measurement: flip through force, Kamada-Kawai, circle-by-degree, our
degree-onion and random, and notice that the only thing changing is how far apart things
*look*.

**Fig. 6 — The archipelago.** The 26 characters every network drawing forgets.

---

## Top of the tail

| Character | In-degree | Out-degree | Note |
|---|---|---|---|
| Spider-Man | 106 | 9 | A third of the network links to him. He links back to 9 of them, and all 9 are two-way. |
| Hulk | 64 | 10 | Same shape as Spider-Man, smaller. Famous and quiet. |
| Wolverine | 60 | 17 | The most linked-to X-Man. |
| Doctor Strange | 50 | 17 | The one that surprised us — above Deadpool and Black Panther. |
| Betsy Braddock | 7 | 28 | The out-degree champion of the whole network, and almost nobody links back. |

The second half of the table is the point: **Betsy Braddock is in this table for the opposite
reason to everyone above her.**

Our favourite pair in the whole dataset, though, is this one:

| Character | In | Out | Undirected degree |
|---|---|---|---|
| Luke Cage | 25 | 9 | **28** |
| Betsy Braddock | 7 | 28 | **28** |

Same undirected degree. Opposite characters. If you only look at the undirected network, these
two are the same node.

---

## What surprised us

**We expected the hubs to be the movie characters. Instead we found two different kinds of
hub, and only one of them is famous.**

Spider-Man, Hulk, Wolverine and Doctor Strange are hubs because *everyone else's article
mentions them*. Betsy Braddock, Cloak and Dagger (24 out) and Adam Warlock (22 out) are hubs
because *their own articles mention everyone else*. Both look big in a drawing where node size
is degree. They are not the same thing at all.

Once we saw it, the reason felt obvious, and it is a fact about how Wikipedia gets written
rather than a fact about Marvel. An out-link is **authored**: a person sits down and types
`[[Wolverine]]` into a page, so the number of out-links is capped by how much anyone is willing
to write. An in-link is **conferred**: every other article's editors deciding you are worth
mentioning, and nothing caps that. So the out-degree stops at 28 and the in-degree runs to 106.

**The alternative explanation we cannot rule out:** article length. Betsy Braddock has had many
identities (Psylocke, Captain Britain) and a very long article, and long articles have room for
more links. That would produce the same picture without any "fame" story. To separate the two
we would need article length or edit counts from the Wikipedia API, which we did not pull this
week. It is on the list.

Two smaller surprises:

- **The island of 9 is not a bug.** We assumed the 9-node component was a crawl artefact. All
  nine are the cast of *Strikeforce: Morituri*, a 1986 series in its own corner of the universe
  — three of them literally have "(Morituri)" in the page title. Radian sits in the middle,
  connected to 6 of the other 8. They link to each other 22 times and to the other 294
  characters **zero** times. A self-contained comic makes a self-contained component, and the
  network found that for us without anybody writing it into the data.
- **Baymax has degree 0.** So do Miracleman, Super Rabbit and Yo-Yo Rodriguez. A character can
  be famous everywhere else and invisible here, because this network measures exactly one
  thing: whether an editor typed your name into another character's page.

> **In this universe, fame is not something you have. It is something other people write about
> you.**

---

## Caveats

- The network is a snapshot of Wikipedia, not of the Marvel universe: an edge means an editor
  wrote a link, which tracks fame and article length as much as it tracks the story.
- Category membership is a human judgement call — who counts as a "superhero" is already an
  analysis decision made before we saw the data.
- **What our own method assumed away:**
  - We never separated *fame* from *article length*, which is the one alternative explanation
    that would break our headline (see above).
  - We fitted nothing. "Power-law-ish" is a shape we read off a log–log plot with a `k+1`
    shift, and both of those are reasons to distrust a slope. No exponent is claimed anywhere.
  - The layouts in Fig. 3 are not data. We put five of them in the post precisely so no reader
    takes one of them as a measurement.
  - The jitter in Fig. 2 is cosmetic. Exact integers are in the tooltips.
  - The *Strikeforce: Morituri* reading is our inference from nine page titles and their
    one-line descriptions. We did not check the nine articles one by one.
  - The category boundary hides the obvious counter-test: Doctor Doom and Magneto are not in
    this dataset, so "importance" here means importance among the characters Wikipedia labelled
    as superheroes.

---

# Appendix A — Exercise 1.4 · Reading the Marvel degree distributions

### 1. Only the in-degree looks like a power law. What does each degree *mean* here?

The two degrees are made by two different groups of people, and that is the whole answer.

- **In-degree = attention you receive.** Somebody else's article decided you were worth
  mentioning. You do not control it, there is no natural limit to it, and it grows every time
  anyone anywhere writes a new page. That is why it reaches 106.
- **Out-degree = work someone did on your page.** Each out-link had to be typed into *your*
  article by an editor. There is a ceiling: an article can only be so long and only so many
  people will edit it. That is why it stops at 28.

So in-degree is closest to *fame*, and out-degree is closest to *how much has been written about
you and how well-connected the writer wanted you to look*. Only one of the two can run away
with itself, and that is the one with the heavy tail.

### 2. Binning extends the power law. Was the extra range hiding, or did binning invent it?

It was hiding. The characters at k = 40, 60, 106 exist in the raw data — Spider-Man is a real
row in the file. The problem is that out in the tail every count is 0 or 1: there is one
character at 106 and nobody at 105 or 107, and a log axis cannot draw a zero. So raw P(k)
becomes a scatter of single dots with invisible gaps between them.

Binning does not add data. It averages over a range of k, so a bin containing "one character
somewhere between 64 and 127" has a small non-zero average instead of a mix of 1s and
undrawable 0s. The trend becomes visible.

What binning *does* hide is that each of those tail points is an average of about one event. It
makes the shape readable, not more certain.

### 3. What can go wrong with binning?

More than we expected. Reasons we now know:

1. **Forget to divide by the bin width** and a wide bin looks popular just for being wide. You
   manufacture a bump in the tail — or flatten a real slope.
2. **Bin where the data is dense** and you gain no reliability and lose your best measurements.
   Binning is for noise, and there is no noise at k = 1.
3. **Put the dot in the wrong place.** On a log axis a wide bin's point belongs at the
   *geometric* mean of what it covers ([8,16) sits at √(8·15) ≈ 10.95), not the arithmetic
   middle, which sits visibly right of centre and tilts the line.
4. **Fit a slope to it.** Do not. Not to binned data and not to a raw log–log plot either.
5. **The integer problem** (the subtle one). Degrees are whole numbers, and `np.logspace` edges
   do not care: with edges at 1, 1.3, 1.8, 2.4, 3.2 … some bins contain **no integer at all** —
   they plot as zero, or on a log axis just disappear — while a neighbour swallows **two**
   integers and looks twice as populated as it should. Dividing by the nominal width does not
   fix it; you have to divide by the number of integers the bin really holds, or make the edges
   integers in the first place.
6. **The first and last bin.** Round fractional edges to integers and two edges can come out
   equal: a zero-width bin, or the first two bins silently merged. At the top, the largest
   degree sits exactly on the final edge and, depending on which half-open convention the
   library uses, either drops out of the histogram or lands in a bin that has quietly merged
   with its neighbour. Spider-Man is precisely the kind of point you would lose that way.

Our fix is the course's: width-1 bins where the degrees are dense, powers of two after that, so
every bin holds a known set of integers, none is empty by construction, and the normalisation
is honest. And the test that catches everything: **where the bins are width 1, the binned curve
must be exactly equal to raw P(k)**. Ours is; the notebook asserts it.

### 4. Why is the undirected distribution the least useful of the three?

Because it adds two numbers that were produced by different mechanisms and then hides which is
which.

- **The low end.** An obscure character with zero in-links almost never has undirected degree 0,
  because their own article still links out to somebody. In our data **41 characters inside the
  giant component have in-degree 0** — nobody mentions them at all — and the undirected view
  gives every one of them a perfectly respectable degree. The "nobody has heard of me" signal is
  erased. The only characters who really reach 0 are the 17 who have neither in- nor out-links.
- **The tail.** It is dominated by in-degree, because in-degree is the bigger of the two numbers
  for anyone in the tail. Spider-Man's undirected degree is 106 = 97 one-way in-links + 9 two-way
  ties. So the tail looks like the in-degree tail with extra noise added, and you cannot tell
  from the curve which mechanism you are looking at.
- **And the killer:** Luke Cage (25 in / 9 out) and Betsy Braddock (7 in / 28 out) both have
  undirected degree 28. One number, two opposite characters.

A network scientist handed this network looks at in- and out-degree separately because the
direction is not a technical detail here — it *is* the finding.
