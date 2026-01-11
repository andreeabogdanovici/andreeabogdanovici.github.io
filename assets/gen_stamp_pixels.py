import random
import struct
import sys
import zlib


def parse_png_read(path):
  data = open(path, 'rb').read()
  if data[:8] != b'\x89PNG\r\n\x1a\n':
    raise SystemExit('not png')

  pos = 8
  width = None
  height = None
  bit_depth = None
  color_type = None
  idat = []

  while pos < len(data):
    length = struct.unpack('>I', data[pos:pos + 4])[0]
    kind = data[pos + 4:pos + 8]
    chunk = data[pos + 8:pos + 8 + length]
    pos += 12 + length

    if kind == b'IHDR':
      width, height, bit_depth, color_type = struct.unpack('>IIBB3x', chunk[:13])
    elif kind == b'IDAT':
      idat.append(chunk)
    elif kind == b'IEND':
      break

  if bit_depth != 8:
    raise SystemExit('unsupported bit depth')
  if color_type not in (2, 6):
    raise SystemExit('unsupported color type')

  raw = zlib.decompress(b''.join(idat))
  bpp = 3 if color_type == 2 else 4
  stride = width * bpp

  def paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
      return a
    if pb <= pc:
      return b
    return c

  out = []
  i = 0
  prev = [0] * stride
  for _ in range(height):
    ft = raw[i]
    i += 1
    row = list(raw[i:i + stride])
    i += stride
    if ft == 0:
      pass
    elif ft == 1:
      for x in range(stride):
        left = row[x - bpp] if x >= bpp else 0
        row[x] = (row[x] + left) & 255
    elif ft == 2:
      for x in range(stride):
        row[x] = (row[x] + prev[x]) & 255
    elif ft == 3:
      for x in range(stride):
        left = row[x - bpp] if x >= bpp else 0
        up = prev[x]
        row[x] = (row[x] + ((left + up) >> 1)) & 255
    elif ft == 4:
      for x in range(stride):
        left = row[x - bpp] if x >= bpp else 0
        up = prev[x]
        up_left = prev[x - bpp] if x >= bpp else 0
        row[x] = (row[x] + paeth(left, up, up_left)) & 255
    else:
      raise SystemExit('unsupported filter')

    prev = row
    if color_type == 2:
      for x in range(0, stride, 3):
        out.append((row[x], row[x + 1], row[x + 2], 255))
    else:
      for x in range(0, stride, 4):
        out.append((row[x], row[x + 1], row[x + 2], row[x + 3]))

  return width, height, out


def downsample_avg(width, height, pixels, out_w, out_h, bg=(247, 241, 228)):
  out = []
  for oy in range(out_h):
    y0 = oy * height / out_h
    y1 = (oy + 1) * height / out_h
    iy0 = int(y0)
    iy1 = int(y1) + 1
    for ox in range(out_w):
      x0 = ox * width / out_w
      x1 = (ox + 1) * width / out_w
      ix0 = int(x0)
      ix1 = int(x1) + 1

      rs = gs = bs = n = 0
      for sy in range(iy0, iy1):
        if sy < 0 or sy >= height:
          continue
        for sx in range(ix0, ix1):
          if sx < 0 or sx >= width:
            continue
          r, g, b, a = pixels[sy * width + sx]
          if a != 255:
            ar = a / 255.0
            r = int(r * ar + bg[0] * (1 - ar))
            g = int(g * ar + bg[1] * (1 - ar))
            b = int(b * ar + bg[2] * (1 - ar))
          rs += r
          gs += g
          bs += b
          n += 1
      out.append((rs // n, gs // n, bs // n))
  return out


def kmeans_palette(pixels, k, iters, seed=9228):
  random.seed(seed)
  centers = [list(pixels[random.randrange(0, len(pixels))]) for _ in range(k)]
  for _ in range(iters):
    buckets = [[] for _ in range(k)]
    for r, g, b in pixels:
      best_i = 0
      best_d = 10**18
      for i, (cr, cg, cb) in enumerate(centers):
        d = (r - cr) * (r - cr) + (g - cg) * (g - cg) + (b - cb) * (b - cb)
        if d < best_d:
          best_d = d
          best_i = i
      buckets[best_i].append((r, g, b))
    for i in range(k):
      if not buckets[i]:
        centers[i] = list(pixels[random.randrange(0, len(pixels))])
        continue
      rs = sum(p[0] for p in buckets[i])
      gs = sum(p[1] for p in buckets[i])
      bs = sum(p[2] for p in buckets[i])
      n = len(buckets[i])
      centers[i] = [rs // n, gs // n, bs // n]
  centers = [tuple(c) for c in centers]

  def lum(c):
    r, g, b = c
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

  return sorted(centers, key=lum)


def assign_indices(pixels, palette):
  out = []
  for r, g, b in pixels:
    best_i = 0
    best_d = 10**18
    for i, (cr, cg, cb) in enumerate(palette):
      d = (r - cr) * (r - cr) + (g - cg) * (g - cg) + (b - cb) * (b - cb)
      if d < best_d:
        best_d = d
        best_i = i
    out.append(best_i)
  return out


def hex_color(c):
  return '#%02x%02x%02x' % c


def main():
  path = sys.argv[1]
  out_w = int(sys.argv[2])
  out_h = int(sys.argv[3])
  k = int(sys.argv[4])
  w, h, px = parse_png_read(path)
  small = downsample_avg(w, h, px, out_w, out_h)
  palette = kmeans_palette(small, k=k, iters=9)
  idx = assign_indices(small, palette)

  print('CSS_START')
  print(f'.stamp-pixels {{ display: grid; grid-template-columns: repeat({out_w}, 1fr); grid-template-rows: repeat({out_h}, 1fr); width: 100%; height: 100%; }}')
  print('.stamp-pixels .px { width: 100%; height: 100%; }')
  for i, c in enumerate(palette):
    print(f'.stamp-pixels .p{i} {{ background: {hex_color(c)}; }}')
  print('CSS_END')

  print('HTML_START')
  parts = []
  for i in idx:
    parts.append(f"<i class='px p{i}'></i>")
  print(''.join(parts))
  print('HTML_END')


if __name__ == '__main__':
  main()
