import numpy as np

def add_exact(a, b, n):
    max_val = (1 << n) - 1
    if n <= 8: dtype = np.uint16
    elif n <= 16: dtype = np.uint32
    else: dtype = np.uint64
    
    return np.clip(a.astype(dtype) + b.astype(dtype), 0, max_val)

def add_loa(a, b, k, n):
    if k == 0: return add_exact(a, b, n)
    mask = (1 << k) - 1
    sum_lsb = (a & mask) | (b & mask)
    cin = ((a >> (k - 1)) & 1) & ((b >> (k - 1)) & 1)
    sum_msb = (a >> k) + (b >> k) + cin
    max_val = (1 << n) - 1
    return (((sum_msb << k) | sum_lsb) & max_val)

def add_heaa(a, b, k, n):
    if k == 0: return add_exact(a, b, n)
    mask = (1 << (k - 1)) - 1 if k > 1 else 0
    sum_or = (a & mask) | (b & mask)
    bit_a, bit_b = (a >> (k - 1)) & 1, (b >> (k - 1)) & 1
    c_approx = bit_a & bit_b
    sum_k1 = np.where(c_approx == 1, 0, bit_a | bit_b)
    sum_lsb = (sum_k1 << (k - 1)) | sum_or
    sum_msb = (a >> k) + (b >> k) + c_approx
    max_val = (1 << n) - 1
    return (((sum_msb << k) | sum_lsb) & max_val)

def add_hoeraa(a, b, k, n):
    if k == 0: return add_exact(a, b, n)
    c_approx = ((a >> (k - 1)) & 1) & ((b >> (k - 1)) & 1)
    if k == 2:
        s0 = (a & 1) | (b & 1)
        s1 = np.where(c_approx == 1, (a & 1) & (b & 1), ((a >> 1) & 1) | ((b >> 1) & 1))
        sum_lsb = (s1 << 1) | s0
    elif k > 2:
        ones = (1 << (k - 2)) - 1
        s_k2 = ((a >> (k - 2)) & 1) | ((b >> (k - 2)) & 1)
        s_k1 = np.where(c_approx == 1, ((a >> (k - 2)) & 1) & ((b >> (k - 2)) & 1), ((a >> (k - 1)) & 1) | ((b >> (k - 1)) & 1))
        sum_lsb = (s_k1 << (k - 1)) | (s_k2 << (k - 2)) | ones
    else:
        sum_lsb = np.where(c_approx == 1, 0, (a & 1) | (b & 1))
    sum_msb = (a >> k) + (b >> k) + c_approx
    max_val = (1 << n) - 1
    return (((sum_msb << k) | sum_lsb) & max_val)

def add_herloa(a, b, k, n):
    if k == 0: return add_exact(a, b, n)
    mask = (1 << (k - 1)) - 1 if k > 1 else 0
    s_int_lower = (a & mask) | (b & mask)
    bit_a, bit_b = (a >> (k - 1)) & 1, (b >> (k - 1)) & 1
    s_int_k1 = bit_a ^ bit_b
    c_approx = bit_a & bit_b
    
    correction = ((a >> (k - 2)) & 1) & ((b >> (k - 2)) & 1) if k > 1 else np.zeros_like(a)
    
    sum_approx = np.where(correction == 0, (s_int_k1 << (k-1)) | s_int_lower, 0)
    
    corr_0_val = (1 << (k-1)) | (s_int_lower & ((1 << (k-2)) - 1)) if k > 2 else (1 << (k-1))
    sum_approx = np.where((correction == 1) & (s_int_k1 == 0), corr_0_val, sum_approx)
    
    corr_1_val = (s_int_k1 << (k-1))
    if k > 1: corr_1_val |= (((s_int_lower >> (k-2)) & 1) << (k-2))
    if k > 2: corr_1_val |= ((1 << (k-2)) - 1)
    sum_approx = np.where((correction == 1) & (s_int_k1 == 1), corr_1_val, sum_approx)
    
    sum_msb = (a >> k) + (b >> k) + c_approx
    max_val = (1 << n) - 1
    return (((sum_msb << k) | sum_approx) & max_val)
