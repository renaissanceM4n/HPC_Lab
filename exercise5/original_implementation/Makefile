# Compiler and flags
CXX = mpic++ 
CXXFLAGS = -O3 -std=c++17 -g
# scorep --instrument-filter=scorep.filt

# Source files
SRCS = main.cpp raytracer.cpp scene.cpp
OBJS = $(SRCS:.cpp=.o)

# Target executable
TARGET = snowman

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

