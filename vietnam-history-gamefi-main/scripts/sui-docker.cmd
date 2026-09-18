@echo off
rem Wrapper gọi SUI CLI trong container docker (máy Windows bị Smart App Control chặn sui.exe)
docker exec -i -w /work/blockchain/sui sui-dev sui %*
