[rprichard] 2017-04-08

I copied these files from https://github.com/signal11/hidapi, commit
a6a622ffb680c55da0de787ff93b80280498330f.  I had trouble getting libhidapi.dylib
working on OS X -- Homebrew had the latest release (0.8.0-rc1), but that's dated
2013, and it didn't work.  (The IOKit IOService path-related change might have
been the issue.)  I tried building from master, but I couldn't get the
autotools-based build system to work.  So instead, I copied the two C files and
came up with a compile command-line by hand, which was much easier.
