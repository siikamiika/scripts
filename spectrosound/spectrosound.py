#!/usr/bin/env python3
from PIL import Image
import numpy as np
from scipy.signal import istft
from scipy.io import wavfile

"""
[y][x][color]
[r, g, b]

bg: 201 201 201

bg turning blue:
    r   g   b
    194 198 204
    180 192 207
    121 171 237
    118 170 239
    108 164 245

blue turning red:
    r   g   b
    131 145 241
    150 128 238
    193  92 230
    226  65 221
    236  55 131
    237  55 125
    240  51 100
    242  49  78
    244  48  61

red turning white:
    r   g   b
    246  51  51
    246  66  66
    246 142 142
    246 186 186
    246 193 193
    246 244 244
"""

FILENAME = './2019-07-21_17-10-20.png'

L_0K = 36, 657
L_20K = 36, 66

R_0K = 30, 895
R_20K = 30, 487

SILENT = np.array([201, 201, 201])
# TODO more or less arbitrary, could check the exact colors from Audacity source
BLUE   = np.array([100, 150, 246])
RED    = np.array([246,  45,  45])
WHITE  = np.array([246, 246, 246])

COLORS = [SILENT, BLUE, RED, WHITE]

def pos_between_colors(pixel, color_from, color_to):
    scale = np.sum(np.abs(color_to - color_from))
    pos = np.sum(np.abs(color_to - pixel))
    return np.min([np.max([(1 - pos / scale), 0.0]), 1.0])

def color_to_volume(pixel):
    # close enough to background color, is silent
    if not np.any(np.abs(SILENT - pixel) > 2):
        return np.float(0)

    r, g, b = pixel
    color_transition_count = len(COLORS) - 1
    for i, color_from in enumerate(COLORS):
        if i >= len(COLORS) - 1:
            continue
        color_to = COLORS[i + 1]
        r_min, r_max = sorted(c[0] for c in [color_from, color_to])
        g_min, g_max = sorted(c[1] for c in [color_from, color_to])
        b_min, b_max = sorted(c[2] for c in [color_from, color_to])
        if r_min <= r <= r_max and g_min <= g <= g_max and b_min <= b <= b_max:
            volume = i * (1 / color_transition_count) + pos_between_colors(pixel, color_from, color_to) / color_transition_count
            if volume < 0.45:
                return np.float(0.0)
            return volume
    else:
        raise Exception(f"unexpected pixel: {pixel}")

def read_spectro_col(x, y, h, image):
    return np.array([color_to_volume(pix) for pix in image[y:y + h:, x]])

def convert_amplitudes(amplitudes):
    min_amp = np.min(amplitudes)
    max_amp = np.max(amplitudes)
    amplitudes = amplitudes - min_amp + 0.000001
    amplitudes = amplitudes / (max_amp - min_amp) * 65535 - 32767
    return amplitudes


image = np.array(Image.open(FILENAME))
x_top, y_top = L_20K
x_bot, y_bot = L_0K
times, amplitudes = istft(
    # np.rot90([read_spectro_col(x, y_top, y_bot - y_top, image) for x in range(50, 1500)]).repeat(2, axis=0),
    np.rot90([read_spectro_col(x, y_top, y_bot - y_top, image) for x in range(36, 500)]),
)
amplitudes = convert_amplitudes(amplitudes)
wavfile.write(
    'test.wav',
    40000,
    amplitudes.astype('int16')
)

# for coord in '729,144; 730,146; 730,148; 151,729; 731,150; 729,186; 755,216; 811,209; 857,208; 858,201; 868,194; 878,194'.split('; '):
#     y, x = map(int, coord.split(','))
#     pixel = image[y][x]
#     print(pixel, color_to_volume(pixel))
