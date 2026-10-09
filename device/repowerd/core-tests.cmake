cmake_minimum_required(VERSION 3.20)
project(repowerd_core_tests CXX)
set(CMAKE_CXX_STANDARD 17)
if(NOT REPOWERD_SOURCE)
  message(FATAL_ERROR "Pass REPOWERD_SOURCE explicitly")
endif()
find_package(GTest REQUIRED)
file(GLOB CORE "${REPOWERD_SOURCE}/src/core/*.cpp")
file(GLOB TESTS "${REPOWERD_SOURCE}/tests/core-tests/*.cpp")
list(FILTER TESTS EXCLUDE REGEX "test_performance_booster.cpp")
add_executable(raise-tests ${CORE} ${TESTS}
  "${REPOWERD_SOURCE}/tests/common/fake_log.cpp"
  "${REPOWERD_SOURCE}/tests/common/fake_system_power_control.cpp"
  "${REPOWERD_SOURCE}/tests/common/spin_wait.cpp")
target_include_directories(raise-tests PRIVATE "${REPOWERD_SOURCE}" "${REPOWERD_SOURCE}/tests/common")
target_link_libraries(raise-tests PRIVATE GTest::gtest GTest::gmock GTest::gtest_main pthread)
enable_testing()
add_test(NAME repowerd-core COMMAND raise-tests)
