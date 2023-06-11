# pylint: disable=duplicate-code
# pylint: disable=redefined-outer-name
# type: ignore

import time

import numpy
from numpy.typing import NDArray

from tfhe.boot_gates import tfhe_gate_MUX_
from tfhe.keys import (
    empty_ciphertext,
    tfhe_decrypt,
    tfhe_encrypt,
    tfhe_key_pair,
    tfhe_parameters,
)


def int_to_bitarray(x: int) -> NDArray[numpy.bool_]:
    return numpy.array([((x >> i) & 1 != 0) for i in range(16)])


def bitarray_to_int(x: NDArray[numpy.bool_]) -> int:
    int_answer = 0
    for i in range(16):
        int_answer = int_answer | (x[i] << i)
    return int_answer


def encrypt():
    rng = numpy.random.RandomState(123)

    print("Key generation:")
    t = time.time()
    secret_key, cloud_key = tfhe_key_pair(rng)
    print(time.time() - t)

    bits1 = int_to_bitarray(2017)
    bits2 = int_to_bitarray(42)
    bits3 = int_to_bitarray(12345)

    print("Encryption:")
    t = time.time()
    ciphertext1 = tfhe_encrypt(rng, secret_key, bits1)
    ciphertext2 = tfhe_encrypt(rng, secret_key, bits2)
    ciphertext3 = tfhe_encrypt(rng, secret_key, bits3)
    print(time.time() - t)

    return secret_key, cloud_key, ciphertext1, ciphertext2, ciphertext3


def process(cloud_key, ciphertext1, ciphertext2, ciphertext3):
    params = tfhe_parameters(cloud_key)
    result = empty_ciphertext(params, ciphertext1.shape)

    print("Processing:")
    t = time.time()
    tfhe_gate_MUX_(cloud_key, result, ciphertext1, ciphertext2, ciphertext3)
    print(time.time() - t)

    return result


def verify(secret_key, answer) -> None:
    print("Decryption:")
    t = time.time()
    answer_bits = tfhe_decrypt(secret_key, answer)
    print(time.time() - t)

    int_answer = bitarray_to_int(answer_bits)
    print("Answer:", int_answer)


secret_key, cloud_key, ciphertext1, ciphertext2, ciphertext3 = encrypt()
answer = process(cloud_key, ciphertext1, ciphertext2, ciphertext3)
verify(secret_key, answer)
