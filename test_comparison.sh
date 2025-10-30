#!/bin/bash

#============================================================================
# Performance Comparison Test Script
# This script helps compare original vs optimized collector performance
#============================================================================

echo "=========================================================================="
echo "  COLLECTOR PERFORMANCE COMPARISON TEST"
echo "=========================================================================="
echo ""

# Colors for output (if terminal supports it)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "run.sh" ]; then
    echo -e "${RED}Error: run.sh not found. Please run this script from the project root directory.${NC}"
    exit 1
fi

cd app

echo -e "${BLUE}This script will run both collectors and compare their performance.${NC}"
echo ""
echo "Configuration:"
echo "  Customer: PSLAB"
echo "  Mode: Monthly"
echo "  Date: February 5, 2025 (from run.sh)"
echo ""

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found. Using system Python.${NC}"
fi

echo ""
echo "=========================================================================="
echo "  TEST 1: Running ORIGINAL collector (collector.py)"
echo "=========================================================================="
echo ""

# Run original collector
START_TIME_ORIGINAL=$(date +%s)
python3 script_files/collector.py PSLAB monthly 2 5 2025
END_TIME_ORIGINAL=$(date +%s)
DURATION_ORIGINAL=$((END_TIME_ORIGINAL - START_TIME_ORIGINAL))

echo ""
echo -e "${GREEN}Original collector completed in ${DURATION_ORIGINAL} seconds${NC}"
echo ""

# Prompt to continue
echo -e "${YELLOW}Press Enter to continue with optimized collector test...${NC}"
read

echo ""
echo "=========================================================================="
echo "  TEST 2: Running OPTIMIZED collector (collector_optimized.py)"
echo "=========================================================================="
echo ""

# Run optimized collector
START_TIME_OPTIMIZED=$(date +%s)
python3 script_files/collector_optimized.py PSLAB monthly 2 5 2025
END_TIME_OPTIMIZED=$(date +%s)
DURATION_OPTIMIZED=$((END_TIME_OPTIMIZED - START_TIME_OPTIMIZED))

echo ""
echo -e "${GREEN}Optimized collector completed in ${DURATION_OPTIMIZED} seconds${NC}"
echo ""

# Calculate improvement
IMPROVEMENT=$((DURATION_ORIGINAL - DURATION_OPTIMIZED))
IMPROVEMENT_PERCENT=$(echo "scale=2; ($IMPROVEMENT / $DURATION_ORIGINAL) * 100" | bc)

echo ""
echo "=========================================================================="
echo "  PERFORMANCE COMPARISON RESULTS"
echo "=========================================================================="
echo ""
printf "%-30s %10s seconds\n" "Original Collector:" "$DURATION_ORIGINAL"
printf "%-30s %10s seconds\n" "Optimized Collector:" "$DURATION_OPTIMIZED"
echo "--------------------------------------------------------------------------"
printf "%-30s %10s seconds\n" "Time Saved:" "$IMPROVEMENT"
printf "%-30s %10s%%\n" "Performance Improvement:" "$IMPROVEMENT_PERCENT"
echo ""

if [ $IMPROVEMENT -gt 0 ]; then
    echo -e "${GREEN}✓ Optimized version is faster!${NC}"
else
    echo -e "${RED}✗ Optimized version was slower (unexpected)${NC}"
fi

echo ""
echo "=========================================================================="
echo ""
echo "Check the log files in the 'log/' directory for detailed timing information."
echo ""
echo "Log files contain:"
echo "  - Phase-by-phase timing"
echo "  - API call durations"
echo "  - Database write speeds"
echo "  - Memory usage (if debug mode enabled)"
echo ""
echo "=========================================================================="
