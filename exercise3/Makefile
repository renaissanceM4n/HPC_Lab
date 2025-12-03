# Compiler and flags
CXX = mpic++
CXXFLAGS = -O3 -std=c++17 -fopenmp

# Source files
SRCS = main.cpp raytracer.cpp scene.cpp
OBJS = $(SRCS:.cpp=.o)
OBJS_NO_COLLAPSE = $(SRCS:.cpp=.no_collapse.o)

# Target executables
TARGETS = snowman_collapse snowman_no_collapse

all: $(TARGETS)

snowman_collapse: $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

snowman_no_collapse: $(OBJS_NO_COLLAPSE)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

%.no_collapse.o: %.cpp
	$(CXX) $(CXXFLAGS) -DNO_COLLAPSE -c $< -o $@

clean:
	rm -f $(OBJS) $(OBJS_NO_COLLAPSE) $(TARGETS)

