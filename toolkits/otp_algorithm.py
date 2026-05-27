import os
import numpy as np
from pathlib import Path
import time
import argparse

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"
TITLE = """
   ____                 _______                   ____            __
  / __ \____  ___      /_  __(_)___ ___  ___     / __ \____ _____/ /
 / / / / __ \/ _ \______/ / / / __ `__ \/ _ \   / /_/ / __ `/ __  / 
/ /_/ / / / /  __/_____/ / / / / / / / /  __/  / ____/ /_/ / /_/ /  
\____/_/ /_/\___/     /_/ /_/_/ /_/ /_/\___/  /_/    \__,_/\__,_/   
"""


BLOCK_SIZE = 1 * 1024 * 1024  # 1 MB

parser = argparse.ArgumentParser(
    description='OTP CYPHER - SYSTEM | Cifrado de archivos con One-Time Pad',
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="""
Ejemplos:
  Cifrar:    python otp.py -f video.mp4  -o video.lock -e
  Cifrar:    python otp.py -f video.mp4  -o video.lock -e -k clave.pkey
  Descifrar: python otp.py -f video.lock -o video.mp4  -d -k clave.pkey
    """)
parser.add_argument('--key',     '-k', type=str, required=False, dest='key_argument')
parser.add_argument('--file',    '-f', type=str, required=True,  dest='file_argument')
parser.add_argument('--output',  '-o', type=str, required=True,  dest='output_argument')
parser.add_argument('--encrypt', '-e', action='store_true',      dest='encrypt_argument')
parser.add_argument('--decrypt', '-d', action='store_true',      dest='decrypt_argument')
args = parser.parse_args()


def key_gen(length):
    return os.urandom(length)

def otp_encrypt_numpy(path_input, path_output, path_key):
    total     = Path(path_input).stat().st_size
    procesado = 0
    start     = time.perf_counter()

    with open(path_input, "rb") as fin, \
         open(path_output, "wb") as fout, \
         open(path_key,    "wb") as fkey:

        while True:
            block = fin.read(BLOCK_SIZE)
            if not block:
                break
            key_block = os.urandom(len(block))
            a       = np.frombuffer(block,     dtype=np.uint8)
            k       = np.frombuffer(key_block, dtype=np.uint8)
            cifrado = np.bitwise_xor(a, k).tobytes()
            fout.write(cifrado)
            fkey.write(key_block)
            procesado += len(block)
            elapsed    = time.perf_counter() - start
            speed      = (procesado / elapsed) / (1024 * 1024)
            pct        = (procesado / total) * 100
            print(f"\r{pct:.1f}%  {speed:.1f} MB/s", end="", flush=True)

    print(f"\nListo — {total / 1024 / 1024:.1f} MB en {time.perf_counter() - start:.1f}s")
    print(f"Cifrado → {path_output}")
    print(f"Clave   → {path_key}")


def otp_decrypt_numpy(path_input, path_output, path_key):
    total     = Path(path_input).stat().st_size
    procesado = 0
    start     = time.perf_counter()

    with open(path_input, "rb") as fin, \
         open(path_output, "wb") as fout, \
         open(path_key,    "rb") as fkey:

        while True:
            block     = fin.read(BLOCK_SIZE)
            key_block = fkey.read(BLOCK_SIZE)
            if not block:
                break
            a           = np.frombuffer(block,     dtype=np.uint8)
            k           = np.frombuffer(key_block, dtype=np.uint8)
            descifrado  = np.bitwise_xor(a, k).tobytes()
            fout.write(descifrado)
            procesado += len(block)
            elapsed    = time.perf_counter() - start
            speed      = (procesado / elapsed) / (1024 * 1024)
            pct        = (procesado / total) * 100
            print(f"\r{pct:.1f}%  {speed:.1f} MB/s", end="", flush=True)

    print(f"\nListo — {total / 1024 / 1024:.1f} MB en {time.perf_counter() - start:.1f}s")
    print(f"Descifrado → {path_output}")

if __name__ == "__main__":
    print(f"{CYAN}{BOLD}{TITLE}{RESET}")

    if args.encrypt_argument and args.decrypt_argument:
        print(f"{RED}Error: no puedes usar --encrypt y --decrypt al mismo tiempo{RESET}")
        exit(1)

    if not args.encrypt_argument and not args.decrypt_argument:
        print(f"{RED}Error: debes indicar --encrypt o --decrypt{RESET}")
        exit(1)

    if args.encrypt_argument:
        key_path = args.key_argument if args.key_argument else args.output_argument + ".pkey"
        print(f"{YELLOW}Cifrando:{RESET} {args.file_argument}")
        otp_encrypt_numpy(
            path_input=args.file_argument,
            path_output=args.output_argument,
            path_key=key_path
        )

    elif args.decrypt_argument:
        if not args.key_argument:
            print(f"{RED}Error: --decrypt requiere --key <archivo_clave>{RESET}")
            exit(1)
        print(f"{YELLOW}Descifrando:{RESET} {args.file_argument}")
        otp_decrypt_numpy(
            path_input=args.file_argument,
            path_output=args.output_argument,
            path_key=args.key_argument
        )