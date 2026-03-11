#include "klee/klee.h"

int main() {
    int a, b;
    int c;

    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");
    klee_make_symbolic(&c, sizeof(c), "c");

    if (a > 0 && b > 0) {
        if (a > b) {
            a = a + b;
            if (a > b) {
                c = a + b;
            } else {
                c = 0;
            }
        } else {
            a = a - b;
            c = 0;
        }
    } else {
        a = 0;
    }

    return 0;
}