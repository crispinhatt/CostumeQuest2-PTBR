#!/usr/bin/env python3
"""
dfpf_parser.py — Double Fine Pack Format (dfpf) v2 e v5
Extrator/reempacotador para Costume Quest 1 (v2) e Costume Quest 2 (v5)
Autor: crispinhatt | github.com/crispinhatt/CostumeQuest1-Traducao-PTBR
"""

import struct, zlib, os, sys

class Reader:
    def __init__(self, data):
        self.data = data
        self.pos  = 0
    def seek(self, off, whence=0):
        if whence == 0:   self.pos = off
        elif whence == 1: self.pos += off
        elif whence == 2: self.pos = len(self.data) + off
    def read_bytes(self, n):
        b = self.data[self.pos:self.pos+n]; self.pos += n; return b
    def read_dword(self):
        return struct.unpack('>I', self.read_bytes(4))[0]
    def read_qword(self):
        return struct.unpack('>Q', self.read_bytes(8))[0]
    def read_byte(self):
        b = self.data[self.pos]; self.pos += 1; return b
    def read_cstring(self, maxlen=512):
        end = self.data.find(b'\x00', self.pos, self.pos+maxlen+1)
        if end == -1: end = self.pos + maxlen
        s = self.data[self.pos:end]
        return s.decode('latin-1', errors='replace').strip()

def mask32(x): return x & 0xFFFFFFFF
def mask64(x): return x & 0xFFFFFFFFFFFFFFFF

def parse_v2(hdata):
    """dfpf versão 2 — Costume Quest 1"""
    r = Reader(hdata)
    assert hdata[:4] == b'dfpf' and hdata[4] == 2
    r.seek(8)
    file_ext_offset     = r.read_qword()
    name_dir_offset     = r.read_qword()
    file_ext_count      = r.read_dword(); r.seek(4,1)
    num_files           = r.read_dword(); r.seek(4,1); r.seek(4,1); r.seek(4,1); r.seek(8,1)
    file_records_offset = r.read_qword()
    r.seek(8,1); r.seek(8,1); r.seek(4,1); r.seek(4,1)

    SOR, files = 16, []
    for i in range(num_files):
        P = file_records_offset + SOR * i
        uncomp   = struct.unpack_from('>I', hdata, P)[0]   >> 9
        size     = ((struct.unpack_from('>I', hdata, P+5)[0]  << 1) & 0xFFFFFFFF) >> 10
        offset   = ((struct.unpack_from('>Q', hdata, P+7)[0]  << 7) & mask64(-1))  >> 34
        name_off = struct.unpack_from('>I', hdata, P+12)[0] >> 11
        type_idx = (struct.unpack_from('>I', hdata, P+14)[0] >> 20) & 0x7F
        comp     = hdata[P+15] & 15
        r.seek(name_dir_offset + name_off)
        fname = r.read_cstring(512)
        files.append({'name': fname, 'size': size, 'offset': offset,
                      'uncompressed_size': uncomp, 'compression_type': comp,
                      'file_type_index': type_idx, 'name_offset': name_off})

    r.seek(file_ext_offset)
    exts = []
    for _ in range(file_ext_count):
        tlen = r.read_dword()
        s = hdata[r.pos:r.pos+tlen]; r.pos += tlen
        exts.append(s.rstrip(b'\x00').decode('latin-1').strip()); r.seek(12,1)
    for f in files:
        f['ext'] = exts[f['file_type_index']] if 0 <= f['file_type_index'] < len(exts) else '?'
    return {'version': 2, 'num_files': num_files,
            'file_records_offset': file_records_offset,
            'name_dir_offset': name_dir_offset,
            'file_ext_offset': file_ext_offset, 'exts': exts, 'files': files}

def parse_v5(hdata):
    """dfpf versão 5 — Costume Quest 2"""
    assert hdata[:4] == b'dfpf' and hdata[4] == 5
    rd = lambda o: struct.unpack_from('>I', hdata, o)[0]
    rq = lambda o: struct.unpack_from('>Q', hdata, o)[0]
    file_ext_offset     = rq(8)
    name_dir_offset     = rq(16)
    file_ext_count      = rd(24)
    num_files           = rd(32)
    file_records_offset = rq(56)

    SOR, files = 16, []
    for i in range(num_files):
        P        = file_records_offset + SOR * i
        uncomp   = rd(P)    >> 8
        name_off = rd(P+3)  >> 11
        offset   = rd(P+8)  >> 3
        size     = ((rd(P+11) << 5) & 0xFFFFFFFF) >> 9
        type_idx = ((((rd(P+14) << 4) & 0xFFFFFFFF) >> 24) >> 1)
        comp     = hdata[P+15] & 15
        base = name_dir_offset + name_off
        end  = hdata.find(b'\x00', base, base+512)
        fname = hdata[base:end].decode('latin-1','replace').strip()
        files.append({'name': fname, 'size': size, 'offset': offset,
                      'uncompressed_size': uncomp, 'compression_type': comp,
                      'file_type_index': type_idx, 'name_offset': name_off})

    pos = file_ext_offset
    exts = []
    for _ in range(file_ext_count):
        tlen = struct.unpack_from('>I', hdata, pos)[0]; pos += 4
        s = hdata[pos:pos+tlen].rstrip(b'\x00').decode('latin-1').strip(); pos += tlen + 12
        exts.append(s)
    for f in files:
        f['ext'] = exts[f['file_type_index']] if 0 <= f['file_type_index'] < len(exts) else '?'
    return {'version': 5, 'num_files': num_files,
            'file_records_offset': file_records_offset,
            'name_dir_offset': name_dir_offset,
            'file_ext_offset': file_ext_offset, 'exts': exts, 'files': files}

def auto_parse(hdata):
    v = hdata[4]
    if v == 2:   return parse_v2(hdata)
    elif v == 5: return parse_v5(hdata)
    else: raise ValueError(f"Versão dfpf não suportada: {v}")

def extract_all_auto(h_path, p_path, out_dir=None):
    hdata = open(h_path, 'rb').read()
    pdata = open(p_path, 'rb').read()
    meta  = auto_parse(hdata)
    if out_dir: os.makedirs(out_dir, exist_ok=True)
    results = []
    for f in meta['files']:
        raw = pdata[f['offset']: f['offset'] + f['size']]
        try:
            data = zlib.decompress(raw) if f['compression_type'] in (4,8) and f['uncompressed_size'] != f['size'] else raw
        except:
            data = raw
        f['extracted'] = data
        results.append(f)
    return meta, results

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Uso: python3 dfpf_parser.py <arquivo.~h> <arquivo.~p> <pasta_saida>")
        sys.exit(1)
    h_path, p_path, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    meta, results = extract_all_auto(h_path, p_path)
    print(f"dfpf v{meta['version']} | {meta['num_files']} arquivos")
    os.makedirs(out_dir, exist_ok=True)
    count = 0
    for f in results:
        if f['extracted']:
            path = os.path.join(out_dir, f['name'].replace('/', os.sep).replace('\\\\', os.sep))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, 'wb').write(f['extracted'])
            count += 1
    print(f"Extraídos: {count} arquivos em '{out_dir}'")
