#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @Author  : Vincent Young
# @Time    : 2022/04/19 12:00
# @GitHub  : github.com/missuo

import requests
import socks
import socket
import yaml
import subprocess
import time
import os
import psutil
import sys
import json

subscriptionURL = input("Enter Your Subscription URL: ")

def fetchSubsription(subscriptionURL):
	print("Starting fetch subscription...")
	transformURL = "https://sub.missuo.me/sub?target=clash&url={}&insert=false&config=https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online.ini&emoji=false&list=true&tfo=false&scv=false&fdn=false&sort=false&new_name=true".format(subscriptionURL)
	try:
		nodeListYaml = requests.get(transformURL).text
		nodeListDict = yaml.safe_load(nodeListYaml)
		nodeList = nodeListDict["proxies"]
	except Exception as e:
		print("Subscription URL is Incorrect!")
		sys.exit()
	return nodeList, nodeListDict

def runClash():
	os.system('pkill -f "clash"')
	# Fetch Subs Info
	nodeList, nodeListDict = fetchSubsription(subscriptionURL)
	
	# Fetch Blank Config File
	clashConfigFile = open("./config.yaml", 'r')
	clashConfigDict = yaml.safe_load(clashConfigFile)
	clashConfigDict["proxies"] = nodeListDict["proxies"]
	clashConfigFile.close()
	
	# Write new Config File
	newClashConfigFile = open("./newConfig.yaml", 'w', encoding="utf-8")
	yaml.safe_dump(clashConfigDict, newClashConfigFile, default_flow_style=False, allow_unicode=True)
	newClashConfigFile.close()
	
	nodeNum = len(nodeList)
	currentNode = 0
	
	checkResult = []
	

	# Loop
	for node in nodeList:
		nodeResult = {}
		currentNode = currentNode + 1
		print("Checking Node [{}/{}]".format(currentNode, nodeNum))
		nodeName = node["name"]
		currentClashFile = open("./newConfig.yaml", 'r')
		currentClashConfigDict = yaml.safe_load(currentClashFile)
		currentClashFile.close()
		
		currentClashFile = open("./newConfig.yaml", 'w')
		currentClashConfigDict["proxy-groups"][0]["proxies"][0] = nodeName
		yaml.safe_dump(currentClashConfigDict, currentClashFile, default_flow_style=False, allow_unicode=True)
		currentClashFile.close()
		
		clashLog = open("./clashLog", 'a+')
		
		clashRuner = subprocess.Popen("clash -f newConfig.yaml", shell=True, stdout = clashLog,  preexec_fn = os.setsid)
		time.sleep(2)
		startProxy()
		IPAddress = getIPInfo()
		if(IPAddress == ""):
			print("Name:", nodeName)
			print("\nNode Time Out! Pass...")
			print("---------------------------\n")
			time.sleep(3)
			kill(clashRuner.pid)
			continue
		nfRetCode, nfStatus, country = nfCheck()
		nodeResult["name"] = nodeName
		nodeResult["ip"] = IPAddress.replace("\n", "")
		if(nfRetCode ==200):
			unlock = "yes"
		else:
			unlock = "no"
		nodeResult["unlock"] = unlock
		nodeResult["country"] = country
		checkResult.append(nodeResult)
		print("Name:", nodeName)
		print("IP:", IPAddress)
		print(nfStatus)
		if(country != ""):
			print("Netflix Unlock Country: ", country)
		print("---------------------------\n")
		time.sleep(3)
		kill(clashRuner.pid)
	resultFileName = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + ".json"
	resultFile = open(resultFileName, 'w')
	resultJSON = json.dumps(checkResult, indent=4, ensure_ascii=False)
	resultFile.write(resultJSON)
	# yaml.safe_dump(checkResult, resultFile, default_flow_style=False, allow_unicode=True)
	resultFile.close()
	print("Check Result is saved into ./{}".format(resultFileName))
	print("Thanks for using SubsCheck :)")

	
def kill(proc_pid):
	process = psutil.Process(proc_pid)
	for proc in process.children(recursive=True):
		proc.kill()
	process.kill()

def getIPInfo():
	IPRet = ""
	try: 
		IPRet = requests.post(url = "http://api-ipv4.ip.sb/geoip").text
		return IPRet
	except Exception as e:
		IPRet = ""
		return IPRet
	
def nfCheck():
	# Define headers
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}
	
	# Test Availability
	FLIMURL = "https://www.netflix.com/title/81215567"
	nfRet = requests.get(url = FLIMURL, headers = headers, allow_redirects = True)
	nfRetCode = nfRet.status_code
	
	# Fetch Country
	AREAURL = "https://www.netflix.com/title/80018499"
	areaRet = requests.get(url = AREAURL, headers = headers, allow_redirects = True)
	areaHeaders = areaRet.headers
	
	# Define null country
	country = ""
	if(nfRetCode == 403 or nfRetCode == 404):
		nfStatus = "Not Support Netflix"
	elif(nfRetCode == 200):
		urlCountry = areaHeaders["X-Originating-URL"]
		country = urlCountry.split("/")[3].split("-")[0].upper()
		if(country == "TITLE"):
			country = "US"
		nfStatus = "Fully Support Netflix"
	else:
		nfStatus = "Unknown"
	return nfRetCode, nfStatus, country
	
	
def startProxy():
	socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1204)
	socket.socket = socks.socksocket

runClash()
