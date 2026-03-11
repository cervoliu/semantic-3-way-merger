#include "klee/klee.h"

int func(int n, int m) {
    if (n + m == 0) {
        return -1;
    }
    int x = m;
    if (m == 0) return 0;
    int t;
    t = n % x + 1;
    return t;
}

int main() {
    int x, y;
    klee_make_symbolic(&x, sizeof(x), "x");
    klee_make_symbolic(&y, sizeof(y), "y");
    func(x, y);
    return 0;
}