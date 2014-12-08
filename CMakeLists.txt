CMAKE_MINIMUM_REQUIRED(VERSION 2.8)

include(RezBuild)

rez_install_files(
	src/*
	DESTINATION .
	EXECUTABLE
)
