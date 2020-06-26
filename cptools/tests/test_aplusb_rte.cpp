#include <bits/stdc++.h>

using namespace std;

int main() {
    int a[2];
    cin >> a[0];
    assert(a[0] != 1);

    cin >> a[10000001];
    cout << (a[0] + a[10000001]) << endl;
    return 0;
}
