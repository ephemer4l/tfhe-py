import numpy

from tfhe.boot_gates import tfhe_gate_CONSTANT_, tfhe_gate_MUX_, tfhe_gate_XNOR_
from tfhe.keys import (
    TFHECloudKey,
    empty_ciphertext,
    tfhe_decrypt,
    tfhe_encrypt,
    tfhe_key_pair,
    tfhe_parameters,
)
from tfhe.lwe import LweSampleArray
from tfhe.utils import bitarray_to_int, int_to_bitarray

rng = numpy.random.RandomState(123)


def test() -> None:
    secret_key, cloud_key = tfhe_key_pair(rng)

    bits42 = int_to_bitarray(42)
    bits4711 = int_to_bitarray(4711)

    ciphertext42 = tfhe_encrypt(rng, secret_key, bits42)
    ciphertext4711 = tfhe_encrypt(rng, secret_key, bits4711)

    result = _encrypted_minimum(cloud_key, ciphertext42, ciphertext4711)

    answer_bits = tfhe_decrypt(secret_key, result)
    answer_int = bitarray_to_int(answer_bits)

    assert answer_int == 42


def _encrypted_minimum(
    cloud_key: TFHECloudKey,
    a: LweSampleArray,
    b: LweSampleArray,
) -> LweSampleArray:
    params = tfhe_parameters(cloud_key)

    shape = a.shape
    result = empty_ciphertext(params, shape)

    nb_bits = result.shape[0]

    params = tfhe_parameters(cloud_key)

    tmp1 = empty_ciphertext(params, (1,))
    tmp2 = empty_ciphertext(params, (1,))

    # Initialize the carry to 0.
    tfhe_gate_CONSTANT_(tmp1, False)

    # Run the elementary comparator gate `n` times.
    for i in range(nb_bits):
        tmp_a = a[i : i + 1]  # type: ignore
        tmp_b = b[i : i + 1]  # type: ignore
        tfhe_gate_XNOR_(cloud_key, tmp2, tmp_a, tmp_b)
        tfhe_gate_MUX_(cloud_key, tmp1, tmp2, tmp1, tmp_a)

    # `tmp1` is the result of the comparison:
    #   - 0 if `a` is larger
    #   - 1 if `b` is larger
    # Select the max and copy it to the `result``.
    tfhe_gate_MUX_(cloud_key, result, tmp1, b, a)

    return result
