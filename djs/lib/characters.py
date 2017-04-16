#!/usr/bin/env python3

CHINESE_NUMBERS = '一二三四五六七八九'

# stop: used as a space and after list index (see LIST_1)
STOP = 9473
# delimiter: separate entry and headwords or readings
# format: entry + DELIMITER + hw or reading (+ DELIMITER + hw or reading ...)
DELIMITER = 9475
# --------------------------------------
# TODO
# 57360 alla breve
# 57363 ň
# 57366 ゑ
BRACKET_SQ_OPEN = 57456
BRACKET_SQ_CLOSE = 57457
# --------------------------------------
# [一] (bold bg, newline after, big list of lists of lists)
NUM_BOLD_1 = 57458
NUM_BOLD_END = 57466 # 9
# ---
# [一] (light bg)
NUM_LIGHT_1 = 57467
NUM_LIGHT_END = 57476 # 10
# --------------------------------------
# under list (see LIST_1), not numbered
SUBLIST_1 = 57497
SUBLIST_END = 57516 # 20
# --------------------------------------
# on: before katakana that means on'yomi (ON + kata) ［音］
ON = 57524
# kun: before hiragana that means kun'yomi (KUN + hira) ［訓］
KUN = 57525
# ［文］
BUN = 57526
# （慣）
NARE = 57527
# （呉）
KURE = 57528
# （漢）
KAN = 57529
# （唐）
TOU = 57530
# xref: XREF + word + [$|STOP]
XREF = 57532
# ant: ANT + word + [$|STOP|。]
ANT = 57533
# [下接句]
KASETUKU = 57534
# [下接語]
KASETUGO = 57535
# [可能]
KANOU = 57536
# ［難読］
NANDOKU = 57537
# [派生]
HASEI = 57538
# [補説]
HASETU = 57539
# ［名のり］
NANORI = 57540
# [用法]
YOUHOU = 57541
# ［歌枕］
UTAMAKURA = 57543
# list item: LIST_N + STOP
# under bold number, see NUM_BOLD_1
LIST_1 = 57545
LIST_END = 57584 # 40
# redirect to another entry (-->)
REDIR = 57585
# --------------------------------------
# symbols used in indexes that need processing
# ×, skippable
NON_JOUYOU = 215
# ‐, needed for indexing, used for shortening indexes
# アーカート城┃アーカート‐じょう┃‐ジヤウ
# 藤子不二雄Ⓐ┃ふじこ‐ふじお‐エー┃ふぢこフジを‐
DASH = 8208
# ―, skippable
HORIZONTAL_BAR = 8213
# …, start…end
FROM_TO = 8230
# ▽, skippable
NON_JOUYOU_READING = 9661
# 
