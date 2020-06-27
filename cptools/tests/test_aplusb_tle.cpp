#include <bits/stdc++.h>

using namespace std;

int main() {
    long long a, b;
    cin >> a >> b;
    if (a == 3 && b == 4) {
        cout << "tle!" << endl;
        while (a > 0 || b > 0) {
            a++;
            b++;
        }
    }
    cout << (a + b) << endl;
    return 0;
}
