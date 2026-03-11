void func(int cond) {
    int x = 1;
    int *ptr = &x;
    if (!cond) ptr = NULL;
    
    if (ptr != NULL) {
        *ptr = 1;
    }
}