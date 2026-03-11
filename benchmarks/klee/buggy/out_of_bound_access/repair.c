void func() {
    int x = 6, y = 6, z = 0;

    int a[10];

    // Safely adjust z to avoid out-of-bounds access
    z += x; // Include the intent of Branch A
    z += y; // Include the intent of Branch B

    if (z >= 10) { // Ensure z is within bounds
        z = 9; // Cap z at the highest valid index
    }

    int res = a[z]; // Safe access within array bounds
}