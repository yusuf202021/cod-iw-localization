import pymem, struct, json, sys

pm = pymem.Pymem("iw7_ship.exe")
global start
start = pm.base_address + 0x35135B0
end, = struct.unpack("Q", pm.read_bytes(start, 8))
def interact(l):
    import code
    for i in globals().items():
        l[i[0]] = i[1]
    code.interact(local=l)
start += 8
count = (end - start) // 16


def read_null(pm, addr):
    ret = b""
    while b"\x00" not in ret:
        ret += pm.read_bytes(addr, 1)
        addr += 1
    return ret[:-1].decode(errors="ignore")
        

def export():
    ret = {}
    global start
    for i in range(count):
        try:
            string_o, id_o = struct.unpack("QQ", pm.read_bytes(start, 16))
            start += 16
            string, id_o = read_null(pm, string_o), read_null(pm, id_o)
            ret[id_o] = string
        except:
            pass
    json.dump(ret, open("localize.json", "w", encoding="utf8"), indent=4, ensure_ascii=False)
def _import():
    strings = json.load(open("localize.json", encoding="utf8"))
    to_write = b""
    table_offsets = {}
    for id, string in strings.items():
        table_offsets[id] = len(to_write)
        to_write += string.encode() + b"\x00"
    global start
    new_table = pm.allocate(len(to_write))
    pm.write_bytes(new_table, to_write, len(to_write))
    for i in range(count):
        try:
            string_o, id_o = struct.unpack("QQ", pm.read_bytes(start, 16))
            start += 16
            string, id = read_null(pm,string_o), read_null(pm, id_o)
        except:
            continue
        if id in strings:
            print(f"Hooking {id} to {hex(table_offsets[id] + new_table)} from {hex(string_o)}. New string: {strings[id]}")
            pm.write_bytes(start - 16, struct.pack("Q", table_offsets[id] + new_table) ,8)
if __name__ == "__main__":
    if len(sys.argv) == 1:
        quit("""Usage:
    -e: It creates localize.json file
    -i: Imports localize.json to game.""")
    if sys.argv[1] == "-e":
        export()
    elif sys.argv[1] == "-i":
        _import()