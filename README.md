# EAC3_Converter

# Testing command
docker build -t eac3_converter_test . && timeout 10 docker run --rm -e RUN_IMMEDIATELY=true -v ./test_data:/app/input:rw -v ./cache:/app/cache:rw eac3_converter_test