#!/bin/sh
# Configurer les locales
sed -i "/${LOCALE}/s/^# //g" /etc/locale.gen && locale-gen
exec "$@"
