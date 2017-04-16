#!/usr/bin/env python3

import sys
import csv
from bitarray import bitarray

def decrypt_char(input_char):

    byt = bytearray(input_char.encode('utf-8'))
    num = len(byt)

    if len(byt) == 1:
        return input_char

    b2 = byt[num - 1]
    b2 = ~b2
    b2 = ((b2 & 56) >> 3) + ((b2 & 7) << 3) + 128
    byt[num - 1] = b2

    if 2 < num:
        bit_array = bitarray(endian='little')
        bit_array.frombytes(bytes([byt[num - 2]]))
        num2 = 0
        if bit_array[7]:
            num2 = 128
        if bit_array[6]:
            num2 += 64
        if bit_array[5]:
            num2 += 32
        if bit_array[0]:
            num2 += 16
        if bit_array[1]:
            num2 += 8
        if bit_array[2]:
            num2 += 4
        if bit_array[3]:
            num2 += 2
        if bit_array[4]:
            num2 += 1
        byt[num - 2] = num2

    return bytes(byt).decode('utf-8')

def decrypt_text(input_text):
    output = []
    for c in input_text:
        output.append(decrypt_char(c))
    return ''.join(output)

def main():
    for filename in sys.argv[1:]:
        print(filename)
        input_file = open(filename, 'r', encoding='utf-8')
        open(filename + '.out', 'w').close()
        output_file = open(filename + '.out', 'a', encoding='utf-8')
        output_writer = csv.writer(output_file)
        for row in csv.reader(input_file):
            if len(row) != 14:
                print(row)
            new_row = []
            for data in row[:-2]:
                new_row.append(decrypt_text(data))
            # row = row.replace(' ', '')
            output_writer.writerow(new_row)

        output_file.close()
        input_file.close()

if __name__ == '__main__':
    main()
