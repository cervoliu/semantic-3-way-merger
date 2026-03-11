#include "klee/klee.h"

void func(int cond) {
    int x = 1;
    int *ptr = &x;
    if (!cond) ptr = NULL;
    
    if (ptr != NULL) {
        *ptr = 1;
    }
}

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    func(x);
    return 0;
}