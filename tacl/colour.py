"""Module containing functions to generate distinct colours."""


def hsv_to_rgb(h, s, v):
    """Convert a colour specified in HSV (hue, saturation, value) to an
    RGB string.

    Based on the algorithm at
    https://en.wikipedia.org/wiki/HSL_and_HSV#Converting_to_RGB

    :param h: hue, a value between 0 and 1
    :type h: `int`
    :param s: saturation, a value between 0 and 1
    :type s: `int`
    :param v: value, a value between 0 and 1
    :type v: `int`
    :rtype: `str`

    """
    c = v * s
    hp = h*6
    x = c * (1 - abs(hp % 2 - 1))
    if hp < 1:
        r, g, b = c, x, 0
    elif hp < 2:
        r, g, b = x, c, 0
    elif hp < 3:
        r, g, b = 0, c, x
    elif hp < 4:
        r, g, b = 0, x, c
    elif hp < 5:
        r, g, b = x, 0, c
    elif hp < 6:
        r, g, b = c, 0, x
    m = v - c
    colour = (r + m, g + m, b + m)
    return 'rgb({}, {}, {})'.format(*[round(value * 255) for value in colour])


def generate_colours(n):
    """Return a list of `n` distinct colours, each represented as an RGB
    string suitable for use in CSS.

    Based on the code at
    http://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/

    :param n: number of colours to generate
    :type n: `int`
    :rtype: `list` of `str`

    """
    colours = []
    golden_ratio_conjugate = 0.618033988749895
    h = 0.8  # Initial hue
    s = 0.7  # Fixed saturation
    v = 0.95  # Fixed value
    for i in range(n):
        h += golden_ratio_conjugate
        h %= 1
        colours.append(hsv_to_rgb(h, s, v))
    return colours
