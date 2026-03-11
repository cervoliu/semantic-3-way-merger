#include "klee/klee.h"

void func(int cond) {
    int *ptr = malloc(sizeof(int));
    if (cond) {
        free(ptr);
        return;
    }



    int tmp;
    
}

int main() {
    int x;
    klee_make_symbolic(&x, sizeof(x), "x");
    func(x);
    return 0;
}