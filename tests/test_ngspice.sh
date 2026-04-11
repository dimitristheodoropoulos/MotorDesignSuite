#!/bin/bash
# Simple Ngspice test

echo "=== Running Ngspice test ==="

if ! command -v ngspice &> /dev/null
then
    echo "Ngspice not found. Install it first."
    exit 1
fi

# Create a temporary test circuit
CIRCUIT_FILE=$(mktemp /tmp/test_circuitXXXX.cir)
cat <<EOL > $CIRCUIT_FILE
* Simple RC circuit
V1 in 0 DC 5
R1 in out 1k
C1 out 0 1u
.tran 1ms 10ms
.end
EOL

ngspice -b $CIRCUIT_FILE

rm $CIRCUIT_FILE
echo "Ngspice test completed successfully."
