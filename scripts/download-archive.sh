#!/usr/bin/env bash

# Retry incomplete transfers to a regular file so curl can discard partial bytes.
exec curl --disable --fail --location --retry 3 --retry-all-errors \
  --connect-timeout 10 --max-time 120 --remove-on-error --output "$2" -- "$1"
