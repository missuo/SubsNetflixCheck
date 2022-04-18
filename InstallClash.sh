#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
#================================================================
#	System Required: macOS/Linux
#	Description: Subs Netflix Unlock Check
#	Version: 0.1
#	Author: Vincent Young
# 	Telegram: https://t.me/missuo
#	Github: https://github.com/missuo/SubsNetflixCheck
#	Latest Update: April 19, 2022
#=================================================================

# Define Color
red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
plain='\033[0m'

# Make sure run with root
[[ $EUID -ne 0 ]] && echo -e "[${red}Errot${plain}]Please run this script with ROOT!" && exit 1

read -p "Please enter your system: (macos/linux)" system
	[ -z "${system}" ]

if [[ ${system} = "macos" ]]; then
    systemname="darwin"
else
    systemname="linux"
fi

last_version=$(curl -Ls "https://api.github.com/repos/Dreamacro/clash/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
if [[ ! -n "$last_version" ]]; then
    echo -e "${red}Failure to detect mtg version may be due to exceeding Github API limitations, please try again later."
    exit 1
fi
echo -e "Latest version of Clash detected: ${last_version}, start installing..."

wget -N --no-check-certificate -O clash-${systemname}-amd64-v3-${last_version}.gz https://github.com/Dreamacro/clash/releases/download/${last_version}/clash-${systemname}-amd64-v3-${last_version}.gz
if [[ $? -ne 0 ]]; then
    echo -e "${red}Download failed, please check your network or try again later."
    exit 1
fi
echo -e "Download complete, start installing..."
gzip -d clash-${systemname}-amd64-v3-${last_version}.gz

if [[ ${systemname} = "darwin" ]]; then
    mv clash-${systemname}-amd64-v3-${last_version} /usr/local/bin/clash
else
    mv clash-${systemname}-amd64-v3-${last_version} /usr/bin/clash
fi