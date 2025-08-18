#!/bin/bash

BACKUP_DIR="./MySQL_Backup"
TIMESTAMP=$(date +%s)
BACKUP_FILE="$BACKUP_DIR/GRU-PA-MySQL_Backup_$TIMESTAMP.sql"

if [ -d "$BACKUP_DIR" ]; then
    mysqldump --defaults-file=.mysql.cnf gru-pa > "$BACKUP_FILE"

    if [ -f "$BACKUP_FILE" ]; then
        FILE_SIZE=$(stat -c%s "$BACKUP_FILE")
        if [ $FILE_SIZE -gt 0 ]; then
            FILE_SIZE_KB=$(echo "scale=1; $FILE_SIZE / 1024" | bc)
            echo "File: $BACKUP_FILE 备份完成，大小: ${FILE_SIZE_KB} KB"
        else
            echo "File: $BACKUP_FILE 备份文件为空，请检查 mysqldump 执行情况。"
            rm -f "$BACKUP_FILE"
            exit 1
        fi
    else
        echo "File: $BACKUP_FILE 备份失败，请检查路径和权限。"
        exit 1
    fi
else
    echo "$BACKUP_DIR 路径不存在, 请检查设置."
    exit 1
fi