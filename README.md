# cipherEngine

Implementaciones desde cero de algoritmos criptográficos clásicos y modernos en Python puro. El objetivo es entender cómo funcionan internamente, no reemplazar librerías de producción.

---

## Algoritmos implementados

| Algoritmo | Tipo | Seguridad | Archivo |
|-----------|------|-----------|---------|
| One-Time Pad (OTP) | Simétrico | Perfecta (Shannon 1949) | `otp.py` |

---

## One-Time Pad (`otp.py`)

El único sistema de cifrado matemáticamente irrompible. Demostrado por Claude Shannon en 1949: si la clave es verdaderamente aleatoria, de la misma longitud que el mensaje y nunca se reutiliza, es imposible romperlo incluso con potencia de cómputo infinita.

### Cómo funciona

```
Archivo (bytes):  10110010 01001101 11000011 ...
Clave (random):   01101011 10110100 00111010 ...
XOR bit a bit →   11011001 11111001 11111001 ...  ← texto cifrado
```

La operación XOR es su propia inversa: aplicar XOR dos veces con la misma clave devuelve el original exacto.

### Uso

```python
from otp import otp_encrypt_file, otp_decrypt_file

# Cifrar
otp_encrypt_file(
    path_input  = "video.mp4",
    path_output = "video.mp4.enc",
    path_key    = "video.mp4.key"
)

# Descifrar
otp_decrypt_file(
    path_encrypted = "video.mp4.enc",
    path_key       = "video.mp4.key",
    path_output    = "video.mp4.dec"
)
```

### Generación de clave

La clave se genera con `os.urandom()`, que lee directamente del CSPRNG del sistema operativo (`/dev/urandom` en Linux/macOS, `CryptGenRandom` en Windows). Esto garantiza entropía física real — no pseudoaleatoriedad.

```python
import os
clave = os.urandom(len(archivo_en_bytes))
```

### Rendimiento

El cuello de botella es `os.urandom()`, no el XOR. El XOR se vectoriza con NumPy (instrucciones SIMD del CPU).

```
os.urandom:    ~300 MB/s   ← límite real del sistema
XOR (numpy):   ~7000 MB/s  ← no es el problema
XOR (Python):  ~40  MB/s   ← evitar para archivos grandes
```

Benchmark en tu máquina:

```bash
python benchmark.py --file tu_archivo.mp4
```

### Procesamiento por bloques

Para archivos grandes (4 GB+) el cifrado se procesa en bloques para no cargar todo en RAM:

```python
BLOCK_SIZE = 1 * 1024 * 1024  # 1 MB por bloque
# RAM usada: BLOCK_SIZE × 3 = ~3 MB, sin importar el tamaño del archivo
```

### Limitaciones del OTP

- La clave debe tener exactamente el mismo tamaño que el archivo
- La clave nunca puede reutilizarse (reutilizarla destruye la seguridad perfecta)
- Distribuir la clave de forma segura es tan difícil como distribuir el mensaje original
- No escala para uso general — es ideal para casos donde la distribución física de claves es viable

### Guardar la clave

```
/cifrados/archivo.mp4.enc   ← texto cifrado
/claves/archivo.mp4.key     ← clave (idealmente en un disco físico separado)
```

La extensión de la clave no tiene ningún efecto técnico. `.key` es solo una convención.

---

## Instalación

```bash
git clone https://github.com/tu-usuario/cipherEngine
cd cipherEngine
pip install numpy
```

No hay más dependencias. `os`, `numpy` y la librería estándar de Python es todo lo necesario.

---

## Estructura del proyecto

```
cipherEngine/
├── src/
│   ├── otp.py          # One-Time Pad
│   └── benchmark.py    # Benchmark de rendimiento por tamaño de bloque
├── tests/
│   └── test_otp.py     # Verificación de integridad cifrado/descifrado
└── README.md
```

---

## Ejecutar los tests

```bash
python -m pytest tests/
```

Los tests verifican que `descifrado == archivo_original` para varios tamaños de archivo.

---

## Contexto y referencias

- Shannon, C. (1949). *Communication Theory of Secrecy Systems*. Bell System Technical Journal.
- El teorema de Shannon prueba que la seguridad perfecta requiere `|clave| ≥ |mensaje|`.
- El proyecto VENONA (1943-1980) rompió mensajes soviéticos cifrados con OTP porque reutilizaron claves — no por una debilidad matemática del algoritmo.

---

## Aviso

Este repositorio es educativo. Para cifrado en producción usa librerías auditadas como `cryptography` (Python) o `libsodium`. El objetivo aquí es entender los mecanismos, no reemplazar implementaciones battle-tested.
