#!/bin/bash
mkdir -p build
cp -r src/* build/
cd build
zip -r ../lambda.zip .