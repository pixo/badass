CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

include(RezBuild)

FILE(GLOB_RECURSE py_files "src/*")

rez_install_files(
	src/*
	DESTINATION .
	EXECUTABLE
)