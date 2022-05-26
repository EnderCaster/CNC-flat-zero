#!/usr/bin/env python3
# -*- coding:utf8 -*-
import argparse

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--x-length", help="X向长度(mm)", type=int)
arg_parser.add_argument("--y-length", help="Y向长度(mm)", type=int)

arg_parser.add_argument("--line-width", default=1.5,
                        help="行距，一般为刀尖宽度/2", type=float)
arg_parser.add_argument("--zero-pos", default="LT",
                        help="对刀点：LT=左上，RT=左下，C=中心，LB=左下，RB=右下")
arg_parser.add_argument("--speed", default=500, help="行进速率F", type=int)
arg_parser.add_argument("--safe-z", default=10, help="安全高度", type=int)

args = arg_parser.parse_args()
if args.x_length <= 0 or args.y_length <= 0 or args.line_width <= 0.0:
    print("xy与行距均需大于0")

if args.zero_pos not in ["LT", "RT", "C", "LB", "RB"]:
    print("检测到不支持的对刀点，已将对刀点重置为左下")
    args.zero_pos = "LT"
file_name = "flat_zero_{}_{}_{}_{}_{}.gcode".format(args.x_length, args.y_length,
                                                    args.line_width, args.zero_pos, args.speed)


code_header = """
G0 Z{}
G0 X{} Y{}
G0 Z0
"""
min_x = 0
min_y = 0 - args.y_length
max_x = args.x_length
max_y = 0
if args.zero_pos == "RT":
    min_x = 0 - args.x_length
    min_y = 0-args.y_length
    max_x = 0
    max_y = 0
elif args.zero_pos == "C":
    min_x = 0 - args.x_length/2
    min_y = 0-args.y_length/2
    max_x = args.x_length/2
    max_y = args.y_length/2
elif args.zero_pos == "LB":
    min_x = 0
    min_y = 0
    max_x = args.x_length
    max_y = args.y_length
elif args.zero_pos == "RB":
    min_x = 0 - args.x_length
    min_y = 0
    max_x = 0
    max_y = args.y_length

code_header = code_header.format(args.safe_z, min_x, min_y)
code = ""
code = code+code_header
current_y = min_y
next_x = min_x
while current_y <= max_y:
    code = code+"G1 X{} F{} \n".format(next_x, args.speed)
    next_x = min_x if next_x == max_x else max_x
    next_y = current_y+args.line_width if max_y - \
        current_y >= args.line_width else max_y
    code = code+"G1 Y{} F{} \n".format(next_y, args.speed)
    current_y = next_y if not current_y == next_y else current_y+1

with open(file_name, 'w') as source_file:
    source_file.write(code)
    source_file.flush()

print("保存为:{}".format(file_name))
