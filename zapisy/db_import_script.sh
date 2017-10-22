#!/bin/bash
#remove old db
sudo su - postgres  <<'ENDSUDO'
    psql -c "DROP DATABASE \"fereol\";"
    psql -c "CREATE DATABASE \"fereol\";"
    logout
ENDSUDO

#new db
PGPASSWORD="fereolpass" psql -U fereol -h localhost -f $1 fereol 


