#include <iostream>

class Test {
public:
    void foo(int x) {
        if (x > 10) {
            std::cout << x;
        }
    }
};