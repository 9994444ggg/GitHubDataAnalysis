from bs4 import BeautifulSoup
import requests
from itertools import chain, combinations
from github import Github
import pandas as pd
import sys
if r"C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib" not in sys.path:
    sys.path.append(r'C:\Users\pmedappa\Dropbox\Code\CustomLib\PooLib')
    print(sys.path)
from poo_ghmodules import gettoken

def xl_input():
	df = pd.read_excel(r'C:\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\2021 Update\CleanConsolidatedSponsors_SOMatchOnly_Sub0121_nomatch_3.xlsx', encoding='ISO-8859-1')
	users = df.login
	return users

def all_subsets(fname):
	if len(fname) > 1:
		all_subsets = list(chain(*map(lambda x: combinations(fname, x), range(2, len(fname) + 1)))) 
	else:
		all_subsets = list(chain(*map(lambda x: combinations(fname, x), range(1, len(fname) + 1))))
	all_subsets = [' '.join(subset) for subset in all_subsets]
	all_subsets = all_subsets[::-1]
	return all_subsets

def full_name(client, user):
	full_name = client.get_user(user).name
	return full_name

def github_username(client, user):
	github_username = client.get_user(user).login.strip()
	return github_username

def github_url(client, user):
	github_url = client.get_user(user).html_url.strip()
	return github_url

def company_url(client, user):
	company_url = client.get_user(user).company
	if company_url:
		company_url = company_url.replace('@', 'https://github.com/').strip()
		return company_url

def stack_id(profile_link):
	stack_id = profile_link.split('/')
	stack_id = stack_id[2].strip()
	return stack_id

def search_sid(subsets, gurl, company):
	for subset in subsets:
		print(subset)
		url =  'https://stackoverflow.com/users?tab=Reputation&filter=all&search=' + subset
		response = requests.get(url)
		soup = BeautifulSoup(response.text, 'lxml')
		profile_links = soup.select('div.user-details a')
		profile_links = [profile_link['href'] for profile_link in profile_links if profile_link.text.lower() == subset.lower()]
		for profile_link in profile_links:
			stack_id = profile_link.split('/')
			if stack_id[1] == 'users':
				return [stack_id[2],'https://stackoverflow.com'+ profile_link]
#			url = 'https://stackoverflow.com' + profile_link
#			response = requests.get(url)
#			soup = BeautifulSoup(response.text, 'lxml')
#			links = soup.select('a.url')
#			print("***************",links)            
#			if links:
#				links = [link['href'] for link in links]
#				print(profile_link, ":::", links)
#				for link in links:
#					if link == gurl or link == company:
#						sid = stack_id(profile_link)
#						return sid

def main():
	print('Start')
	users = xl_input()
	users = users[:]
	all_ids = []
	all_urls = []
	for user in users:
		try:
			TOKEN = gettoken(r"C:\Users\pmedappa\Dropbox\Code\PW\GHtoken.txt")
			client = Github(TOKEN)
			fname = full_name(client, user)
			# guname = github_username(client, user)
			# gurl = github_url(client, user)
			github_url = 'https://github.com/' + user
			company = company_url(client, user)
			if fname:
				fname = fname.strip().split(' ')
				subsets = all_subsets(fname)
			else:
				subsets = []
			subsets.insert(0, user)
			stack_id = search_sid(subsets, github_url, company)
			all_ids.append(stack_id[0])
			all_urls.append(stack_id[1])
			print(stack_id)            
		except:
			all_ids.append(None)
			all_urls.append(None)            
			print(user, 'FAIL')

	d = zip(users, all_ids,all_urls)
	df = pd.DataFrame(data=d)
	df.to_excel(r'C:\Users\pmedappa\Dropbox\Course and Research Sharing\Research\Data\Sponsor\2021 Update\CleanConsolidatedSponsors_SOMatchOnly_Sub0121_nomatch_3_ret.xlsx', encoding='utf-8-sig', index=False, header=['github username','stack ID', 'stack url'])

if __name__ == '__main__':
	main()