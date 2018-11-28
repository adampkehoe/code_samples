import copy
import operator
import random
import sys

def random_matrix(n, m, p=1, L=0, U=1, keep=False):

    # basic input checking
    assert(n > 0 and type(n) is int), "n must be a positive integer"
    assert(m > 0 and type(m) is int), "m must be a positive integer"
    assert(0 < p <= 1), "p must satisfy 0 < p <= 1"
    assert(L <= U), "l and u must satisfy L <= U"

    # generate a 0 matrix of size m x n
    M = [[0 for c in range(m)] for r in range(n)]

    # generate a random number for each element
    for r in range(n):
        for c in range(m):
            # generate a random number on the interval [0, 1]
            x = random.uniform(0, 1)
            # if x <= p, scale x from the interval [0, p] to the interval
            # [l, u] and store the value to M[r][c]; otherwise, store 0
            M[r][c] = L + (U - L) * x * 1.0 / p if x <= p else 0

    # if applying the matrix discarding subroutine
    if not keep:
        # while any row or column consists of only zeros
        while any([x.count(0) == len(x) for x in M + map(list, zip(*M))]):
            # recursively generate a new matrix
            return random_matrix(n, m, p=p, L=L, U=U, keep=keep)

    return M


def inverse(C):

    # check that the matrix is square
    assert(len(C) == len(C[0])), "C must be square"

    A = C

    # store the size of the matrix
    N = len(A)

    # initialize an identity matrix to be transformed into A inverse
    B = [[1 if i == j else 0 for j in range(N)] for i in range(N)]

    # eliminate the lower triangular
    for p in range(N):
        m = max(range(N-p), key=[abs(r[p]) for r in A[p:]].__getitem__) + p
        if A[m][p] == 0:
            sys.exit("singular matrix")
        else:
            A[p], A[m] = A[m], A[p]
            B[p], B[m] = B[m], B[p]
        for r in range(p+1, N):
            k = float(1.0 * A[r][p] / A[p][p])
            A[r] = A[r] - A[p]*[k]*N
            B[r] = B[r] - B[p]*[k]*N

    # eliminate the upper triangular
    for p in range(N)[::-1]:
        for r in range(p)[::-1]:
            k = float(1.0 * A[r][p] / A[p][p])
            # row addition/subtraction
            A[r] = A[r] - A[p]*[k]*N
            B[r] = B[r] - B[p]*[k]*N

    # scale rows so the diagonal is 1
    for r in range(N):
        k = float(A[r][r])
        # row multiplication/division
        A[r] = A[r]/[k]*N
        B[r] = B[r]/[k]*N

    return B

def mm_mult(a, b):
    
    assert(len(a[0]) == len(b)), "a and b are incompatible for multiplication"
    return [[sum(a[r][i] * b[i][c] for i in range(len(b)))
        for c in range(len(b[0]))]
        for r in range(len(a))]

def matprint(x):
   
    s = "\n".join([" ".join(["{:10.3f}"]*len(x[0]))]*len(x)) + "\n"
    b = [i for j in x for i in j]
    print(s.format(*b))

