#!/bin/bash

set -e

source ~/scoop/apps/emscripten/current/emsdk_env.sh

scons platform=javascript target=release tools=no -j8

