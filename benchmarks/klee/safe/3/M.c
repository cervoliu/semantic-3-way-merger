#include "klee/klee.h"

int f() {
    int i = 0;
    int odds = 0;
    while (i < 5) // R
    {
        odds *= 10;
        odds += 2 * i + 1; // R
        // next
        ++ i;
    }
    return odds;
}

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    x = f();
    return 0;
}