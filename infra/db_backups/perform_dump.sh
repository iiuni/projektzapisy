#!/usr/bin/env bash

set -e

OUTFILE_PATH_DEV="$1"
OUTFILE_PATH_PROD="$2"
TEMP_DUMP_PATH_DEV="/tmp/ii_zapisy_dump_dev.sql"
TEMP_DUMP_PATH_PROD="/tmp/ii_zapisy_dump_prod.sql"
TEMP_DB_NAME="II_ZAPISY_BACKUP_TEMP_DB"

errcho () {
	>&2 echo $@
}

[ -z "$II_ZAPISY_DB_BACKUP_DB_NAME" ] && errcho "Need to set II_ZAPISY_DB_BACKUP_DB_NAME" && exit 1;
[ -z "$II_ZAPISY_DB_BACKUP_DB_USER" ] && errcho "Need to set II_ZAPISY_DB_BACKUP_DB_USER" && exit 1;
[ -z "$II_ZAPISY_DB_BACKUP_DB_PASS" ] && errcho "Need to set II_ZAPISY_DB_BACKUP_DB_PASS" && exit 1;
[ -z "$II_ZAPISY_DB_BACKUP_DB_PORT" ] && errcho "Need to set II_ZAPISY_DB_BACKUP_DB_PORT" && exit 1;
[ -z "$II_ZAPISY_DB_BACKUP_DUMP_PASS" ] && errcho "Need to set II_ZAPISY_DB_BACKUP_DUMP_PASS" && exit 1;

if ! type "7za" &> /dev/null; then
	errcho "p7zip-full is required."
	exit 2
fi


# $1 - DB name
# $2 - filename
dump_db_to_file () {
	PGPASSWORD="$II_ZAPISY_DB_BACKUP_DB_PASS" pg_dump \
	-U "$II_ZAPISY_DB_BACKUP_DB_USER" \
	-h localhost \
	-p "$II_ZAPISY_DB_BACKUP_DB_PORT" \
	"$1" > "$2"
}


setup_temp_db () {
	PGPASSWORD="$II_ZAPISY_DB_BACKUP_DB_PASS" psql \
	-U "$II_ZAPISY_DB_BACKUP_DB_USER" \
	-h localhost \
	-p "$II_ZAPISY_DB_BACKUP_DB_PORT" \
	-c "CREATE DATABASE \"$TEMP_DB_NAME\";"
}

teardown_temp_db () {
	PGPASSWORD="$II_ZAPISY_DB_BACKUP_DB_PASS" psql \
	-U "$II_ZAPISY_DB_BACKUP_DB_USER" \
	-h localhost \
	-p "$II_ZAPISY_DB_BACKUP_DB_PORT" \
	-c "DROP DATABASE IF EXISTS \"$TEMP_DB_NAME\";"
}

run_script_on_temp_db () {
	PGPASSWORD="$II_ZAPISY_DB_BACKUP_DB_PASS" psql \
	-U "$II_ZAPISY_DB_BACKUP_DB_USER" \
	-h localhost \
	-p "$II_ZAPISY_DB_BACKUP_DB_PORT" \
	-f "$1" \
	"$TEMP_DB_NAME"
}

# First make the production dump, we won't be changing that
dump_db_to_file "$II_ZAPISY_DB_BACKUP_DB_NAME" "$TEMP_DUMP_PATH_PROD"

# Run the anonymizing script on the dev DB
teardown_temp_db # Make sure any old DB is nuked
setup_temp_db
# First load it into the newly created DB...
run_script_on_temp_db "$TEMP_DUMP_PATH_PROD"
# Then anonymize
run_script_on_temp_db anonymize.sql
# Finally dump
dump_db_to_file "$TEMP_DB_NAME" "$TEMP_DUMP_PATH_DEV"
# Get rid of the temp db
teardown_temp_db


# Compress to outfiles

# $1 - archive name
# $2 - pass
# $3... - filenames
compress_with_7z () {
	if [ -z "$2" ]; then
		7za a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on "$1" "${@:3}"
	else
		7za a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -ms=on -p"$2" "$1" "${@:3}"
	fi
}
compress_with_7z "$OUTFILE_PATH_DEV" "" "$TEMP_DUMP_PATH_DEV"
compress_with_7z "$OUTFILE_PATH_PROD" "$II_ZAPISY_DB_BACKUP_DUMP_PASS" "$TEMP_DUMP_PATH_PROD"

# Remove tempfiles
rm "$TEMP_DUMP_PATH_DEV"
rm "$TEMP_DUMP_PATH_PROD"
