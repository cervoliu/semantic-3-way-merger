#include "klee/klee.h"

void func(int cond) {
    int *ptr = malloc(sizeof(int));
    if (cond) {
        free(ptr);
        return; // `ptr` is freed, no further use.
    }
    
    // Free `ptr` only once, unconditionally after the condition check
    int tmp;
    free(ptr);
}

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    func(x);
    return 0;
}