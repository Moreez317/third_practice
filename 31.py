import struct

# format characters
FC = {
    'b': 1,  # int8
    'H': 2,  # uint16
    'i': 4,  # int32
    'I': 4,  # uint32
    'q': 8,  # int64
    'Q': 8,  # uint64
    's': 1,  # char[]
    'd': 8,  # double
    'c': 1,  # uint8
    'h': 2,  # int16
    'f': 4   # float
}


def pattern_to_length(pattern):
    length = 0
    pattern_parts = pattern.split(' ')

    for i in range(1, len(pattern_parts)):
        part = pattern_parts[i]

        if len(part) == 1:
            length += FC[part]
        else:
            length += int(part[0]) * FC[part[1]]

    return length


def process_structure(data, index, pattern, name):
    data_unpacked = struct.unpack(pattern, data[index:index + pattern_to_length(pattern)])

    pre_result = []

    for i in range(len(data_unpacked)):
        to_append = data_unpacked[i]

        if name == 'A':
            if i == 0:
                to_append = [data_unpacked[i]]

            if i == 1:
                pre_result[-1].append(data_unpacked[i])
                continue

            if i == 3:
                to_append = [data_unpacked[i]]

            if i == 4:
                pre_result[-1].append(data_unpacked[i])
                continue

            if i == 5:
                to_append = [data_unpacked[i]]

            if 6 <= i <= 10:
                if i == 8:
                    array_size = data_unpacked[i]
                    array_index = data_unpacked[i + 1]

                    to_append_bytes = struct.unpack(f'>{array_size}d', data[array_index:array_index + (array_size * FC['d'])])

                    pre_result[-1].append(list(to_append_bytes))
                    continue

                if i == 9:
                    continue

                pre_result[-1].append(data_unpacked[i])
                continue

            if i == 12:
                to_append = [data_unpacked[i]]

            if 13 <= i <= 16:
                pre_result[-1].append(data_unpacked[i])
                continue

        if name == 'B':
            if i == 0:
                to_append = data_unpacked[i].decode('utf-8')

            if i > 0:
                to_append = int.from_bytes(data_unpacked[i], "big")

        pre_result.append(to_append)

    result = {}

    for i0 in range(len(pre_result)):
        result[f'{name}{i0 + 1}'] = pre_result[i0]

    return result


def f31(data):
    pattern_a = '> I I ' \
                'i ' \
                'I d ' \
                'q H b I H c ' \
                'b 5Q d h'
    position_a = 5  # omit signature
    a = process_structure(data, position_a, pattern_a, 'A')

    pattern_b = '> 4s c c'
    position_b = a['A1'][1]
    length_b = a['A1'][0]
    a['A1'] = []

    for n in range(length_b):
        if n > 0:
            position_b += pattern_to_length(pattern_b)
        a['A1'].append(process_structure(data, position_b, pattern_b, 'B'))

    pattern_d = '> h f I i q H'
    position_d = a['A3'][0]
    d = process_structure(data, position_d, pattern_d, 'D')

    c1 = d
    c2 = a['A3'][1]
    a['A3'] = {'C1': c1, 'C2': c2}

    e = {}
    for i in range(len(a['A4'])):
        if i == 4:
            e[f'E{i + 1}'] = int.from_bytes(a['A4'][i], "big")
            continue

        e[f'E{i + 1}'] = a['A4'][i]

    a['A4'] = e

    return a

