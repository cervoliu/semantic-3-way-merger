#include "klee/klee.h"

int f() {
    int i = 1; // L
    int odds = 0;
    while (i < 10)
    {
        if ((i & 1) != 0)
        {
            odds *= 10;
            odds += i;
        }
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