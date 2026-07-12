# https://just.systems/man/en/

# REQUIRES
find := require("find")
rm := require("rm")
uv := require("uv")

# SETTINGS
set dotenv-load := true

# VARIABLES
SOURCES := "apps libs"
TESTS := "tests"

# DEFAULTS
default:
    @just --list

# IMPORTS
import 'tasks/check.just'
import 'tasks/clean.just'
import 'tasks/commit.just'
import 'tasks/format.just'
import 'tasks/install.just'
import 'tasks/db.just'
