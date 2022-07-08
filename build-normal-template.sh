#!/bin/bash

set -e

scons platform=windows target=release tools=no use_lto=yes module_gltf=yes -j8
