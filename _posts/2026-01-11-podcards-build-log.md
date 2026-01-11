---
layout: post
title: 'build log: podcards as ui'
---

A postcard is a constraint with edges. Fixed format. That was the point:))

A technical blog wants to bloat. Infinite scroll. 'Here’s what I did'.
Podcards flips the reflex: say what matters, then stop.

like old paper + ink.

## what was built

- the site background is a postcard rebuilt as pixels (HTML+CSS grid)
- the writing surface is a different paper layer (also pixel rebuilt)
- metadata it’s postal logic (stamps)
- posts don’t spill forever: the page stays fixed, text flows into columns and moves sideways (another postcard)

## why this way (and not the easy way)

### 1) the background isn’t an image, it’s material

 a grid of cells. pixelation makes it an object. 
 it reads as printed.

Cost: big DOM. cost paid in paint. (not a bug, a position.)

### 2) text gets its own paper

as the writing surface.

### 3) fixed page, sideways overflow

The text breaks into columns and is read horizontally. slices. notes. fragments.

### 4) metadata = stamp

Date and post title are round stamps, ink + ring.
Year archive uses the same.

### 5) typography *omg

- body: `Newsreader` + ink (pen blue)
- code: `IBM Plex Mono`
- stamps/titles: `Caveat`

## difficulties (aka reality)

- Jekyll/Liquid: nothing screams until it screams
- cache: Safari lies with a straight face (hard refresh or fight ghosts)
- layering: postcard + paper + stamps + columns = z-index as theology
- pixels: 'it’s CSS' doesn’t mean free; it means the bill is paid somewhere else


Podcards gives the blog pressure. Correspondence.
