#include <stdio.h>
#include <stdlib.h>

// Function to calculate the minimum number of scalar multiplications
int matrixChainMultiplication(int dims[], int n) {
    int M[n][n]; // M-table
    int S[n][n]; // S-table

    // Initialize M-table with zeros
    for (int i = 1; i < n; i++) {
        M[i][i] = 0;
    }

    // Fill the tables using dynamic programming
    for (int chainLen = 2; chainLen < n; chainLen++) {
        for (int i = 1; i < n - chainLen + 1; i++) {
            int j = i + chainLen - 1;
            M[i][j] = INT_MAX;

            for (int k = i; k <= j - 1; k++) {
                int cost = M[i][k] + M[k + 1][j] + dims[i - 1] * dims[k] * dims[j];
                if (cost < M[i][j]) {
                    M[i][j] = cost;
                    S[i][j] = k;
                }
            }
        }
    }

    // Print the optimal parenthesization
    printf("Optimal Parenthesization:\n");
    for (int i = 1; i < n - 1; i++) {
        for (int j = 2; j < n; j++) {
            printf("M%d%d: %d\t", i, j, S[i][j]);
        }
        printf("\n");
    }

    return M[1][n - 1]; // Minimum scalar multiplications
}

int main() {
    int n;
    printf("Enter the number of matrices: ");
    scanf("%d", &n);

    int dims[n];
    printf("Enter the dimensions of the matrices: ");
    for (int i = 0; i < n; i++) {
        scanf("%d", &dims[i]);
    }

    int minMultiplications = matrixChainMultiplication(dims, n);
    printf("Minimum number of scalar multiplications: %d\n", minMultiplications);

    return 0;
}
