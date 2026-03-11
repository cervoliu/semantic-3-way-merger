#include "klee/klee.h"

int main() {
    int a, b;


    klee_make_symbolic(&a, sizeof(a), "a");
    klee_make_symbolic(&b, sizeof(b), "b");
    

    if (a > 0 && b > 0) {
        if (a > b) {
            a = a + b;
        } else {
            a = a - b;
        }
    } else {
        a = 0;
    }

    return 0;
}