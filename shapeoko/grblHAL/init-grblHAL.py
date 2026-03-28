import argparse, serial, sys, time

def init(port, file):
    ser = serial.Serial(port, 115200, timeout=1)
    print('Port:', ser)
    while True:
        time.sleep(.1)
        ser.write(b'\n')
        res = ser.readline()
        if b'ok' in res:
            break
        #print(res)
    print('Got reply')
    with open(file, 'r') as f:
        lines = f.readlines()
        count = 0
        for line in lines:
            time.sleep(.1)
            ser.write(line.encode('ascii'))
            ok = False
            for i in range(0, 10):
                res = ser.readline()
                if b'ok' in res:
                    ok = True
                    break
            if not ok:
                print(f'Error: No reply to {line.strip()}')
                sys.exit(1)
            count += 1
            print(f'{count}/{len(lines)}\r', end='', flush=True)
    print('\nDone')
    ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Initialize grblHAL')
    parser.add_argument('port',
                        help="USB serial port")
    parser.add_argument('file',
                        help="FFile with grblHAL settings")

    args = parser.parse_args()
    init(args.port, args.file)
