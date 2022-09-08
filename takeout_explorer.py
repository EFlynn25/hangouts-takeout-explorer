import sys
import json
import curses
import math
from datetime import datetime

if len(sys.argv) == 1:
	print("Need directory arg")
	sys.exit(0)

users = {}

# Helper functions

def header(conv):
	return conv["conversation"]["conversation"]

def body(conv):
	e = conv["events"]

	sections = math.ceil(len(e) / 1000)
	new_e = []
	for i in range(sections):
		start = (sections - i - 1) * 1000
		end = start + 1000
		new_e = new_e + e[start:end]

	return new_e

def user_name(chat_id):
	return users[chat_id][0:5].ljust(5) if chat_id in users else chat_id[-5:]

def chat_type(conv):
	real_type = header(conv)["type"]
	if real_type == "STICKY_ONE_TO_ONE":
		return "dm"
	elif real_type == "GROUP":
		return "group"

def chat_name(conv):
	if chat_type(conv) == "dm":
		my_header = header(conv)
		second_person = my_header["participant_data"][1]
		if "fallback_name" in second_person:
			users[second_person["id"]["chat_id"]] = second_person["fallback_name"]
			return second_person["fallback_name"]
		return my_header["id"]["id"]
	elif chat_type(conv) == "group":
		my_header = header(conv)
		for participant in my_header["participant_data"]:
			if "fallback_name" in participant:
				users[participant["id"]["chat_id"]] = participant["fallback_name"]
		if "name" in my_header:
			return my_header["name"]
		return my_header["id"]["id"]

def chat_message(conv, i, my_body=None):
	message = None
	try:
		if my_body == None:
			message = body(conv)[i]
		else:
			message = my_body[i]
	except:
		return None
	
	prefix = user_name(message["sender_id"]["chat_id"])
	if "chat_message" not in message:
		if message["event_type"] == "RENAME_CONVERSATION":
			return "*" + prefix + " renamed chat to " + str(message["conversation_rename"]["new_name"])
		elif message["event_type"] == "ADD_USER":
			added_users = message["membership_change"]["participant_id"]
			latter_msg = user_name(added_users[0]["chat_id"])
			for i in range(len(added_users) - 1):
				latter_msg += ", " + user_name(added_users[i + 1]["chat_id"])
			return "*" + prefix + " added " + latter_msg
		elif message["event_type"] == "REMOVE_USER":
			removed = message["membership_change"]["participant_id"][0]["chat_id"]
			if message["sender_id"]["chat_id"] == removed:
				return "*" + prefix + " left"
			else:
				return "*" + prefix + " removed " + user_name(removed)
		elif message["event_type"] == "HANGOUT_EVENT":
			return "*" + prefix + " started a Hangout "
		return "&" + message["event_type"]
		return list(message.keys())[3:] # This is kept for testing other event types

	content = message["chat_message"]["message_content"]
	if "segment" in content:
		if content["segment"][0]["type"] == "TEXT":
			return prefix + ": " + content["segment"][0]["text"]
		elif content["segment"][0]["type"] == "LINK":
			return prefix + ": " + content["segment"][0]["text"]
	elif "attachment" in content:
		return prefix + " <img>: " + content["attachment"][0]["embed_item"]["plus_photo"]["url"]
		
	return content

# File open

f = open(sys.argv[1] + "/Hangouts/Hangouts.json", "r")

Hangouts = json.load(f)
conversations = Hangouts["conversations"]

match = None
name_indexes = []
name_matches = []
term = sys.argv[2] if len(sys.argv) > 2 else ""
if term.isnumeric():
	match = conversations[int(term)]
	name_matches.append(chat_name(match))
else:
	i = 0
	for conv in conversations:
		name = chat_name(conv)
		if term in name:
			match = conv
			name_matches.append(name)
			name_indexes.append(i)
		i += 1

if len(name_matches) != 1:
	for i in range(len(name_matches)):
		print(str(name_indexes[i]) + ": " + name_matches[i])
	sys.exit(0)

print(name_matches[0])
search = None
if len(sys.argv) > 3:
	search = " ".join(sys.argv[3:])

def main(stdscr):
	rows, cols = stdscr.getmaxyx()
	curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
	
	my_body = body(match)
	max_page = math.floor((len(my_body) - 1) / (rows - 2))
	page = max_page
	while True:
		stdscr.clear()
		end = (page + 1) * (rows - 2)
		start = end - rows + 2

		if start < 0:
			start = 0
			end = start + rows - 2
		
		stdscr.addstr(0, 0, "{0} (page {1}/{2}) (range {3}-{4}) {5}".format(name_matches[0], page + 1, max_page + 1, start, end - 1, datetime.utcfromtimestamp(int(my_body[start]["timestamp"]) / 1000000).strftime("%b %-d, %Y • %-I:%M %p")))
		for i in range(start, end):
			message = chat_message(match, i, my_body)
			msg_color = 0
			if not isinstance(message, str):
				if message == None:
					message = ""
				else:
					message = str(message)
				msg_color = 1
			elif message[0] == "*":
				message = message[1:]
				msg_color = 1
			elif message[0] == "&":
				message = message[1:]
				msg_color = 2
			
			if search != None and search in message:
				curses.endwin()
				print(message)
				print("Page #{0}".format(page + 1))
				print("Message #{0}".format(i))
				sys.exit(0)
				
			try:
				stdscr.addstr(i - start + 1, 0, message, curses.color_pair(msg_color))
			except curses.error:
				pass
			stdscr.clrtoeol()
		
		stdscr.addstr(rows - 1, 0, "Go to page: ")
		stdscr.clrtoeol()
		stdscr.refresh()

		quit = False
		if search != None:
			if page > 0:
				page -= 1
			else:
				quit = True
		else:
			my_page = ""
			while True:
				c = stdscr.getch()
				if c == curses.KEY_LEFT:
					if page > 0:
						page -= 1
					break
				elif c == curses.KEY_RIGHT:
					if page < max_page:
						page += 1
					break
				elif c == ord("q"):
					quit = True
					break
				elif chr(c).isnumeric():
					my_page += str(chr(c))
					stdscr.addstr(rows - 1, 12, my_page)
					stdscr.clrtoeol()
					stdscr.refresh()
				elif c == 127:
					my_page = my_page[:-1]
					stdscr.addstr(rows - 1, 12, my_page)
					stdscr.clrtoeol()
					stdscr.refresh()
				elif c == 10:
					if len(my_page) == 0:
						continue
					page = int(my_page) - 1
					if page < 0:
						page = 0
					elif page > max_page:
						page = max_page
					break

		if quit:
			break

curses.wrapper(main)

f.close()