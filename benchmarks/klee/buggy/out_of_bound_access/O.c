#include "klee/klee.h"

void func() {
    int x = 6, y = 6, z = 0;
    
    int a[10];

    int res = a[z];
}

int main() {
    func();
    return 0;
}