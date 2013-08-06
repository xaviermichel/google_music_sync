#!-*-coding:utf-8-*-

#
# https://github.com/simon-weber/Unofficial-Google-Music-API
# push music in PUSH_DIR and, after, pull music in PULL_DIR
#

from gmusicapi import Musicmanager
import os
import marshal

ROOT='/home/xavier/musiques/'

DICT_FILE= ROOT + '.gmusic.bdd'
PULL_DIR = ROOT + '{artist}/{album}/'
PUSH_DIR = '/home/xavier/musique_to_upload/'

def pull() :
	i = 0
	all_songs = mm.get_all_songs()
	for track in all_songs :
		i+=1
		print 'Track ' + str(i) + ' / ' + str(len(all_songs)),

		# si on a déjà l'ID dans le dico, c'est que l'on a déjà la chanson
		if track['id'] in id_list.keys() :
			print ' is already downloaded'
			continue

		print ' is downloading...'

		# build file path
		target_path=unicode(PULL_DIR, 'utf-8')
		for element in [e for e in track if '{' + e + '}' in target_path] :
			target_path = target_path.replace('{' + element + '}', track[element])

		target_path = target_path.replace(u'É', u'é')
		target_path = ''.join(e for e in target_path if e.isalnum() or e in u'/ .,;-_éèêàâùïîçùûô')

		#print type(target_path), target_path
		if not os.path.exists(target_path.lower()) :
			os.makedirs(target_path.lower())

		filename, audio = mm.download_song(track['id'])
		with open(target_path.lower() + filename, 'wb') as f:
			f.write(audio)

		id_list[track['id']] = target_path.lower() + filename
		marshal.dump(id_list, open(DICT_FILE, 'wb'))


def push() :
	for musique in [f for f in os.listdir(PUSH_DIR) if f.endswith('.mp3')] :
		print musique,
		uploaded, matched, not_uploaded = mm.upload(PUSH_DIR + musique, transcode_quality="320k", enable_matching=True)

		upload_ok = True # on est optimiste, on part du principe que tout va bien :)
		if uploaded:
			print " has been uploaded"
		elif matched:
			print " has been found in google library"
		else:
			if "ALREADY_EXISTS" or "this song is already uploaded" in not_uploaded[file_path]:
				print " aleady exists"
			else:
				print " upload failed !"
				upload_ok = False
		# remove uploaded file
		if upload_ok :
			os.remove(PUSH_DIR + musique)


# init
id_list={}
try : id_list = marshal.load(open(DICT_FILE, "rb"))
except : pass

mm = Musicmanager()
if not mm.login() :
	mm.perform_oauth()
	mm.login()

# main
pull()
print "==========="
push()

# finish
mm.logout()
marshal.dump(id_list, open(DICT_FILE, 'wb'))


