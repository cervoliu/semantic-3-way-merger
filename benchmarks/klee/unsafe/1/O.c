#include "klee/klee.h"

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");

    int t = 1;
    
    return 0;
}