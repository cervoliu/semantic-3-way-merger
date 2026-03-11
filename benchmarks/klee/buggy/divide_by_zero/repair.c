#include "klee/klee.h"

int func(int n, int m) {
    if (n + m == 0) {
        return -1; // From A.c
    }
    int x = m; // Use m as the divisor, ensuring it is non-zero if used
    if (m == 0) {
        return 0; // Handle the case where m is zero explicitly
    }
    int t;
    t = n % x + 1; // Safely use x as a divisor
    return t;
}

int main() {
    int x, y;
    klee_make_symbolic(&x, sizeof(x), "x");
    klee_make_symbolic(&y, sizeof(y), "y");
    func(x, y);
    return 0;
}