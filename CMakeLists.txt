cmake_minimum_required(VERSION 3.15)
project(ThreeDimensionsCore LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(THREEDIMENSIONS_BUILD_PYBIND "Build the pybind11 C++ extension" ON)

if (THREEDIMENSIONS_BUILD_PYBIND)
  find_package(pybind11 CONFIG QUIET)
  if (NOT pybind11_FOUND)
    include(FetchContent)
    message(STATUS "pybind11 not found; attempting FetchContent download (requires internet).")
    FetchContent_Declare(
      pybind11
      GIT_REPOSITORY https://github.com/pybind/pybind11.git
      GIT_TAG v2.13.6
    )
    FetchContent_MakeAvailable(pybind11)
  endif()
endif()

file(GLOB_RECURSE CORE_SOURCES
    cpp_core/*.cpp
)

if (THREEDIMENSIONS_BUILD_PYBIND)
  if (TARGET pybind11::module OR pybind11_FOUND)
    pybind11_add_module(_threedimensions_core ${CORE_SOURCES})

    install(TARGETS _threedimensions_core
            LIBRARY DESTINATION threedimensions
            ARCHIVE DESTINATION threedimensions
            RUNTIME DESTINATION threedimensions)
  else()
    message(WARNING "pybind11 is unavailable; skipping _threedimensions_core build. The Python fallback will still work.")
  endif()
else()
  message(STATUS "THREEDIMENSIONS_BUILD_PYBIND=OFF; skipping _threedimensions_core build.")
endif()