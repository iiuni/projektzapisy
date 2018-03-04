We need this file so we can specify it as the (only) input in tsconfig.json.
Otherwise tsc will attempt to compile _ALL_ .ts files in the directory,
regardless of whether they're specified as an entry (or imported by something that is)
in webpack config.