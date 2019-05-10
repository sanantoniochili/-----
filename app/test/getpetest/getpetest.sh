#!/usr/bin/env bash

# test that new function "get_pe_impl" returns same results as "get_PE"
python3 getpetest.py root root TEST1 TEST2 > test_impls.txt                           
