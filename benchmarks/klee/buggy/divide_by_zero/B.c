#include "klee/klee.h"

int func(int n, int m) {
    if (n + m == 0) {
        return 0;
    }
    int x = 0;
    if (m == 0) return 0;
    int t;
    t = n % m;
    return t;
}

int main() {
    int x, y;
    klee_make_symbolic(&x, sizeof(x), "x");
    klee_make_symbolic(&y, sizeof(y), "y");
    func(x, y);
    return 0;
}