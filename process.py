import os
import yaml
import sys

from wand.image import Image
from wand.font import Font
from wand.color import Color

from colorama import Fore


def generate_framed_screenshot(output, text, color, font, size, bg, frm, scrn, offsets, text_offsets):
    font = Font(path=font, size=size, color=Color(color))
    offset_x = offsets["x"]
    offset_y = offsets["y"]
    offset_top = offsets["top"]

    text_left = text_offsets["left"]
    text_right = text_offsets["right"]
    text_top = text_offsets["top"]
    text_bottom = text_offsets["bottom"]

    with Image(filename=bg) as background, Image(filename=frm) as frame, Image(filename=scrn) as screen:
        background.crop(0, 0, width=screen.width, height=screen.height)
        frame.composite(screen, left=offset_x, top=offset_y)
        frame.transform(resize=str(screen.width) + 'x')
        background.composite(frame, left=0, top=offset_top)

        text_width = screen.width - text_left - text_right
        text_height = offset_top - text_top - text_bottom
        background.caption(text=text,
                           left=text_left,
                           top=text_top,
                           width=text_width,
                           height=text_height,
                           font=font,
                           gravity='center')
        background.save(filename=output)
        print(Fore.GREEN + '[OK] Screenshot ' + scrn + ' framed as ' + output)


def value_or_default(arr, key):
    for obj in arr:
        if key in obj:
            return obj[key]
    for obj in arr:
        if 'default' in obj:
            return obj['default']
    return None


base_dir = sys.argv[1] if len(sys.argv) > 1 is not None else '.'

with open(base_dir + '/config.yml', 'r') as config:
    try:
        config = yaml.load(config)
    except yaml.YAMLError as exc:
        print(exc)

with open('devices.yml', 'r') as conf_devices:
    try:
        conf_devices = yaml.load(conf_devices)
    except yaml.YAMLError as exc:
        print(exc)

# Each dir is locale
locales = next(os.walk(base_dir))[1]
for locale in locales:
    screenshots = next(os.walk(base_dir + '/' + locale))[2]
    for screenshot in screenshots:
        if '_framed' in screenshot:
            continue

        splitted = screenshot.split('-')
        if len(splitted) < 3:
            print(Fore.RED + '[FAIL] Invalid screenshot name for ' + screenshot)
            continue

        name = splitted[-2]
        devices = [x for x in conf_devices if x["device"] == '-'.join(splitted[:-2])]
        if len(devices) == 0:
            print(Fore.RED + '[FAIL] No devices for ' + screenshot)
            continue
        if len(devices) > 1:
            print(Fore.RED + '[FAIL] More than one device for ' + screenshot)
            continue

        # Get params
        # First level - device size (default)
        # Second level - locales (default)
        matched_presets = [x for x in config if x["name"] == name]
        if len(matched_presets) == 0:
            print(Fore.RED + '[FAIL] No presets for ' + screenshot)
            continue
        preset = matched_presets[0]
        device = devices[0]

        font = base_dir + '/' + value_or_default(value_or_default(preset["caption"]["font"], device["size"]), locale)
        size = value_or_default(value_or_default(preset["caption"]["size"], device["size"]), locale)
        text = value_or_default(value_or_default(preset["caption"]["text"], device["size"]), locale)
        color = value_or_default(value_or_default(preset["caption"]["color"], device["size"]), locale)
        bg = base_dir + '/' + value_or_default(value_or_default(preset["background"], device["size"]), locale)
        text_offsets = value_or_default(value_or_default(preset["caption"]["offsets"], device["size"]), locale)

        filename = base_dir + '/' + locale + '/' + screenshot
        new_filename = base_dir + '/' + locale + '/' + "{}_{}_{}_framed.{}".format(locale, device["device"], name, screenshot.split('.')[-1])
        generate_framed_screenshot(output=new_filename,
                                   text=text,
                                   color=color,
                                   font=font,
                                   size=size,
                                   bg=bg,
                                   frm=device["frame"],
                                   scrn=filename,
                                   offsets=device["offsets"],
                                   text_offsets=text_offsets)
