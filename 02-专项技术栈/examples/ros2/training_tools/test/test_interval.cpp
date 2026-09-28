#include <gtest/gtest.h>

bool valid_interval(int milliseconds) {
  return milliseconds >= 10 && milliseconds <= 1000;
}

TEST(Interval, IncludesBounds) {
  EXPECT_TRUE(valid_interval(10));
  EXPECT_TRUE(valid_interval(1000));
}
TEST(Interval, RejectsOutside) {
  EXPECT_FALSE(valid_interval(9));
  EXPECT_FALSE(valid_interval(1001));
}
