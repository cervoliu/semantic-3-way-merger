#include "klee/klee.h"

int f() {
    int i = 1; // L
    int odds = 0;
    while (i < 5) // R
    {
        odds *= 10;
        odds += 2 * i + 1; // R
        // next
        i += 2; // L
    }
    return odds;
}

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    x = f();
    return 0;
}